import numpy as np
import cv2
import imageio
from PIL import Image, ImageSequence


def convert_to_binary(data):
    """
    brief: converts str/array/int to bytes

    in (str/array/int): data to be converted
    out (bytes): data in bytes
    """

    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")


"""
@brief: encode payload into image/frame

@param[in] image (np.array): image in array form (height, weight, RGB)
@param[in[ payload (str): payload text
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return encoded_image (np.array)
"""


def encode(image, b_payload, n_lsb):
    print("[*] Encoding data...")

    data_index = 0  # start index
    data_len = len(b_payload)  # size of data to hide

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # get each RGB pixel (i, j, 3)
            pixel = image[i, j]

            # convert RGB values to binary format
            r, g, b = convert_to_binary(pixel)

            # replace the n least significant bit of RED pixel bits
            if data_index < data_len:
                pixel[0] = int(
                    r[:-n_lsb] + b_payload[data_index:data_index + n_lsb], 2)
                data_index += n_lsb

            # replace the n least significant bit of GREEN pixel bits
            if data_index < data_len:
                pixel[1] = int(
                    g[:-n_lsb] + b_payload[data_index:data_index + n_lsb], 2)
                data_index += n_lsb

            # replace the n least significant bit of BLUE pixel bits
            if data_index < data_len:
                pixel[2] = int(
                    b[:-n_lsb] + b_payload[data_index:data_index + n_lsb], 2)
                data_index += n_lsb

            # encoded all payload bytes
            if data_index >= data_len:
                return image

    return False


"""
@brief: decode payload from image/frame

@param[in] image (np.array): image in array form (height, weight, RGB)
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return decoded_data (str)
"""


def decode(image, n_lsb):
    print("[*] Decoding...")

    b_data = ""  # buffer for payload bits to be converted to char
    decoded_data = ""  # converted data

    for idx, row in enumerate(image):
        for pixel in row:
            # get each RGB pixel (i, j, 3) and convert to binary to be decoded

            r, g, b = convert_to_binary(pixel)

            # get payload from the n least significant bit of each RGB pixel bits
            b_data += r[8 - n_lsb:]
            b_data += g[8 - n_lsb:]
            b_data += b[8 - n_lsb:]

            # read 8 bits (1 char) and add to output until buffer runs out
            while len(b_data) >= 8:

                byte = b_data[:8]  # 1 char byte

                # convert char byte to char literal
                decoded_data += chr(int(byte, 2))

                # remove read bits
                b_data = b_data[8:]

                # exit when reach stopper
                if decoded_data[-5:] == "=====":
                    return decoded_data[:-5]

    return "Unable to decode"
