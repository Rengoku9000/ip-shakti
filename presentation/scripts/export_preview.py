import comtypes.client
import fitz
import os
import time

ppt_path = os.path.abspath(r"c:\Projects\drugvista\presentation\source\IP-SAKTI_Sahayak_SIH2026.pptx")
pdf_path = os.path.abspath(r"c:\Projects\drugvista\presentation\work\renders\IP-SAKTI_Sahayak_SIH2026.pdf")
out_dir = os.path.abspath(r"c:\Projects\drugvista\presentation\work\renders\slides_preview")
os.makedirs(out_dir, exist_ok=True)

try:
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1
    deck = powerpoint.Presentations.Open(ppt_path)
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except:
            pass
    deck.SaveAs(pdf_path, 32)
    deck.Close()
    powerpoint.Quit()
    print("PowerPoint saved to PDF successfully.")
except Exception as e:
    print(f"Error via COM: {e}")

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(out_dir, f"exact_slide_{i+1}.png"))
    print(f"Exported {len(doc)} slides to PNG successfully!")
