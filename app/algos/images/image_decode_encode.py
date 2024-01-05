import numpy as np
import cv2
import random
import base64

def convert_to_binary(data):

    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def convert_base64_bytes(base64Str):

    binary_data = base64.b64decode(base64Str)

    # Convert the binary data to a NumPy array
    image_array = np.frombuffer(binary_data, np.uint8)

    # Use OpenCV to read the NumPy array as an image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    print(type(image))

    return image

async def encode_async(base64Str, secret_data):
    # image = cv2.imread(image_name)  # read the image
    image = convert_base64_bytes(base64Str)  # Assuming convert_base64_bytes has an asynchronous version

    n_bytes = image.shape[0] * image.shape[1] * 3 // 8  # maximum bytes to encode
    print("[*] Maximum bytes to encode:", n_bytes)
    secret_data += "======"
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need a bigger image or less data.")
    print("[*] Encoding data...")

    data_index = 0
    binary_secret_data = convert_to_binary(secret_data)  # convert data to binary
    data_len = len(binary_secret_data)  # size of data to hide
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]
            r, g, b = convert_to_binary(pixel)  # convert RGB values to binary format
            if data_index < data_len:
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)  # Least significant red pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)  # Least significant green pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)  # Least significant blue pixel bit
                data_index += 1
            if data_index >= data_len:
                break

    print(f"type of image is {type(image)}")

    return image


def encode(base64Str, secret_data):
    # image = cv2.imread(image_name)  # read the image
    image = convert_base64_bytes(base64Str)


    n_bytes = image.shape[0] * image.shape[1] * 3 // 8  # maximum bytes to encode
    print("[*] Maximum bytes to encode:", n_bytes)
    secret_data += "======"  # add stopping criteria
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need a bigger image or less data.")
    print("[*] Encoding data...")

    data_index = 0
    binary_secret_data = convert_to_binary(secret_data)  # convert data to binary
    data_len = len(binary_secret_data)  # size of data to hide
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]
            r, g, b = convert_to_binary(pixel)  # convert RGB values to binary format
            if data_index < data_len:  # modify the least significant bit only if there is still data to store
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)  # Least significant red pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)  # Least significant green pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)  # Least significant blue pixel bit
                data_index += 1
            if data_index >= data_len:  # if data is encoded, break out of the loop
                break



    return image



def decode(image_name):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = convert_to_binary(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    #split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len (binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            break
    return decoded_data[:-5]



