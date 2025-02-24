# download resource needed
# pip install qrcode[pil]

import qrcode

# get url entered
url = input("Please enter the link to summon a QRcode：")

# main
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# save image
img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode.png")

print("QRcode saved as qrcode.png")