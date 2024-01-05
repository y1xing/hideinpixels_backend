# Encoder and Decoder for mp3 and wav
import subprocess
# This library is needed to open wave format files
import wave
import os
import random

"""This file is an encoder / decoder for both mp3 and wav files, however the mp3 file is converted to wav first before 
it is being encoded. It is not converted back to mp3 after encoding as there will be a loss of data and the 
decoded message will be messed up. So it is left in a lossless form"""

"""This function is to read from text file if you need it"""


def warning_payload_larger(file_path, text):
    # Get the size of the audio file in bytes
    audio_file_size = os.path.getsize(file_path)
    print(audio_file_size)

    # Get the len of the text
    text_file_size = len(text)

    # Compare the sizes
    if text_file_size > audio_file_size:
        print("Warning: Text file is larger than the audio file. Consider using a larger audio file or a shorter "
              "message.")
        return True
    else:
        return False


"""This function is to convert mp3 to wave"""


def convert_to_wav(file_path):

    names = ['temp.wav', 'temp2.wav', 'temp3.wav',
             'temp4.wav', 'temp5.wav', 'temp6.wav', 'temp7.wav']

    output_wav_file = random.choice(names)
    subprocess.call(['ffmpeg', '-i', file_path, '-ab', '190k',
                    '-ac', '2', '-ar', '44100', output_wav_file])

    return output_wav_file


async def wave_encoder(file_path, num_lsb, text, file_type):
    # Convert MP3 to WAV if needed
    if file_type == 'mp3':
        file_path = convert_to_wav(file_path)

    string = text
    song = wave.open(file_path, mode='rb')
    # Read frames and convert to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    # print(len(frame_bytes))

    # Append dummy data to fill out rest of the bytes. Receiver shall detect and remove these characters.
    string = string + \
        int((len(frame_bytes) - (len(string) * num_lsb * 8)) / 8) * '#'
    # Convert text to bit array
    bits = list(
        map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in string])))

    # Replace specified number of LSBs of each byte of the audio data by message bits
    for i in range(len(bits)):
        for j in range(num_lsb):
            frame_bytes[i] = (frame_bytes[i] & (
                255 - (1 << j))) | ((bits[i] >> j) & 1)
    # Get the modified bytes
    frame_modified = bytes(frame_bytes)

    # Write bytes to a new wave audio file
    output_file_path = f"encoded_wav_mp3.{file_type}"
    with wave.open(output_file_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    song.close()

    return output_file_path


"""This function wave_decoder, takes in 1 parameter only and that is the file path"""


async def wave_decoder(file_path):
    song = wave.open(file_path, mode='rb')
    # Convert audio to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # Extract the LSB of each byte
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    print("Extracted LSBBits ", extracted)

    # Convert byte array back to string
    string = "".join(chr(int(
        "".join(map(str, extracted[i:i + 8])), 2)) for i in range(0, len(extracted), 8))
    # Cut off at the filler characters
    decoded = string.split("###")[0]

    # Print the extracted text
    print("Successfully decoded: " + decoded)
    song.close()

    return decoded
