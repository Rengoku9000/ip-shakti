from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r"c:\Projects\drugvista\presentation\assets\new_slide_assets"
os.makedirs(out_dir, exist_ok=True)

# Generate Vector Engine Database Icon for Slide 4 Image 2
def make_vector_engine_icon():
    w, h = 400, 230
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # 3 stacked database cylinders in modern emerald and info blue
    cylinders = [
        (130, (37, 99, 166), (180, 215, 245)),
        (80, (18, 107, 69), (180, 235, 205)),
        (30, (11, 79, 52), (200, 245, 220))
    ]
    for y_top, col, top_col in cylinders:
        # body
        d.rectangle([100, y_top + 20, 300, y_top + 60], fill=col)
        # bottom ellipse
        d.ellipse([100, y_top + 40, 300, y_top + 80], fill=col)
        # top ellipse
        d.ellipse([100, y_top, 300, y_top + 40], fill=top_col, outline=col, width=3)

    # Add a glowing AI node badge in the center
    d.ellipse([175, 80, 225, 130], fill=(255, 255, 255), outline=(18, 107, 69), width=3)
    f_bold = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 22)
    d.text((200, 105), "AI", fill=(11, 79, 52), font=f_bold, anchor="mm")

    out_p = os.path.join(out_dir, "vector_engine_icon.png")
    im.save(out_p)
    print("Saved vector engine icon to", out_p)

if __name__ == "__main__":
    make_vector_engine_icon()
