import pytesseract
from PIL import Image
import pandas as pd
import re
import os

# Set up tesseract executable path if needed (uncomment if you have to specify)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path where you saved the images
image_files = [
    '/mnt/data/IMG_0497.PNG',
    '/mnt/data/IMG_0498.PNG',
    '/mnt/data/IMG_0499.PNG',
    '/mnt/data/IMG_0500.PNG',
    '/mnt/data/IMG_0501.PNG',
    '/mnt/data/IMG_0502.PNG'
]

# Storage for extracted data
contacts = []

# Regex to find phone numbers (Nigerian format in your images)
phone_pattern = re.compile(r'(\+234\s?\d{3}\s?\d{3}\s?\d{4}|\d{4}\s?\d{3}\s?\d{4})')

for image_path in image_files:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    
    # Extract the name: first non-empty line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        name = lines[0]
    else:
        name = 'Unknown'
    
    # Extract the phone number
    phones = phone_pattern.findall(text)
    phone = phones[0] if phones else 'Not found'

    contacts.append({'Name': name, 'Phone Number': phone})

# Create DataFrame
df = pd.DataFrame(contacts)

# Save to Excel
output_path = '/mnt/data/contacts.xlsx'
df.to_excel(output_path, index=False)

print(f"Contacts saved to {output_path}")
