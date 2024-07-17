import os
import imageio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")
GIF_FRAME_DURATION = int(config.get("Settings", "gif_frame_duration", fallback="5000"))

common_size = (1200, 800)


def blend_images(img1, img2, alpha):
    return Image.blend(img1, img2, alpha)


def add_timer(image, time_left):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=30)

    # Position for the timer text
    position = (common_size[0] - 60, 10)
    text = f"{time_left}s"

    # Add text to the image
    draw.text(position, text, font=font, fill="white")
    return image


# Directory path to fetch PNG images from
directory = "DataVisuals"
directory = os.path.join(os.getcwd(), directory)

# Create directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Get all PNG files from the directory
image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".png")]

# Duration each image should be shown in milliseconds
duration_per_frame = GIF_FRAME_DURATION
fade_duration = 1000  # Duration for fade effect in milliseconds
fade_steps = int(fade_duration / 100)  # Number of steps for the fade effect

# Background color
bg_color = (34, 39, 46)  # RGB color for #22272E

# Load images using Pillow (PIL) and ensure they are in RGB mode and the same size
images = [Image.open(img_path).convert("RGB") for img_path in image_paths]

# Resize images to the common size
resized_images = [img.resize(common_size, Image.LANCZOS) for img in images]

# Create a background image with the specified color
background_image = Image.new("RGB", common_size, bg_color)

# Initialize list to hold all frames (including fade in/out frames)
all_frames = []

# Generate frames with fade out/in effect
for i in range(len(resized_images)):
    current_image = resized_images[i]
    next_image = resized_images[(i + 1) % len(resized_images)]

    # Add current image for the main duration with a timer
    for second in range(duration_per_frame // 1000, 0, -1):
        frame = add_timer(current_image.copy(), second)
        all_frames.extend([np.array(frame)] * 10)  # 10 frames per second

    # Generate fade out frames to background
    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(current_image, background_image, alpha)
        all_frames.append(np.array(blended_image))

    # Generate fade in frames from background to next image
    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(background_image, next_image, alpha)
        all_frames.append(np.array(blended_image))

# Output GIF file path
output_gif = os.path.join(directory, "data.gif")

# Save GIF using imageio
imageio.mimsave(output_gif, all_frames, duration=100, loop=0)

print(f"Animated GIF created: {output_gif}")
