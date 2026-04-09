from PIL import Image
import pytesseract

# 👇 Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 👇 Load image (put a test image in your folder)
img = Image.open("test.png")

# 👇 Extract text
text = pytesseract.image_to_string(img)

print("\nExtracted Text:\n")
print(text)