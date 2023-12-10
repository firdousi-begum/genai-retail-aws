# Campaign and prompt data (same as in the previous response)
campaigns = ["NONE","Grocery Campaign", "Product Ideation"]
prompts_data = {
    "Product Ideation": [
         {
            "Prompt Title": "Men's leather jacket in black",
            "Prompts": [
                {
                    "Text Prompt": "Generate a high-resolution image of a classic men's leather jacket in black. It should showcase fine stitching details and a sleek, modern design.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPM_2",
                "Samples": 1,
                "Steps": 50,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            },
            
        },

         {
            "Prompt Title": "Luxurious SUV interior",
            "Prompts": [
                {
                    "Text Prompt": "Create an image of a luxurious SUV interior with premium leather seats, a state-of-the-art infotainment system, and panoramic sunroof.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPM_2",
                "Samples": 1,
                "Steps": 50,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            },
            
        },

        
         {
            "Prompt Title": "Compact Urban Autonomous Vehicle",
            "Prompts": [
                {
                    "Text Prompt": "Generate a concept image of a compact autonomous vehicle designed for urban commuting, featuring smart sensors and a spacious interior.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Height": 768,
                "Width": 1344,
                "Sampler": "K_DPM_2",
                "Samples": 1,
                "Steps": 50,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            },
            
        },

        
         {
            "Prompt Title": "Efficient urban delivery truck",
            "Prompts": [
                {
                    "Text Prompt": "Create an image of an efficient urban delivery truck optimized for city logistics, featuring an ergonomic driver cabin and eco-friendly technology.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPM_2",
                "Samples": 1,
                "Steps": 50,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            },
            
        },


    ],
    "Grocery Campaign": [
        {
            "Prompt Title": "Promotion of Fresh Berries",
            "Prompts": [
                {
                    "Text Prompt": "A vibrant display of freshly picked Scandinavian berries, including strawberries, blueberries, and raspberries, arranged in a rustic wooden crate.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPM_2",
                "Samples": 1,
                "Steps": 70,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Scandinavian Seafood Feast",
            "Prompts": [
                {
                    "Text Prompt": "A seafood banquet showcasing Norwegian salmon, Swedish shrimp, and Finnish herring, presented on a seaside picnic table with lemon wedges and fresh dill.",
                    "Weight": 1.0
                },
                {
                    "Text Prompt": "Oceanfront, al fresco dining, summery, well-lit, delicious, traditional, Scandinavian.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Height": 768,
                "Width": 1344,
                "Sampler": "K_DPM_2_ANCESTRAL",
                "Samples": 1,
                "Steps": 60,
                "Cfg Scale": 6,
                "Clip Guidance Preset": "FAST_GREEN",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Scandinavian BBQ Feast",
            "Prompts": [
                {
                    "Text Prompt": "Scandinavian style grilled meats and fresh vegetables for a sizzling BBQ feast.",
                    "Weight": 1.0
                },
                {
                    "Text Prompt": "Smoky, savory, grilled, barbecue, al fresco dining.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Height": 768,
                "Width": 1344,
                "Sampler": "K_EULER",
                "Samples": 1,
                "Steps": 50,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Icy Cool Scandinavian Treats",
            "Prompts": [
                {
                    "Text Prompt": "A delightful display of Scandinavian ice creams (mjukglas) and frozen treats, perfect for cooling down on a hot summer day.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPM_2_ANCESTRAL",
                "Samples": 1,
                "Steps": 20,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Nordic Picnic Delights",
            "Prompts": [
                {
                    "Text Prompt": "A picnic scene in a lush Scandinavian forest with a spread of open sandwiches (smørrebrød), creamy cheeses, crisp cucumbers, and local jams.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_EULER",
                "Samples": 1,
                "Steps": 75,
                "Cfg Scale": 6,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Refreshing Berry Smoothies",
            "Prompts": [
                {
                    "Text Prompt": "A tabletop filled with glass jars of refreshing berry smoothies made from Nordic wild berries, garnished with mint leaves and ice cubes.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "K_DPMPP_2M",
                "Samples": 1,
                "Steps": 70,
                "Cfg Scale": 5,
                "Clip Guidance Preset": "FAST_GREEN",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
            "Prompt Title": "Savoring Scandinavian Cuisine",
            "Prompts": [
                {
                    "Text Prompt": "A cozy kitchen scene with a chef preparing a traditional Scandinavian dish, surrounded by fresh local ingredients like salmon, potatoes, and dill.",
                    "Weight": 1.0
                }
            ],
            "Generation Parameters": {
                "Sampler": "DDPM",
                "Samples": 1,
                "Steps": 65,
                "Cfg Scale": 6,
                "Clip Guidance Preset": "FAST_BLUE",
                "Style Preset": "NONE",
                "Seed": 555
            }
        },
        {
        "Prompt Title": "Harvest Abundance",
        "Prompts": [
            {
                "Text Prompt": "A bountiful display of autumn's bounty, featuring pumpkins, apples, colorful leaves, and rustic gourds set on a weathered wooden table.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Sampler": "K_DPMPP_2M",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 6,
            "Clip Guidance Preset": "FAST_BLUE",
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Scandinavian Fall Feast",
        "Prompts": [
            {
                "Text Prompt": "A sumptuous Scandinavian feast with roasted meats, root vegetables, and traditional fall dishes.",
                "Weight": 1.0
            },
            {
                "Text Prompt": "Farm-fresh produce and warm recipes for cozy fall meals.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Height": 896,
            "Width": 1152,
            "Sampler": "DDIM",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 6,
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Fall Baking Delights",
        "Prompts": [
            {
                "Text Prompt": "A delightful display of Scandinavian fall baking, featuring apple pies, swedish cinnamon rolls (Kanelbullar), and hot chocolate.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Height": 1152,
            "Width": 896,
            "Sampler": "K_LMS",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 6,
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Scandinavian Apple Harvest",
        "Prompts": [
            {
                "Text Prompt": "An abundant display of crisp Scandinavian apples, freshly harvested from the orchard, ready for delicious autumn pies.",
                "Weight": 1.0
            },
            {
                "Text Prompt": "Fresh, harvest, apples, pies, seasonal.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Height": 1024,
            "Width": 1024,
            "Sampler": "DDIM",
            "Samples": 1,
            "Cfg Scale": 6,
            "Steps": 50,
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Autumn Tea Time",
        "Prompts": [
            {
                "Text Prompt": "A close-up of a steaming cup of aromatic cinnamon-spiced tea with a slice of apple pie, enjoyed by the fireplace in a cozy cabin.",
                "Weight": 1.0
            },
            {
                "Text Prompt": "Comforting, fireside, aromatic, indulgent, relaxation.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Sampler": "K_DPMPP_2M",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 6,
            "Clip Guidance Preset": "FAST_BLUE",
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Elegant Christmas Dinner",
        "Prompts": [
            {
                "Text Prompt": "An elegant dining featuring  Swedish Christmas feast (Julbord), crystal glasses",
                "Weight": 1.0
            },
            {
                "Text Prompt": "Formal, opulent, culinary delight, festive elegance, celebratory.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Sampler": "K_DPMPP_2M",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 6,
            "Clip Guidance Preset": "FAST_BLUE",
            "Seed": 555
        }
    },
    {
        "Prompt Title": "Scandinavian Gingerbread Delights",
        "Prompts": [
            {
                "Text Prompt": "An assortment of beautifully decorated gingerbread cookies, a beloved Scandinavian Christmas tradition.",
                "Weight": 1.0
            },
            {
                "Text Prompt": "Gingerbread, sweet, decorated, holiday treats, baking.",
                "Weight": 1.0
            }
        ],
        "Generation Parameters": {
            "Height": 896,
            "Width": 1152,
            "Sampler": "K_EULER_ANCESTRAL",
            "Samples": 1,
            "Cfg Scale": 6,
            "Steps": 50,
            "Seed": 555
        }
    },
        # Add more prompts for the "Grocery Summer" campaign here...
    ],
    # Add data for other campaigns...
}
prompts_data_idea = {
    "Retail": [
         {
            "Prompt Title": "Men's leather jacket in black",
            "Prompt": "Generate a high-resolution image of a classic men's leather jacket in black. It should showcase fine stitching details and a sleek, modern design."
        },
         {
            "Prompt Title": "Designer handbag",
            "Prompt": "Generate an image of a designer handbag in rich, earthy tones, highlighting the quality craftsmanship and timeless design."
        },
         {
            "Prompt Title": "Women's high-heeled shoes",
            "Prompt": "Create an image of a stylish pair of women's high-heeled shoes in vibrant red. Emphasize the details of the shoe's design."
        },
         {
            "Prompt Title": "Wide brim Summer Hat",
            "Prompt": "Generate an image of a summer hat with a wide brim. Showcase the hat's texture and style in a simple, elegant composition."
        },
         {
            "Prompt Title": "Elegant low-top sneakers",
            "Prompt": "Imagine crafting a cutting-edge design for low-top sneakers that captures the essence of urban fashion and street culture. These sneakers should reflect the energy and style of modern city life. Incorporate bold patterns, elegant brown color, and innovative materials to create a standout look. The design should resonate with trendsetters and those seeking a dynamic and fashion-forward footwear choice."
        },
    ],
    "Transport": [
         {
            "Prompt Title": "Luxurious SUV interior",
            "Prompt": "Create an image of a luxurious SUV interior with premium leather seats, a state-of-the-art infotainment system, and panoramic sunroof."
        },
        {
             "Prompt Title": "Compact Urban Autonomous Vehicle",
            "Prompt": "Generate a concept image of a compact autonomous vehicle designed for urban commuting, featuring smart sensors and a spacious interior."
        },
        {
             "Prompt Title": "Efficient urban delivery truck",
            "Prompt": "Create an image of an efficient urban delivery truck optimized for city logistics, featuring an ergonomic driver cabin and eco-friendly technology."
        }, 
        {
            "Prompt Title": "Truck in a Cityscape (USA)",
            "Prompt": "Design an image of a powerful, midnight-black truck navigating the bustling streets of a dynamic American city during rush hour. Showcase its urban appeal, agility, and efficiency as it seamlessly merges with city life."
        },
         {
            "Prompt Title": "Truck in a Winter Wonderland (Sweden)",
            "Prompt": "Design an image of a powerful, midnight-black truck navigating snow-covered roads in Sweden. Illuminate the truck's safety features, advanced technology, and reliability during harsh winter conditions."
        },
    ],
    "Financial Services": [
         {
            "Prompt Title": "QuantumSafe CryptoVault",
            "Prompt": "Cutting-edge financial product, the QuantumSafe CryptoVault. Showcase its revolutionary quantum-resistant encryption technology, ensuring the highest level of security for digital assets. Emphasize the product's role in safeguarding cryptocurrencies and sensitive financial information against emerging threats. Capture the essence of innovation, security, and the future of financial protection."
        },
    ],
}
adapter_data = {
    "Retail": [
         {
            "Prompt Title": "Women's Shirt Dress Midi",
            "Image_Source": "data/images/dress_shirt.jpg",
            "Prompt": "White silk shirt dress, with black stitch, realistic, 4k photo, highly detailed. It should showcase fine stitching details and a sleek, modern design."
        },
    ],
}

industry =[
    "Retail",
    "Financial Services",
    "Transport"
]

description_prompt = {
    "Retail": [
        {
            "Product Name": "Sunglasses",
            "Features": '''- Polarized lenses for enhanced clarity
- Stylish and lightweight design
- UV protection for eye safety
- Adjustable nose pads for a comfortable fit
- Comes with a protective case and cleaning cloth'''
    }
    ],
    "Financial Services": [
        {
            "Product Name": "WealthBuilder Credit Card",
            "Features": '''- Cashback Rewards: Earn cashback on every purchase, putting money back into your pocket with every transaction.
- Financial Planning Tools: Access exclusive financial planning tools to help you achieve your short and long-term financial goals.
- Travel Benefits: Enjoy complimentary travel insurance, airport lounge access, and special discounts on travel bookings.
- Security and Control: Benefit from advanced security features, including real-time transaction alerts and the ability to freeze/unfreeze your card instantly.
- Contactless Payments: Experience the convenience of contactless payments for a faster and more secure checkout process.
            '''
        }
    ]
}
