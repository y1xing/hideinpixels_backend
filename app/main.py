from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from fastapi import APIRouter, Cookie, Form, status, Body, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, Field
import os
import uvicorn
from dotenv import load_dotenv
import base64
import cv2
import numpy as np
import random
import imageio
from PIL import Image, ImageSequence
from algos.images.image_decode_encode import encode, decode, encode_async
from algos.images.png_bmp import encode_image, decode_image
from algos.images.gif import encode_gif, decode_gif
from algos.audio.audio import wave_encoder, wave_decoder, warning_payload_larger
from algos.video.video import decode_video, encode_video
from config.config import format_base64, convert_base64_bytes, convert_base64_gif, convert_base64_audio, convert_base64_video

load_dotenv()


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
app = FastAPI(title="HideInPixels Backend", version="0.5")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Encode Schema


class EncodeSchema(BaseModel):
    base64Str: str
    type: str
    fileKind: str
    secretMessage: str
    lsbBit: int

    class Config:
        json_schema_extra = {
            "example": {
                "base64Str": "base64 encoded image/video/audio",
                "type": "image",
                "fileKind": "png",
                "secretMessage": "Hello World!",
                "lsbBit": 1
            }
        }


class DecodeSchema(BaseModel):
    base64Str: str
    type: str
    fileKind: str
    lsbBit: int

    class Config:
        json_schema_extra = {
            "example": {
                "base64Str": "base64 encoded image/video/audio",
                "type": "image",
                "fileKind": "png",
                "lsbBit": 5

            }
        }


@app.get("/")
async def root():

    return {"api_status": "online", "username": "none"}


# Receive the base 64 encoded image/video/audio and encode it (but just return the same thing for now)
@app.post("/encode")
async def encode(body: EncodeSchema, response: Response):

    body = body.dict()

    base64_str, type, file_kind, secret_message, lsb_bit = body['base64Str'], body[
        'type'], body['fileKind'], body['secretMessage'], body['lsbBit']

    # Front consist of the file type for the frontend to know what to do with the base64
    base64_str_front, base64_str_new = format_base64(base64_str)

    # Check for the type of file
    if type == "image":
        if file_kind == "png" or file_kind == "bmp":

            # Convert base64 to np array
            image = convert_base64_bytes(base64_str_new)

            # Yu Fei's encode function
            encoded_image_yf = await encode_image(image, secret_message, lsb_bit)

            # Check for error
            if encoded_image_yf['status'] == "error":
                return {"status": "error", "message": "Payload too large"}

            output_file_path = f"png_bmp_encoded.{file_kind}"

            # Save the file to png_bmp_encoded.png/bmp
            cv2.imwrite(output_file_path, encoded_image_yf['data'])

            # Convert png_bmp_encoded.png to base64
            with open(output_file_path, 'rb') as f:
                img_bytes = f.read()
                base64_str_new = base64.b64encode(img_bytes).decode('utf-8')
                base64_str_new = f"{base64_str_front},{base64_str_new}"

        elif file_kind == "gif":
            # Convert base64 to np array
            image = convert_base64_gif(base64_str_new)

            # Test saving of gif
            # Decode the Base64 string into binary data
            gif_binary_data = base64.b64decode(base64_str_new)

            # Specify the output file path and name
            input_file_path = "gif_encoded_before.gif"

            # Write the binary data to a file
            with open(input_file_path, "wb") as output_file:
                output_file.write(gif_binary_data)

            print(f"Successfully saved the GIF to {input_file_path}")

            # Yu Fei's encode function
            encoded_gif_yf = await encode_gif(input_file_path, secret_message, lsb_bit)

            print(encoded_gif_yf)

            # Check for error
            if encoded_gif_yf['status'] == 'error':
                return {"status": "error", "message": "Payload too large"}

            output_file_path = f"gif_encoded.{file_kind}"

            video_fps = encoded_gif_yf['video_fps']
            data = encoded_gif_yf['data']

            # write to file
            with imageio.get_writer(output_file_path, mode="I",
                                    duration=1000 * 1 / video_fps) as writer:
                for en_frame in data:
                    writer.append_data(en_frame)

            with open(output_file_path, 'rb') as f:
                img_bytes = f.read()
                base64_str_new = base64.b64encode(img_bytes).decode('utf-8')
                base64_str_new = f"{base64_str_front},{base64_str_new}"

        else:
            # Return error
            return {"status": "error", "message": "Invalid fileKind"}
    elif type == "video":

        if file_kind == 'mp4' or file_kind == 'avi':
          # Convert the base64 audio file to actual audio first
            video_path = convert_base64_video(
                base64_str_new, file_kind=file_kind)

            payload_path = "video_payload.txt"

            # Write the secret message into a video_payload.txt
            with open(payload_path, 'w') as f:
                f.write(secret_message)

            output_file_path = "video_encoded.avi"

            # Encode the video file
            await encode_video(video_path, payload_path, output_file_path)

            with open(output_file_path, 'rb') as f:
                video_bytes = f.read()
                base64_str_new = base64.b64encode(
                    video_bytes).decode('utf-8')
                base64_str_new = f"{base64_str_front},{base64_str_new}"

        else:
            # Return error
            return {"status": "error", "message": "Invalid fileKind"}
    elif type == "audio":
        if file_kind == "mp3" or file_kind == 'wav':
            # Convert the base64 audio file to actual audio first
            audio_path = convert_base64_audio(
                base64_str_new, file_kind=file_kind)

            # Check if payload is too large
            if warning_payload_larger(audio_path, secret_message):
                return {"status": "error", "message": "Payload too large"}

            # Encode the audio file
            try:
                encoded_audio_path = await wave_encoder(
                    audio_path, lsb_bit, secret_message, file_kind)

                # Convert the encoded audio file to base64
                with open(encoded_audio_path, 'rb') as f:
                    audio_bytes = f.read()
                    base64_str_new = base64.b64encode(
                        audio_bytes).decode('utf-8')
                    base64_str_new = f"{base64_str_front},{base64_str_new}"
            except IndexError as e:
                return {"status": "error", "message": "Payload too large"}

        else:
            # Return error
            return {"status": "error", "message": "Invalid fileKind"}

    return {"status": "success",  'type': type, 'fileKind': file_kind, 'secretMessage': secret_message, 'lsbBit': lsb_bit, 'base64Str_new': base64_str_new}


# Receive the base 64 decodec image/video/audio and decode it
@app.post("/decode")
async def decode(body: DecodeSchema, response: Response):

    body = body.dict()

    base64_str, type, file_kind, lsb_bit = body['base64Str'], body['type'], body['fileKind'], body['lsbBit']

    # Front consist of the file type for the frontend to know what to do with the base64
    base64_str_front, base64_str_new = format_base64(base64_str)

    # Check for the type of file
    if type == "image":
        if file_kind == "png" or file_kind == "bmp":

            # Convert base64 to np array
            image = convert_base64_bytes(base64_str_new)

            # Yu Fei's encode function
            secret_message = await decode_image(image, lsb_bit)

            print(secret_message)

        elif file_kind == "gif":
            # Convert base64 to np array
            image = convert_base64_gif(base64_str_new)

            # Test saving of gif
            # Decode the Base64 string into binary data
            gif_binary_data = base64.b64decode(base64_str_new)

            # Specify the output file path and name
            output_file_path = "gif_decoded.gif"

            # Write the binary data to a file
            with open(output_file_path, "wb") as output_file:
                output_file.write(gif_binary_data)

            print(f"Successfully saved the GIF to {output_file_path}")

            # Yu Fei's encode function
            secret_message = await decode_gif(output_file_path, lsb_bit)

            print(secret_message)

        elif file_kind == "jpeg":
            pass
        else:
            # Return error
            return {"status": "error", "message": "Invalid fileKind"}
    elif type == "video":
        if file_kind == "avi":
            video_path = convert_base64_video(base64_str_new, file_kind)

            # Decode the video file
            secret_message = await decode_video(video_path)

        else:
            # Return error
            return {"status": "error", "message": "Invalid fileKind"}
    elif type == "audio":
        # Convert the base64 audio file to actual audio first
        audio_path = convert_base64_audio(
            base64_str_new, file_kind=file_kind)

        # Encode the audio file
        secret_message = await wave_decoder(audio_path)

    else:
        # Return error
        return {"status": "error", "message": "Invalid fileKind"}

    return {"status": "success",  'type': type, 'fileKind': file_kind, 'lsbBit': lsb_bit, 'message': secret_message}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost",
                port=8001, reload=True, reload_dirs=".")
