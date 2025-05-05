import cv2
import pytesseract
import pandas as pd
import re
import os

# If Tesseract isn’t on your PATH, uncomment & set the path:
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

# your screenshots folder & files
IMAGE_DIR = 'img'
image_files = ['IMG_0498.PNG', 'IMG_0499.PNG', 'IMG_0500.PNG']

# regex for “0806 849 6761” or “+234 806 849 6761”
phone_re = re.compile(r'(?:\+234|0)\s*\d{3}[\s-]?\d{3}[\s-]?\d{4}')

def extract_name(img):
    h, w = img.shape[:2]
    # crop the band where the contact name appears (20%→32% down)
    y1, y2 = int(h * 0.20), int(h * 0.32)
    x1, x2 = int(w * 0.05), int(w * 0.95)
    roi = img[y1:y2, x1:x2]

    # grayscale + equalize to boost white-on-grey
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # invert + Otsu threshold so name text is black on white
    inv = 255 - gray
    _, th = cv2.threshold(inv, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR as a single line, only letters & spaces
    cfg = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    text = pytesseract.image_to_string(th, config=cfg).strip()
    # take the first non-empty line
    return text.splitlines()[0] if text else None

def extract_phones(img):
    # same as before: blur + Otsu + invert → block OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inv = cv2.bitwise_not(thresh)
    raw = pytesseract.image_to_string(inv, config='--psm 6')
    # normalize & return matches
    return [m.group().replace(' ', '').replace('-', '')
            for m in phone_re.finditer(raw)]

rows = []
for fname in image_files:
    path = os.path.join(IMAGE_DIR, fname)
    img = cv2.imread(path)
    if img is None:
        print(f"⚠️ Couldn’t load {path}")
        continue

    name = extract_name(img) or os.path.splitext(fname)[0]
    phones = extract_phones(img)

    if not name:
        print(f"⚠️ No name OCR’d in {fname}")
    if not phones:
        print(f"⚠️ No phone OCR’d in {fname}")

    for ph in phones:
        rows.append({'Name': name, 'Phone': ph})

# dump to Excel
df = pd.DataFrame(rows)
df.to_excel('contacts.xlsx', index=False)
print(f"✅ Extracted {len(df)} rows → contacts.xlsx")
