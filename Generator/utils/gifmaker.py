import os
import imageio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
GIF_FRAME_DURATION = int(config.get("Settings", "gif_frame_duration", fallback="5000"))

directory = "DataVisuals"
directory = os.path.join(os.getcwd(), directory)
os.makedirs(directory, exist_ok=True)

frame_order = config.get("GifOrder", "frame_order")
frame_order = eval(frame_order)

image_paths = {os.path.basename(f): os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".png")}
ordered_image_paths = [image_paths[f] for f in frame_order if f in image_paths]


def blend_images(img1, img2, alpha):
    return Image.blend(img1, img2, alpha)


def add_timer(image, time_left):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=40)
    position = (common_size[0] - 60, 10)
    text = f"{time_left}s"
    draw.text(position, text, font=font, fill="white")
    return image


common_size = (1200, 800)
duration_per_frame = GIF_FRAME_DURATION
fade_duration = 1000
fade_steps = int(fade_duration / 100)

bg_color = (34, 39, 46)

images = [Image.open(img_path).convert("RGB") for img_path in ordered_image_paths]
resized_images = [img.resize(common_size, Image.LANCZOS) for img in images]
background_image = Image.new("RGB", common_size, bg_color)

all_frames = []

for i in range(len(resized_images)):
    current_image = resized_images[i]
    next_image = resized_images[(i + 1) % len(resized_images)]

    for second in range(duration_per_frame // 1000, 0, -1):
        frame = add_timer(current_image.copy(), second)
        all_frames.extend([np.array(frame)] * 10)

    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(current_image, background_image, alpha)
        all_frames.append(np.array(blended_image))

    for step in range(1, fade_steps + 1):
        alpha = step / fade_steps
        blended_image = blend_images(background_image, next_image, alpha)
        all_frames.append(np.array(blended_image))

output_gif = os.path.join(directory, "data.gif")
imageio.mimsave(output_gif, all_frames, duration=100, loop=0)

print(f"Animated GIF created: {output_gif}")
