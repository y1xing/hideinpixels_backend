import numpy as np
import cv2
import imageio
from PIL import Image, ImageSequence
from .encode_decode import encode, decode, convert_to_binary

"""
@brief: prepare image and encode payload into image

@param[in] image (np.array): image in array form (height, weight, RGB)
@param[in[ payload (str): payload text
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return encoded_image (np.array)
"""


async def encode_image(image, payload, n_lsb):
    # return error if n least significant bits is more than 7 bits or less than 1
    if n_lsb < 1 or n_lsb > 7:
        raise ValueError(
            "[!] Invalid number of least significant bits, need to be between 1 to 7.")

    # calculate maximum payload bytes
    n_bytes = (image.shape[0] * image.shape[1] * 3) // (8 - n_lsb)
    print("[*] Maximum bytes to encode: ", n_bytes)

    payload += "======"  # add stopping criteria

    # return error if payload larger than max payload byte size
    if len(payload) > n_bytes:
        return {"status": "error", "message": "Insufficient bytes"}

    # convert payload to binary
    b_payload = convert_to_binary(payload)

    return {"status": "success", "data": encode(image, b_payload, n_lsb)}


"""
@brief: prepare image and decode payload from image

@param[in] image (np.array): image in array form (height, weight, RGB)
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return decoded_message (str)
"""


async def decode_image(image, n_lsb):
    # return error if n least significant bits is more than 7 bits or less than 1
    if n_lsb < 1 or n_lsb > 7:
        raise ValueError(
            "[!] Invalid number of least significant bits, need to be between 1 to 7.")

    # decode payload from image
    return decode(image, n_lsb)
