"""Generate the resource QR codes used in the IP-SAKTI Sahayak deck."""

from pathlib import Path

import qrcode


REPO_ROOT = Path(__file__).resolve().parents[2]
QR_DIR = REPO_ROOT / "presentation" / "assets" / "qrcodes"

# Prefer stable official landing pages over old direct-file URLs that have moved.
# GitHub and Drive destinations match the clickable links embedded in slide 3.
URLS = {
    "qr_ipindia.png": "https://ipindia.gov.in/resource/patents-resources-act",
    "qr_nba.png": "https://nbaindia.nic.in/",
    "qr_ayush.png": "https://ayush.gov.in/resources/pdf/quality_standards/Drugs-and-Cosmetics-Act-Rules.pdf",
    "qr_wipo.png": "https://www.wipo.int/en/web/treaties/ip/gratk/index",
    "qr_nagoya.png": "https://www.cbd.int/abs/text/default.shtml",
    "qr_pcimh.png": "https://www.portal.pcimh.gov.in/",
    "qr_tkdl.png": "https://tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
    "qr_hf.png": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
    "qr_github.png": "https://github.com/Rengoku9000/ip-shakti",
    "qr_report.png": "https://drive.google.com/drive/folders/1nfDT2fVEXlzJ61C37zGnA_zNBlg5g-mK?usp=drive_link",
}


def main():
    QR_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in URLS.items():
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(QR_DIR / filename)
    print(f"Generated {len(URLS)} QR codes in {QR_DIR}")


if __name__ == "__main__":
    main()
