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
