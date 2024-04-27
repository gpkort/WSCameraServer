#!/usr/bin/env python

import asyncio

import numpy as np
import websockets
import cv2
import json
import configparser
import logging
from image.ImageData import Image

CONFIG_FILE = "config.ini"
LOGGING_SECTION = "Logging"
SERVER_SECTION = "SocketServer"
CAMERA_SECTION = "Camera"

config = configparser.ConfigParser()
logger = logging.getLogger(__name__)

cap = None


async def get_image(websocket, info: dict):
    img: Image = Image(np.zeros((0, 0, 0)), 0, 0, 1)

    has_frame, frame = cap.read()
    if not has_frame:
        logger.warning("Image not available.")
    else:
        logger.info(f"Captured Image: h:{frame.shape[0]}, w: {frame.shape[1]}")
        img.image = frame
        img.height = frame.shape[0]
        img.width = frame.shape[1]
        img.status = 0

    # await websocket.send(json.dumps(res)) #

    await websocket.send(img.to_json())


async def handler(websocket):
    async for message in websocket:
        if message != "":
            try:
                req: dict = json.loads(message)
                reqtype = req.get("type")

                if reqtype is not None:
                    match reqtype:
                        case "image":
                            await get_image(websocket, req)
                        case _:
                            logger.warning(f"Unknown request type: {reqtype}")
                else:
                    logger.warning(f"Json format does not contain \"type\" key.")                
            except json.JSONDecodeError as e:
                logger.warning(f"Cannot parse {message}, {e.msg}")


async def main():
    async with websockets.serve(handler,
                                host=config[SERVER_SECTION]["IP"],
                                port=int(config[SERVER_SECTION]["PORT"])):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        config.read(CONFIG_FILE)
    except:
        print("WebSocket Server cannot find \"config.ini\"")
        exit(1)

    dev_num: int = int(config[CAMERA_SECTION]["device_number"])
    cap = cv2.VideoCapture(dev_num)
    if not cap.isOpened():
        logger.warning(f"Camera is not available! for device({dev_num}")

    logging.basicConfig(filename=config[LOGGING_SECTION]["log"],
                        encoding='utf-8',
                        level=int(config[LOGGING_SECTION]["level"]))

    logger.info("Starting Server")

    asyncio.run(main())
    cap.release()
