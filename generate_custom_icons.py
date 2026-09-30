import os
from PIL import Image, ImageDraw, ImageFont

out_dir = r"c:\Projects\drugvista\extracted_assets\custom_icons"
os.makedirs(out_dir, exist_ok=True)

def draw_circle_bg(draw, size, bg_color):
    draw.ellipse([4, 4, size-4, size-4], fill=bg_color)

def create_leaf_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(230, 246, 238), outline=(19, 117, 71), width=4)
    # Draw leaf shape
    d.polygon([(60, 24), (88, 52), (76, 92), (60, 98), (44, 92), (32, 52)], fill=(19, 117, 71))
    d.line([(60, 30), (60, 92)], fill=(255, 255, 255), width=3)
    d.line([(60, 50), (74, 42)], fill=(255, 255, 255), width=2)
    d.line([(60, 65), (74, 58)], fill=(255, 255, 255), width=2)
    d.line([(60, 50), (46, 42)], fill=(255, 255, 255), width=2)
    d.line([(60, 65), (46, 58)], fill=(255, 255, 255), width=2)
    img.save(os.path.join(out_dir, "icon_leaf.png"))

def create_scales_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(237, 242, 247), outline=(27, 54, 93), width=4)
    # central pillar
    d.line([(60, 26), (60, 94)], fill=(27, 54, 93), width=4)
    d.line([(40, 94), (80, 94)], fill=(27, 54, 93), width=5)
    # beam
    d.line([(28, 42), (92, 42)], fill=(27, 54, 93), width=4)
    # left scale
    d.line([(32, 42), (22, 64)], fill=(27, 54, 93), width=2)
    d.line([(32, 42), (42, 64)], fill=(27, 54, 93), width=2)
    d.arc([18, 56, 46, 72], 0, 180, fill=(27, 54, 93), width=3)
    # right scale
    d.line([(88, 42), (78, 64)], fill=(27, 54, 93), width=2)
    d.line([(88, 42), (98, 64)], fill=(27, 54, 93), width=2)
    d.arc([74, 56, 102, 72], 0, 180, fill=(27, 54, 93), width=3)
    img.save(os.path.join(out_dir, "icon_scales.png"))

def create_shield_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(254, 243, 235), outline=(217, 119, 6), width=4)
    # shield
    d.polygon([(60, 26), (90, 36), (84, 76), (60, 94), (36, 76), (30, 36)], fill=(217, 119, 6))
    # inner checkmark
    d.line([(48, 60), (56, 68), (74, 48)], fill=(255, 255, 255), width=4)
    img.save(os.path.join(out_dir, "icon_shield.png"))

def create_database_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(240, 244, 255), outline=(37, 99, 235), width=4)
    # database cylinders
    for y in [34, 52, 70]:
        d.ellipse([34, y, 86, y+18], fill=(37, 99, 235), outline=(30, 64, 175), width=2)
    img.save(os.path.join(out_dir, "icon_database.png"))

def create_ai_brain_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(245, 243, 255), outline=(124, 58, 237), width=4)
    # nodes
    pts = [(60, 32), (38, 50), (82, 50), (44, 78), (76, 78), (60, 62)]
    # lines
    d.line([(60, 32), (38, 50)], fill=(124, 58, 237), width=2)
    d.line([(60, 32), (82, 50)], fill=(124, 58, 237), width=2)
    d.line([(38, 50), (60, 62)], fill=(124, 58, 237), width=2)
    d.line([(82, 50), (60, 62)], fill=(124, 58, 237), width=2)
    d.line([(38, 50), (44, 78)], fill=(124, 58, 237), width=2)
    d.line([(82, 50), (76, 78)], fill=(124, 58, 237), width=2)
    d.line([(44, 78), (60, 62)], fill=(124, 58, 237), width=2)
    d.line([(76, 78), (60, 62)], fill=(124, 58, 237), width=2)
    for p in pts:
        d.ellipse([p[0]-6, p[1]-6, p[0]+6, p[1]+6], fill=(124, 58, 237), outline=(255, 255, 255), width=2)
    img.save(os.path.join(out_dir, "icon_ai_brain.png"))

def create_multilingual_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(236, 253, 245), outline=(5, 150, 105), width=4)
    # Draw letters 'A' and 'अ'
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\Nirmala.ttc", 36)
        d.text((30, 38), "A", fill=(5, 150, 105), font=font)
        d.text((64, 40), "अ", fill=(5, 150, 105), font=font)
    except:
        d.text((32, 42), "A", fill=(5, 150, 105))
        d.text((68, 42), "अ", fill=(5, 150, 105))
    d.line([(58, 36), (58, 84)], fill=(16, 185, 129), width=2)
    img.save(os.path.join(out_dir, "icon_multilingual.png"))

def create_cpu_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(241, 245, 249), outline=(51, 65, 85), width=4)
    # CPU square
    d.rectangle([34, 34, 86, 86], fill=(51, 65, 85), outline=(15, 23, 42), width=2)
    d.rectangle([44, 44, 76, 76], fill=(71, 85, 105))
    # pins
    for i in [42, 54, 66, 78]:
        d.line([(i, 24), (i, 34)], fill=(15, 23, 42), width=2)
        d.line([(i, 86), (i, 96)], fill=(15, 23, 42), width=2)
        d.line([(24, i), (34, i)], fill=(15, 23, 42), width=2)
        d.line([(86, i), (96, i)], fill=(15, 23, 42), width=2)
    img.save(os.path.join(out_dir, "icon_cpu.png"))

def create_check_audit_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(236, 253, 243), outline=(16, 185, 129), width=4)
    d.line([(34, 60), (52, 78), (86, 44)], fill=(16, 185, 129), width=7)
    img.save(os.path.join(out_dir, "icon_check_audit.png"))

def create_book_statute_icon():
    img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, 114, 114], fill=(255, 247, 237), outline=(194, 65, 12), width=4)
    # open book
    d.polygon([(60, 40), (92, 32), (92, 78), (60, 86)], fill=(194, 65, 12))
    d.polygon([(60, 40), (28, 32), (28, 78), (60, 86)], fill=(234, 88, 12))
    d.line([(60, 40), (60, 86)], fill=(255, 255, 255), width=3)
    img.save(os.path.join(out_dir, "icon_book_statute.png"))

create_leaf_icon()
create_scales_icon()
create_shield_icon()
create_database_icon()
create_ai_brain_icon()
create_multilingual_icon()
create_cpu_icon()
create_check_audit_icon()
create_book_statute_icon()
print("Created all custom vector icons successfully!")
