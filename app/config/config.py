import numpy as np
import cv2
import random
import base64
import imageio


def format_base64(base64Str):
    base64_front = base64Str.split(',', 1)[0]
    base64_new = base64Str.split(',', 1)[1].strip()

    return base64_front, base64_new


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


def convert_base64_bytes(base64Str):

    binary_data = base64.b64decode(base64Str)

    # Convert the binary data to a NumPy array
    image_array = np.frombuffer(binary_data, np.uint8)

    # Use OpenCV to read the NumPy array as an image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if isinstance(image, np.ndarray) and len(image.shape) == 3 and image.shape[2] == 3:
        print("The 'image' variable is an RGB image with shape:", image.shape)
    else:
        print("The 'image' variable is not in the expected format.")

    print(type(image))

    return image


def convert_base64_gif(base64Str):
    binary_data = base64.b64decode(base64Str)

    # Use imageio to read the GIF frames
    gif_frames = imageio.imread(binary_data)

    if isinstance(gif_frames, np.ndarray) and len(gif_frames.shape) == 4 and gif_frames.shape[
            3] == 3:
        print("The 'gif_frames' variable is an array of RGB frames with shape:",
              gif_frames.shape)
    else:
        print("The 'gif_frames' variable is not in the expected format.")

    print(type(gif_frames))

    return gif_frames


def convert_base64_audio(base64Str, file_kind):
    binary_data = base64.b64decode(base64Str)

    # Write the binary data to a file
    output_file_path = f"audio.{file_kind}"

    # Write the binary data to a WAV file
    with open(output_file_path, "wb") as output_file:
        output_file.write(binary_data)

    return output_file_path


def convert_base64_video(base64Str, file_kind):
    binary_data = base64.b64decode(base64Str)

    # Write the binary data to a file
    output_file_path = f"video.{file_kind}"

    # Write the binary data to a WAV file
    with open(output_file_path, "wb") as output_file:
        output_file.write(binary_data)

    return output_file_path
