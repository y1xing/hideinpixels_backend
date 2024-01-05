import math
import os
import re
import shutil
from subprocess import call, STDOUT
import cv2
from PIL import Image

# Global Variable
global frame_location

"""This function extracts the number of frames from a video through opencv library and stores it in a temporary folder
called ./temp. If the folder does not exist, it creates one"""


def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    # Temporary folder created to store the frames and audio from the video.
    temp_folder = "./temp"
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1


"""This function simply deletes the temp file created earlier"""


def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")


"""This function takes the payload and converts it into binary so that it can be encoded into the image"""


def generateData(data):
    newdata = []
    for i in data:  # list of binary codes of given data
        newdata.append(format(ord(i), '08b'))
    return newdata


"""This funcion modifies the pixel value to encode the binary data. It iterates through the binary data"""


# Pixels modified according to encoding data in generateData
def modifyPixel(pixel, data, bits):
    datalist = generateData(data)
    lengthofdata = len(datalist)
    imagedata = iter(pixel)
    for i in range(lengthofdata):
        # Extracts 3 pixels at a time
        pixel = [value for value in imagedata.__next__(
        )[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        # Pixel value should be made odd for 1 and even for 0
        for j in range(0, bits):  # choose the number of bits for encoding
            if datalist[i][j] == '0' and pixel[j] % 2 != 0:
                pixel[j] -= 1
            elif datalist[i][j] == '1' and pixel[j] % 2 == 0:
                if pixel[j] != 0:
                    pixel[j] -= 1
                else:
                    pixel[j] += 1
        # Eighth pixel of every set tells whether to stop ot read further. 0 means keep reading; 1 means thec message
        # is over.
        if i == lengthofdata - 1:
            if pixel[-1] % 2 == 0:
                if pixel[-1] != 0:
                    pixel[-1] -= 1
                else:
                    pixel[-1] += 1
        else:
            if pixel[-1] % 2 != 0:
                pixel[-1] -= 1
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]


"""Takes an image and data and modifies the image pixel"""


def encoder(newimage, data):
    w = newimage.size[0]
    (x, y) = (0, 0)

    for pixel in modifyPixel(newimage.getdata(), data, 8):

        # Putting modified pixels in the new image
        newimage.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


"""Main encoding function that takes several parameters
1. Start frame
2. End frame
3. Payload
4. Location of frames
5. Location of output folder"""


def encode(start, end, filename, frame_loc, output_folder):
    total_frame = end - start + 1
    print("Frame start", start)
    print("\nFrame end", end)
    try:
        with open(filename) as fileinput:  # Store Data to be Encoded
            filedata = fileinput.read()
            filedata += '====='
    except FileNotFoundError:
        print("\nFile to hide not found! Exiting...")
        quit()
    # Data Distribution per Frame
    datapoints = math.ceil(len(filedata) / total_frame)
    # Initialize counter for frame numbers
    counter = start
    print("Performing Steganography...")
    for convnum in range(0, len(filedata), datapoints):  # Beginning , end and step
        numbering = frame_loc + "/" + str(counter) + ".png"
        print("numbering is: ", numbering)
        # Copy Distributed Data into Variable
        encodetext = filedata[convnum:convnum + datapoints]
        try:
            image = Image.open(numbering, 'r')
        except FileNotFoundError:
            print("\n%d.png not found" % counter)
            quit()
            # Create a copy of the image to store the hidden data
        # Create a copy of the image to store the hidden data
        newimage = image.copy()  # New Variable to Store Hidden Data

        # Perform steganography on the current frame to hide the data
        encoder(newimage, encodetext)  # Steganography

        # Generate the new filename for the modified frame in the output folder
        new_img_name = os.path.join(
            output_folder, "{}.png".format(counter))  # Frame Number

        # Save the modified frame with the same format as the original
        newimage.save(new_img_name, str(new_img_name.split(".")
                      [1].upper()))  # Save as New Frame

        # Increment the frame counter for the next iteration
        counter += 1

        # Inform the user that the steganography process is complete
    print("Complete!\n")


"""This decoding function takes in the range of frames and the location of the folder where the frames are stored
eg; /temp"""


# Decode the data in the image
def decode(number, frame_location):
    data = ''
    numbering = str(number)
    decoder_numbering = frame_location + "/" + numbering + ".png"
    image = Image.open(decoder_numbering, 'r')
    imagedata = iter(image.getdata())
    while (True):
        pixels = [value for value in imagedata.__next__(
        )[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        # string of binary data
        binstr = ''
        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
        if re.match("[ -~]", chr(int(binstr, 2))) is not None:  # only decode printable data
            data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data


def input_main(video_filename, message_filename, frame_location, output_file_path):
    # This function splits the videos into frames and stores them in a folder called temp
    frame_extraction(video_filename)

    # Splitting the audio from mp4 and the output is audio.mp3
    call(["ffmpeg", "-i", video_filename, "-q:a", "0", "-map", "a", "audio.mp3", "-y"], stdout=open(os.devnull, "w"),
         shell=True, stderr=STDOUT)

    # Encode the frames with the text file
    encode(0, len(os.listdir(frame_location)) - 1,
           message_filename, frame_location, "temp")

    # Stitching all the files in temp which contains the encoded frames into an avi
    call(["ffmpeg", "-i", "temp/%d.png", "-c:v", "ffv1", output_file_path, "-y"],
         stdout=open(os.devnull, "w"), stderr=STDOUT)

    # Combining avi and mp3 audio into a final avi video
    call(["ffmpeg", "-i", output_file_path, "-i", "audio.mp3", "-c:v", "ffv1", "-c:a", "aac",
          "Embedded_Video.avi", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)


async def encode_video(video_filename, message_filename, output_file_path):
    input_main(video_filename=video_filename,
               message_filename=message_filename,
               frame_location="./temp",
               output_file_path=output_file_path)
    clean_temp()


async def decode_video(file_name):
    frame_extraction(file_name)
    extracted_data = ""
    """From the range of frames in ./temp, decode and extract data"""
    for convnum in range(0, len(os.listdir("./temp")) - 1):
        try:
            # Attempt to extract data from each frame
            extracted_data += decode(convnum, "./temp")
        except StopIteration:
            print("No data found in Frame %d" % convnum)

    # Print everything after the ====== to remove any gibberish or garbage
    result = extracted_data.split("=====", 1)[0]
    clean_temp()

    return result
