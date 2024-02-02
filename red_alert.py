import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv
from requests.exceptions import JSONDecodeError

from hue import red_alert

load_dotenv()

logger = logging.getLogger(__name__)
MY_CITY = os.getenv("CITY", "אביגדור")

print(MY_CITY)


def write_id_to_log(current_alert_id: int) -> None:
    """Write the current alert id to log file

    Args:
        current_alert_id (int): The current alert id
    """
    with open("last_alert_id.log", "w") as f:
        f.write(str(current_alert_id))
    logger.info(f"current alert id: {current_alert_id} was written to log")


def read_id_from_log() -> int:
    """Read the last alert id from log file

    Returns:
        int: The last alert id
    """
    try:
        with open("last_alert_id.log", "r") as f:
            last_alert_id = int(f.read())
    except FileNotFoundError:
        last_alert_id = 0
    return last_alert_id


def get_alert() -> dict:
    """Get the last alert from api

    Returns:
        dict: The last alert
    """
    try:
        current_alert = requests.get(
            "https://www.oref.org.il/WarningMessages/alert/alerts.json",
            headers={
                "Accept": "*/*",
                "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Content-Type": "application/json;charset=utf-8",
                "Referer": "https://www.oref.org.il/12481-he/Pakar.aspx",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            },
        )
        current_alert.encoding = "utf-8-sig"
        logger.info(f"{current_alert.status_code} {current_alert.reason}")
        current_alert = current_alert.json()
        current_alert = {
            key: value for key, value in current_alert.items() if key in ["id", "data"]
        }
        logger.info(f"last_alert from oref: {current_alert}")
        return current_alert
    except JSONDecodeError:
        return {"id": 0, "data": []}


def is_new_alert(current_alert: dict, last_alert_id: int) -> bool:
    """Check if the current alert is new by comparing the current alert id to the last alert id

    Args:
        current_alert (dict): Current alert
        last_alert_id (int): Last alert id

    Returns:
        bool: True if the last alert is new, False otherwise
    """
    if int(current_alert["id"]) > int(last_alert_id):
        logger.info(f"New alert: {current_alert['id']}")
        return True
    return False


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    last_alert_id = read_id_from_log()
    current_alert = get_alert()
    if not is_new_alert(current_alert, last_alert_id):
        return

    alert_cities = current_alert["data"]

    write_id_to_log(current_alert["id"])

    if MY_CITY in alert_cities:
        with ThreadPoolExecutor() as pool:
            pool.submit(red_alert)
        logger.info(f"*** Alert is in {MY_CITY} ***")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error(traceback.format_exc())
