"""Contains the stack with the resources for this app."""

import os
import urllib.parse

import aws_cdk.aws_certificatemanager as acm
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecr_assets as ecr_assets
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_elasticloadbalancingv2_actions as elb_actions
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as targets
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_logs as logs
from aws_cdk import aws_iam as iam
from aws_cdk import core

import configuration as configuration

class GenAiRetailStack(core.Stack):
    """
    Provisions a Cognito User Pool with a custom domain as well as
    a VPC with an ALB in front of an ECS service based on Fargate.
    """

    config: configuration.Config

    user_pool: cognito.UserPool
    user_pool_custom_domain: cognito.UserPoolDomain
    user_pool_client: cognito.UserPoolClient

    user_pool_full_domain: str
    user_pool_logout_url: str
    user_pool_user_info_url: str
    app_name: str

    def __init__(self, scope: core.Construct, id: str,
                 config: configuration.Config,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.config = config
        self.app_name = self.config.app_name

        self.os_key_path = self.node.try_get_context("os_key_path") or "/opensearch/"
        self.bedrock_key_path = self.node.try_get_context("bedrock_key_path") or "/bedrock/"
        
        self.add_cognito()

        self.add_streamlit_app()

    def add_cognito(self):
        """
        Sets up the cognito infrastructure with the user pool, custom domain
        and app client for use by the ALB.
        """
        # Create the user pool that holds our users
        self.user_pool = cognito.UserPool(
            self,
            f"{self.app_name}-user-pool",
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(mutable=True, required=True)
            )
        )

        # Add a custom domain for the hosted UI
        self.user_pool_custom_domain = self.user_pool.add_domain(
            f"{self.app_name}-user-pool-domain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=self.config.cognito_custom_domain
            )
        )

        # Create an app client that the ALB can use for authentication
        self.user_pool_client = self.user_pool.add_client(
            f"{self.app_name}-app-client",
            user_pool_client_name="AlbAuthentication",
            generate_secret=True,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_srp=True,
                user_password=True
            ),
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    # This is the endpoint where the ALB accepts the
                    # response from Cognito
                    f"https://{self.config.application_dns_name}/oauth2/idpresponse",

                    # This is here to allow a redirect to the login page
                    # after the logout has been completed
                    f"https://{self.config.application_dns_name}"
                ],
                logout_urls= [f"https://{self.config.application_dns_name}"],
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PHONE
                ]
            ),
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.COGNITO
            ]
        )

        # Logout URLs and redirect URIs can't be set in CDK constructs natively ...yet
        user_pool_client_cf: cognito.CfnUserPoolClient = self.user_pool_client.node.default_child
        user_pool_client_cf.logout_ur_ls = [
            # This is here to allow a redirect to the login page
            # after the logout has been completed
            f"https://{self.config.application_dns_name}"
        ]

        self.user_pool_full_domain = self.user_pool_custom_domain.base_url()
        redirect_uri = urllib.parse.quote('https://' + self.config.application_dns_name)
        self.user_pool_logout_url = f"{self.user_pool_full_domain}/logout?" \
                                    + f"client_id={self.user_pool_client.user_pool_client_id}&" \
                                    + f"logout_uri={redirect_uri}"

        self.user_pool_user_info_url = f"{self.user_pool_full_domain}/oauth2/userInfo"

    def add_streamlit_app(self):
        """
        Adds the ALB, ECS-Service and Cognito Login Action on the ALB.
        """

        vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id = "vpc-08d59b9dca7fd2248", # existing vpc
            is_default=False
        )
        
        # Create the ecs cluster to house our service, this also creates a VPC in 2 AZs
        cluster = ecs.Cluster(
            self,
            f"{self.app_name}-cluster",
            vpc=vpc
        )

        # Load the hosted zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "hosted-zone",
            hosted_zone_id=self.config.hosted_zone_id,
            zone_name=self.config.hosted_zone_name
        )

        # Create a Certificate for the ALB
        certificate = acm.Certificate(
            self,
            f"{self.app_name}-certificate",
            domain_name=self.config.application_dns_name,
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        # Execution Role
        execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                iam.ServicePrincipal("bedrock.amazonaws.com"),
                iam.ServicePrincipal("personalize.amazonaws.com")
            )
        )
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"))
        execution_role.add_to_policy(iam.PolicyStatement(actions=["bedrock:*"], resources=["*"]))
        execution_role.add_to_policy(iam.PolicyStatement(actions=["personalize:*"], resources=["*"]))
        execution_role.add_to_policy(iam.PolicyStatement(
            actions=["ssm:GetParameters"],
            resources=[
                f"arn:aws:ssm:{self.region}:{self.account}:parameter{self.os_key_path}*",
                f"arn:aws:ssm:{self.region}:{self.account}:parameter{self.bedrock_key_path}*"
            ]
        ))

        # Task Role
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                iam.ServicePrincipal("bedrock.amazonaws.com"),
                iam.ServicePrincipal("personalize.amazonaws.com")

            )
        )
        task_role.add_to_policy(iam.PolicyStatement(actions=["ssm:DescribeParameters"], resources=["*"]))
        task_role.add_to_policy(iam.PolicyStatement(actions=["sagemaker:InvokeEndpoint"], resources=["*"]))
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{self.os_key_path}*",
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{self.bedrock_key_path}*"
                ]
            )
        )
        task_role.add_to_policy(iam.PolicyStatement(actions=["bedrock:*"], resources=["*"]))
        task_role.add_to_policy(iam.PolicyStatement(actions=["personalize:*"], resources=["*"]))


        # Define the Docker Image for our container (the CDK will do the build and push for us!)
        path = os.path.join(os.path.dirname(__file__), "..")
        print(path)
        docker_image = ecr_assets.DockerImageAsset(
            self,
            f"{self.app_name}",
            directory=path
        )

        # ECS Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDefinition",
            cpu=512,
            memory_limit_mib=1024,
            execution_role=execution_role,
            task_role=task_role
        )

        container = task_definition.add_container(
            "genai-retail-streamlit-container",
            image=ecs.ContainerImage.from_docker_image_asset(docker_image),
            essential=True,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="ecs/genai-retail-fargate",
                log_retention=logs.RetentionDays.TWO_WEEKS
            ),
            secrets= {
                "OS_ENDPOINT": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self, 
                        "OsEndpoint",
                        parameter_name=f"{self.os_key_path}endpoint",
                        version=1
                    )
                ),
                "OS_USERNAME": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self, 
                        "OsUsername",
                        parameter_name=f"{self.os_key_path}username",
                        version=1
                    )
                ),
                "OS_PASSWORD": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self, 
                        "OsPassword",
                        parameter_name=f"{self.os_key_path}password",
                        version=1
                    )
                ),
                "BR_ENDPOINT": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self, 
                        "BrEndpoint",
                        parameter_name=f"{self.bedrock_key_path}endpoint",
                        version=1
                    )
                ),
                "BR_REGION": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self, 
                        "BrRegion",
                        parameter_name=f"{self.bedrock_key_path}region",
                        version=1
                    )
                )
            }            
        )
        
        container.add_port_mappings(
            ecs.PortMapping(container_port=8501)
        )        

        # Security Groups
        load_balancer_security_group = ec2.SecurityGroup(
            self,
            "LoadBalancerSecurityGroup",
            vpc=vpc,
            description="Security group for the load balancer"
        )

        load_balancer_security_group.add_ingress_rule(
            ec2.Peer.ipv4("0.0.0.0/0"),
            ec2.Port.tcp(80),
            "Allow inbound traffic on port 80"
        )

        ecs_security_group = ec2.SecurityGroup(
            self,
            "EcsSecurityGroup",
            vpc=vpc,
            description="Security group for the ECS service"
        )
        ecs_security_group.add_ingress_rule(
            load_balancer_security_group,
            ec2.Port.tcp(8501),
            "Allow inbound traffic from the load balancer on port 8501"
        )

        # ECS Service
        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            desired_count=1,
            task_definition=task_definition,
            security_group=load_balancer_security_group,
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.public_subnets)
        )

        # Setup AutoScaling policy
        scaling = service.auto_scale_task_count(
            max_capacity=4
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=80,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

        # Elastic Load Balancer
        target_group = elb.ApplicationTargetGroup(
            self,
            "TargetGroup",
            port=80,
            targets=[service],
            vpc=vpc,
            target_type=elb.TargetType.IP
        )

        load_balancer = elb.ApplicationLoadBalancer(
            self,
            "LoadBalancer",
            vpc=vpc,
            internet_facing=True,
            security_group=load_balancer_security_group
        )

        load_balancer.add_listener(
            "Listener", 
            port=80,
            default_action=elb.ListenerAction.forward([target_group])
        )

        https_listener = load_balancer.add_listener(
            "HttpsSListener", 
            port=443,
            default_action=elb.ListenerAction.forward([target_group]),
            certificates=[certificate]
        )

        https_listener.add_action(
            "authenticate-rule",
            priority=1000,
            action=elb_actions.AuthenticateCognitoAction(
                next=elb.ListenerAction.forward(
                    target_groups=[
                        target_group
                    ]
                ),
                user_pool=self.user_pool,
                user_pool_client=self.user_pool_client,
                user_pool_domain=self.user_pool_custom_domain
            ),
            host_header=self.config.application_dns_name
        )

        route53.ARecord(
            self, 
            "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(load_balancer)),
            record_name=self.config.application_dns_name
        )
