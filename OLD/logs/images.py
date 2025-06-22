from PIL import Image, ImageDraw, ImageFont
import os
import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('(\d+)', s)]

def images_to_pdf_with_filenames(image_folder, output_pdf):
    images = []
    font = ImageFont.load_default()

    filenames = [f for f in os.listdir(image_folder)
                 if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))]
    filenames.sort(key=natural_sort_key)

    for filename in filenames:
        image_path = os.path.join(image_folder, filename)
        img = Image.open(image_path).convert("RGB")

        # Add filename text at the top
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), filename, font=font, fill="black")

        images.append(img)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        print(f"PDF created: {output_pdf}")
    else:
        print("No images found.")

# Example usage
images_to_pdf_with_filenames("/home/ariadna/Documentos/TFG/bin/logs_2", "output.pdf")
