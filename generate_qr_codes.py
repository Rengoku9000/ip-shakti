import os
import qrcode

qr_dir = r"c:\Projects\drugvista\extracted_assets\qrcodes"
os.makedirs(qr_dir, exist_ok=True)

urls = {
    "qr_ipindia.png": "https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
    "qr_nba.png": "http://nbaindia.org/content/25/19/1/act.html",
    "qr_ayush.png": "https://ayush.gov.in/docs/drugs-and-cosmetics-act-1940.pdf",
    "qr_wipo.png": "https://www.wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf",
    "qr_nagoya.png": "https://www.cbd.int/abs/text/default.shtml",
    "qr_pcimh.png": "https://pcimh.gov.in",
    "qr_tkdl.png": "https://www.tkdl.res.in",
    "qr_hf.png": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
    "qr_github.png": "https://github.com/Rengoku9000/Drugvista",
    "qr_report.png": "https://github.com/Rengoku9000/Drugvista/blob/main/README.md"
}

for fname, url in urls.items():
    qr = qrcode.QRCode(box_size=6, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(os.path.join(qr_dir, fname))

print("Generated all 10 QR codes successfully!")
