import numpy as np
import cv2
import imageio
from PIL import Image, ImageSequence
from .encode_decode import encode, decode, convert_to_binary


"""
@brief: iterate over frames in gif and encode payload in each frame

@param[in] frames (np.array): array of frames in gif
@param[in] payload (str): payload text
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return encoded_frames (np.array)
"""


def read_gif(filename):
    # read in gif
    video_capture = cv2.VideoCapture(filename)
    video_fps = video_capture.get(cv2.CAP_PROP_FPS)
    frames = []

    if not video_capture.isOpened():
        print("Error")

    # get all frames
    while video_capture.isOpened():
        ret, frame = video_capture.read()

        if ret:
            frames.append(frame)
        else:
            break

    video_capture.release()
    cv2.destroyAllWindows()

    # encode frames
    return np.array(frames), video_fps


async def encode_gif(filename, payload, n_lsb):

    # read in gif
    frames, video_fps = read_gif(filename)

    # return error if n least significant bits is more than 7 bits or less than 1
    if n_lsb < 1 or n_lsb > 7:
        raise ValueError(
            "[!] Invalid number of least significant bits, need to be between 1 to 7.")

    # calculate maximum payload bytes
    n_bytes = (frames.shape[1] * frames.shape[2] *
               3 * frames.shape[0]) // (8 - n_lsb)
    print("[*] Maximum bytes to encode: ", n_bytes)

    frame_payloads = []
    data_per_frame = len(payload) // len(frames)  # amount of data per frame

    # allocate payload equally for each frame
    for index in range(0, len(payload), data_per_frame):
        if len(frame_payloads) >= len(frames) - 1:
            frame_payloads.append(payload[index:] + "=====")
            break

        f_payload = payload[index:index + data_per_frame] + "====="
        frame_payloads.append(f_payload)

    # return error if payload larger than max payload byte size
    if np.sum([len(p) for p in frame_payloads]) > n_bytes:
        raise ValueError(
            "[!] Insufficient bytes, need a bigger image or less data.")

    encoded_frames = []

    # convert each frame's payload to binary, encode the frame,
    for index, f_payload in enumerate(frame_payloads):
        # convert each frame's payload to binary
        b_payload = convert_to_binary(f_payload)

        # encode the frame and convert from BGR to RGB (opencv uses BGR, imageio uses RGB)
        encoded_frame = encode(frames[index], b_payload, n_lsb)
        encoded_frame = cv2.cvtColor(encoded_frame, cv2.COLOR_BGR2RGB)

        encoded_frames.append(encoded_frame)

    return {"status": "success", "data": np.array(encoded_frames), "video_fps": video_fps}


"""
@brief: iterate over frames in gif and decode payload in each frame

@param[in] frames (np.array): array of frames in gif
@param[in] n_lsb (int): number of least significant bits to use for encoding/decoding

@return message (str)
"""


async def decode_gif(filename, n_lsb):
    # read in gif
    frames, video_fps = read_gif(filename)

    # return error if n least significant bits is more than 7 bits or less than 1
    if n_lsb < 1 or n_lsb > 7:
        raise ValueError(
            "[!] Invalid number of least significant bits, need to be between 1 to 7.")

    message = ""

    for index, frame in enumerate(frames):
        message += decode(frame, n_lsb)

    print(message)

    return message
