import os
import imageio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import configparser

# Load configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")
GIF_FRAME_DURATION = int(config.get("Settings", "gif_frame_duration", fallback="5000"))

# Set up the directory for storing the visuals
directory_name: str = "DataVisuals"
directory_path: str = os.path.join(os.getcwd(), directory_name)
os.makedirs(directory, exist_ok=True)

# Load the frame order for the GIF from the configuration file
frame_order: list[str, ...] = config.get("GifOrder", "frame_order")
frame_order = eval(frame_order)

# Map image filenames to their full paths
image_paths: dict[str:str, ...] = {
    os.path.basename(f): os.path.join(directory_path, f)
    for f in os.listdir(directory_path)
    if f.endswith(".png")
}
# Order the image paths according to the specified frame order
ordered_image_paths: list[str, ...] = [
    image_paths[f] for f in frame_order if f in image_paths
]


def blend_images(img1: Image, img2: Image, alpha: float) -> Image:
    """
    Blend two images together using a specified alpha for transparency.

    Args:
    - img1 (Image): The first image.
    - img2 (Image): The second image.
    - alpha (float): The blend factor where 0.0 is fully img1 and 1.0 is fully img2.

    Returns:
    - Image: The blended image.
    """
    return Image.blend(img1, img2, alpha)


def add_timer(image: Image, time_left: int) -> Image:
    """
    Add a countdown timer to an image.

    Args:
    - image (Image): The image to which the timer will be added.
    - time_left (int): The time left to display on the timer, in seconds.

    Returns:
    - Image: The image with the timer added.
    """
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=40)
    position: tuple[int, int] = (common_size[0] - 60, 10)
    text: str = f"{time_left}s"
    draw.text(position, text, font=font, fill="white")
    return image


# Define the common size for all images in the GIF
common_size: tuple[int, int] = (1200, 800)
duration_per_frame: int = GIF_FRAME_DURATION
fade_duration: int = 1000  # Duration of fade effect in milliseconds
fade_steps: int = int(fade_duration / 100)  # Number of steps in the fade effect

bg_color: tuple[int, int, int] = (34, 39, 46)  # Background color

# Load, resize, and prepare the images
images: list[Image, ...] = [
    Image.open(img_path).convert("RGB") for img_path in ordered_image_paths
]
resized_images: list[Image, ...] = [
    img.resize(common_size, Image.LANCZOS) for img in images
]
background_image: Image = Image.new(
    "RGB", common_size, bg_color
)  # Create a background image

all_frames: list[Image | None] = []  # List to hold all the frames for the GIF

# Loop through each image to create the frames for the GIF
for i in range(len(resized_images)):
    current_image: Image = resized_images[i]
    next_image: Image = resized_images[(i + 1) % len(resized_images)]

    # Add the countdown timer frames
    for second in range(duration_per_frame // 1000, 0, -1):
        frame = add_timer(current_image.copy(), second)
        all_frames.extend([np.array(frame)] * 10)

    # Create a fade-out effect to the background
    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(current_image, background_image, alpha)
        all_frames.append(np.array(blended_image))

    # Create a fade-in effect from the background to the next image
    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(background_image, next_image, alpha)
        all_frames.append(np.array(blended_image))

# Save the generated frames as an animated GIF
output_gif = os.path.join(directory, "data.gif")
imageio.mimsave(output_gif, all_frames, duration=100, loop=0)

print(f"Animated GIF created: {output_gif}")
