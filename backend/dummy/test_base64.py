import base64

# Replace with your Base64 string from the JSON
base64_string = "iVBORw0KGgoAAAANSUhEUgAABase64encodedJPEGimagedatQ=="

# Decode the Base64 string and save it as an image
with open("decoded_image.jpg", "wb") as f:
    f.write(base64.b64decode(base64_string))

print("Image saved successfully as decoded_image.jpg")
