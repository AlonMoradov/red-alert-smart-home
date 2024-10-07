import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
import websockets
import asyncio

from dotenv import load_dotenv
from hue import red_alert

load_dotenv()

logger = logging.getLogger(__name__)
MY_CITY = os.getenv("CITY", "אביגדור")

SOCKET_URL = "wss://ws.tzevaadom.co.il:8443/socket?platform=WEB"

async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        # Move the connection inside the async function to attach it to the correct loop
        async with websockets.connect(
            SOCKET_URL,
            origin="https://www.tzevaadom.co.il",
            subprotocols=["chat"]
        ) as websocket:
            while True:
                response = await websocket.recv()
                logger.info(response)
                if MY_CITY in response['data']['cities']:
                    with ThreadPoolExecutor() as pool:
                        pool.submit(red_alert)
                    logger.info(f"*** Alert is in {MY_CITY} ***")
    except Exception:
        logger.error(traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.error(traceback.format_exc())
