import streamlit as st
import base64
from PIL import Image
from utils import stability
import streamlit as st
from PIL import Image
import io
import logging
from typing import Union
from utils import config
from stability_sdk.api import GenerationRequest, GenerationResponse, TextPrompt, InitImageMode, GuidancePreset, Sampler, MaskSource


# Page configuration
st.set_page_config(page_title="Generate Images - Stability.AI", page_icon="🎨")
config.get_background()

# Define API base URL
API_BASE_URL = "https://api.stability.ai"

# Initialize the assistant object using session state
if "st_assistant" not in st.session_state:
    st.session_state.st_assistant = None
if "st_images" not in st.session_state:
    st.session_state.st_images = None
if "st_request" not in st.session_state:
    st.session_state.st_request = None
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

endpointName ='sdxl-jumpstart-1-2023-08-30-23-25-11-865'

# List of engine types
engine_types = ["engine1", "engine2", "engine3", "engine4", "engine5", "engine6"]

# List of generation types
generation_types = ["Text to Image", "Image to Image", "Masking"]
# Create tabs
prompts, params = st.sidebar.tabs(["Prompts", "Parameters"])


#selected_engine = st.sidebar.selectbox("Select Engine", engine_types)
selected_engine = "stable-diffusion-xl-1024-v1-0"

# List of valid dimensions for height and width
valid_dimensions = [
    "1024x1024", "1152x896", "1216x832", "1344x768", 
    "1536x640", "640x1536", "768x1344", "832x1216", "896x1152"
]
styles_preset_values = [ "NONE",
    "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art",
    "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound",
    "neon-punk", "origami", "photographic", "pixel-art", "tile-texture",
]

sampler_list = ["NONE"] + [sampler.value for sampler in Sampler]

guidance_list = [mode.value for mode in GuidancePreset]

default_params = {
     "Prompts": [
                {
                    "Text Prompt": "",
                    "Weight": 1.0
                }
            ],
    "Generation Parameters": {
            "Height": 1024,
            "Width": 1024,
            "Sampler": "NONE",
            "Samples": 1,
            "Steps": 50,
            "Cfg Scale": 7,
            "Clip Guidance Preset": "NONE",
            "Style Preset": "NONE",
            "Seed": 555
        }
}

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

def resize_to_nearest_multiple_of_64(image_path):
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Calculate the new height as the nearest multiple of 64
        new_height = ((img.height - 1) // 64 + 1) * 64

        # Resize the image to the new height while preserving the aspect ratio
        img = img.resize((img.width, new_height), Image.LANCZOS)

        # Save the resized image or return it
        resized_image_path = f"resized_{new_height}_{image_path}"
        img.save(resized_image_path)
        return resized_image_path
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def encode_image(image_data: None, resize: bool = True) -> Union[str, None]:
    """
    Encode an image as a base64 string, optionally resizing it to 512x512.

    Args:
        image_path (str): The path to the image file.
        resize (bool, optional): Whether to resize the image. Defaults to True.

    Returns:
        Union[str, None]: The encoded image as a string, or None if encoding failed.
    """

    if resize:
        image = Image.open(image_data)
        # Get the original width and height
        original_width, original_height = image.size
        #image = image.resize((512, 512))
        # Calculate the new width and height that are multiples of 64
        new_width = original_width - (original_width % 64)
        new_height = original_height - (original_height % 64)

         # Calculate the new pixel count
        new_pixel_count = new_width * new_height

        # Check if the new pixel count exceeds the maximum allowed
        if new_pixel_count > 1048576:
            # Reduce the width and height while maintaining the aspect ratio
            aspect_ratio = original_width / original_height
            new_height = int((1048576 / aspect_ratio) ** 0.5)
            new_width = int(aspect_ratio * new_height)

            # Ensure the new width and height are multiples of 64
            new_width = new_width - (new_width % 64)
            new_height = new_height - (new_height % 64)

        # Resize the image to the new height while preserving the aspect ratio
        image = image.resize((new_width, new_height), Image.LANCZOS)
       
        image_resized_path = f"image_base_resized.png"
        image.save(image_resized_path)
        image_path = image_resized_path
        # Create a thumbnail without specifying a fixed size to maintain aspect ratio
        image.thumbnail((new_width // 4, new_height // 4), Image.LANCZOS)
        #thumbnail = image.resize((image.width,128), Image.LANCZOS)
    #image = Image.open(image_path)
    st.image(image)
    #assert image.size == (512, 512)
    with open(image_path, "rb") as image_file:
        img_byte_array = image_file.read()
        # Encode the byte array as a Base64 string
        try:
            base64_str = base64.b64encode(img_byte_array).decode("utf-8")
            return base64_str
        except Exception as e:
            print(f"Failed to encode image {image_path} as base64 string.")
            print(e)
            return None


def load_sidebar():
    # Load generation parameters based on selected type

    # Streamlit app layout
    st.title("Generate Campaign Images")
    subheader = '### Text Prompts'
    def_sampler = 0
    def_guidance = 0
    def_preset = 0
    def_dimensions = 0

    # Sidebar controls
    params.title("Generate Images")
    selected_generation_type = params.selectbox("Select Generation Type", generation_types, key="generation_type" )

    request = GenerationRequest()
    if st.session_state.generation_type == "Text to Image":
        # Find the selected prompt and its details
        selected_prompt = None
        values = default_params

        prompts.title("Select Campaign")
        campaign_type = prompts.selectbox("Select Campaign", campaigns, key="campaign")
        if campaign_type and campaign_type != "NONE":
            prompt_titles = [item["Prompt Title"] for item in prompts_data[campaign_type]]
            selected_prompt_title = prompts.selectbox("Select Prompt", prompt_titles, key="prompt_title")

            if selected_prompt_title:
                for prompt in prompts_data[campaign_type]:
                    if prompt["Prompt Title"] == selected_prompt_title:
                        selected_prompt = prompt
                        st.session_state.selected_prompt = selected_prompt
                        values = selected_prompt
                        if values["Generation Parameters"].get("Clip Guidance Preset"):
                            def_guidance = guidance_list.index(values["Generation Parameters"]["Clip Guidance Preset"])
                        
                        if values["Generation Parameters"].get("Style Preset"):
                            def_preset = styles_preset_values.index(values["Generation Parameters"]["Style Preset"])

                        if values["Generation Parameters"].get("Sampler"):
                            def_sampler = sampler_list.index(values["Generation Parameters"]["Sampler"])
                        
                        if values["Generation Parameters"].get("Height") and values["Generation Parameters"].get("Width"):
                            def_dimensions = valid_dimensions.index(f'{values["Generation Parameters"].get("Height")}x{values["Generation Parameters"].get("Width")}')

                        campaign_html = f'### <span style="color: #00FFFF;"> {campaign_type}: {selected_prompt_title}</span>'
                        subheader = campaign_html
                        break

        request.seed = params.slider("Seed", min_value=0, max_value=4294967295, value=values["Generation Parameters"]["Seed"], step=1, key="seed")
        request.sampler= params.selectbox("Sampler",sampler_list, index=def_sampler, key="sampler")
        request.samples= params.slider("Samples", min_value=1, max_value=10, value=values["Generation Parameters"]["Samples"], key="samples")
        request.steps= params.slider("Steps", min_value=10, max_value=150, value=values["Generation Parameters"]["Steps"], key="steps")
        request.cfg_scale = params.slider("Config Scale", min_value=1, max_value=10, value=values["Generation Parameters"]["Cfg Scale"], key="cfg_scale")
        request.clip_guidance_preset= params.selectbox("Clip Guidance Preset", guidance_list , index=def_guidance, key="clip_guidance_preset")
        selected_dimension = params.selectbox("Select Dimension", valid_dimensions, index=def_dimensions, key="selected_dimension")
        request.style_preset= params.selectbox("Style Preset", styles_preset_values, index=def_preset, key="style_preset")

        request.text_prompts= []  # Placeholder for text prompts
        request.height,request.width = map(int, selected_dimension.split("x"))

        if request.sampler == 'NONE':
            request.sampler = None



        # Collect text prompts and weights in the main page area
        st.markdown(subheader, unsafe_allow_html = True)
        #print(f'Values: {len(values["Prompts"])}')
        num_prompts = st.number_input("Number of Prompts", min_value=1, value=len(values["Prompts"]))
        text_area_value = ''
        for i in range(num_prompts):
        #for i, prompt in enumerate(values["Prompts"], start=1):
            col1, col2 = st.columns([4, 1])
            default_text = ''
            default_weight = 1.0
            if i < len(values["Prompts"]):
                default_text = values["Prompts"][i][f"Text Prompt"]
                default_weight = values["Prompts"][i][f"Weight"]
            with col1:
                text_prompt = st.text_area(f"Text Prompt {i+1}", max_chars=2000, value=default_text, height=10)
            with col2:
                weight = st.number_input(f"Weight", value=default_weight, step=0.1,  key=f"weight_{i}")
            request.text_prompts.append(TextPrompt(text= text_prompt, weight = weight))
            text_area_value = f'{text_area_value}{default_text}:{default_weight}\n'
        negative_prompts = st.text_input(f"Negative prompts, Weight: -1", max_chars=2000, value="ugly, tiling, poorly drawn hands, out of frame, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low quality, bad art, beginner, windy, amateur, distorted")
        request.text_prompts.append(TextPrompt(text=negative_prompts,weight=-1))
        #st.text_area(label=f"Each prompt in new line in format. Default weight is 1.0",value=text_area_value, height=5)


    elif st.session_state.generation_type == "Image to Image":
        with params:
            request.samples= params.slider("Samples", min_value=1, max_value=10, value=1)
            request.seed= params.number_input("Seed", min_value=0, max_value=4294967295, value=0)
            request.style_preset= params.selectbox("Style Preset", styles_preset_values, index=0)
            request.text_prompts= []  # Placeholder for text prompts

            request.init_image_mode = params.selectbox("Init Image Mode", [mode.value for mode in InitImageMode] ,index=0)
            
            if request.init_image_mode== InitImageMode.STEP_SCHEDULE:
                request.step_schedule_start = params.slider("Step Schedule Start", min_value=0.0, max_value=1.0, value=0.65, step=0.01)
                request.step_schedule_end = params.slider("Step Schedule End", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
            else:
                request.image_strength = params.slider("Image Strength", min_value=0.0, max_value=1.0, value=0.35, step=0.01)
            
            request.cfg_scale = params.slider("Cfg Scale", min_value=1, max_value=10, value=7)
            request.clip_guidance_preset = params.selectbox("Clip Guidance Preset", [mode.value for mode in GuidancePreset], index=0)
            request.sampler = params.selectbox("Sampler", ["NONE"] + [sampler.value for sampler in Sampler], index=0)
            request.steps = params.slider("Steps", min_value=10, max_value=150, value=50)

            
        if request.sampler == 'NONE':
            request.sampler = None
        
        if request.style_preset == 'NONE':
            request.style_preset = None
        
        init_image = st.file_uploader("Upload Initial Image", type=["jpg", "jpeg", "png"])
        if init_image is not None:
            request.init_image = encode_image(init_image)

        # Collect text prompts and weights in the main page area
        # Collect text prompts and weights in the main page area
        st.markdown(subheader, unsafe_allow_html = True)
        num_prompts = st.number_input("Number of Prompts", min_value=1, value=1)
        for i in range(num_prompts):
            col1, col2 = st.columns([4, 1])
            with col1:
                text_prompt = st.text_area(f"Text Prompt {i + 1}", max_chars=2000, height=10)
            with col2:
                weight = st.number_input(f"Weight", value=1.0, step=0.1,  key=f"weight_{i}")
            request.text_prompts.append(TextPrompt(text= text_prompt, weight = weight))
            
        negative_prompts = st.text_input(f"Negative prompts, Weight: -1", max_chars=2000, value="ugly, tiling, poorly drawn hands, out of frame, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low quality, bad art, beginner, windy, amateur, distorted")
        request.text_prompts.append(TextPrompt(text=negative_prompts,weight=-1))
    
    elif st.session_state.generation_type == "Masking":
        with params:
            request.samples= params.slider("Samples", min_value=1, max_value=10, value=1)
            request.seed= params.number_input("Seed", min_value=0, max_value=4294967295, value=1200003866)
            request.style_preset= params.selectbox("Style Preset", styles_preset_values, index=0)
            request.text_prompts= []  # Placeholder for text prompts

            request.mask_source = params.selectbox("Mask Source", [mode.value for mode in MaskSource] ,index=0)
            
            if request.mask_source== MaskSource.MASK_IMAGE_BLACK or request.mask_source == MaskSource.MASK_IMAGE_WHITE:
                mask_image = params.file_uploader("Upload Mask Image", type=["jpg", "jpeg", "png"])
                if mask_image is not None:
                    request.mask_image = encode_image(mask_image)
            
            
            request.cfg_scale = params.slider("Cfg Scale", min_value=1, max_value=10, value=7)
            request.clip_guidance_preset = params.selectbox("Clip Guidance Preset", [mode.value for mode in GuidancePreset], index=0)
            request.sampler = params.selectbox("Sampler", ["NONE"] + [sampler.value for sampler in Sampler], index=0)
            request.steps = params.slider("Steps", min_value=10, max_value=150, value=50)

            
        if request.sampler == 'NONE':
            request.sampler = None
        
        if request.style_preset == 'NONE':
            request.style_preset = None
        
        init_image = st.file_uploader("Upload Initial Image", type=["jpg", "jpeg", "png"])
        if init_image is not None:
            request.init_image = encode_image(init_image)

        # Collect text prompts and weights in the main page area
        # Collect text prompts and weights in the main page area
        st.markdown(subheader, unsafe_allow_html = True)
        num_prompts = st.number_input("Number of Prompts", min_value=1, value=1)
        for i in range(num_prompts):
            col1, col2 = st.columns([4, 1])
            with col1:
                text_prompt = st.text_area(f"Text Prompt {i + 1}", max_chars=2000, height=10)
            with col2:
                weight = st.number_input(f"Weight", value=1.0, step=0.1,  key=f"weight_{i}")
            request.text_prompts.append(TextPrompt(text= text_prompt, weight = weight))
            
        negative_prompts = st.text_input(f"Negative prompts, Weight: -1", max_chars=2000, value="ugly, tiling, poorly drawn hands, out of frame, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low quality, bad art, beginner, windy, amateur, distorted")
        request.text_prompts.append(TextPrompt(text=negative_prompts,weight=-1))
    
    st.session_state.st_request = request

def getAgent():
    assistant = stability.StabilityAssistant(endpointName)
    return assistant

def generateImages(st_assistant, generation_params):
    return st_assistant.generate(generation_params)



def main():

    load_sidebar()
    
    if st.session_state.st_assistant is None:
        st.session_state.st_assistant = getAgent()
        

    # Generate button
    if st.button("Generate"):
        with st.spinner("Generating Images..."):
            # API call to generate images
            #response = requests.post(API_BASE_URL + "/generate", json=generation_params)

            generated_images = generateImages(st.session_state.st_assistant, st.session_state.st_request)
        
            # # Display generated images
            # if response.status_code == 200:
            #     generated_images = response.json()["images"]
            if generated_images is not None:
                st.session_state.st_images = []
                for idx, artifact in enumerate(generated_images, start=1):
                    st.write(f"Generated Image {idx}:")
                    image = artifact.base64
                    image_data = base64.b64decode(image.encode())
                    image = Image.open(io.BytesIO(image_data))
                    #pil_image = Image.open(image_bytes)
                    st.session_state.st_images.append({"image": image, "seed": artifact.seed})
                    #st.image(image, caption=f'Seed: {artifact.seed}', use_column_width=True)
            else:
                st.error("An error occurred while generating images.")

    if st.session_state.st_images is not None:
        for img in st.session_state.st_images:
            st.image(img["image"], caption=f'Seed: {img["seed"]}', use_column_width=True)


@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
        #load_sidebar()
    main()
        