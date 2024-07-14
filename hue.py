import json
import time
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests

from utils import get_hue_bridge_ip_addr, get_hue_bridge_username

USERNAME = get_hue_bridge_username()

HUE_BRIDGE_ADDR = get_hue_bridge_ip_addr()

BASE_URL = f"http://{HUE_BRIDGE_ADDR}/api/{USERNAME}"


def get_all_lights() -> dict:
    """
    Get all lights from the bridge

    Returns:
        dict: All lights
    """
    return requests.get(f"{BASE_URL}/lights").json()


def get_state() -> dict:
    """
    Get the state of all lights

    Returns:
        dict: The state of all lights
    """
    all_lights = get_all_lights()
    res = {}
    for i in all_lights:
        res[i] = {
            k: v
            for (k, v) in all_lights[i]["state"].items()
            if k in ["on", "bri", "hue", "sat", "xy", "ct"]
        }

    return res


def set_state(light, data) -> str:
    """
    Set the state of a light

    Args:
        light (str): The light id
        data (dict): The data to set

    Returns:
        str: The response
    """
    return json.dumps(
        requests.put(
            f"{BASE_URL}/lights/{light}/state",
            data=json.dumps(data),
        ).json(),
        indent=4,
    )


def red_alert() -> None:
    """
    Red alert - all lights blink red 3 times, then stay on with white color for 3 minutes
    """
    lights_state = get_state()

    def action(light):
        for _ in range(3):
            set_state(light, {"on": True, "xy": (0.675, 0.322), "bri": 254})
            requests.get("http://wled.local/win&A=0&R=255&G=0&B=0")
            sleep(1)
            requests.get("http://wled.local/win&A=255&R=255&G=0&B=0")
            set_state(light, {"on": True, "xy": (0.3227, 0.3290), "bri": 254})
            sleep(1)

        sleep(60 * 3)
        set_state(light, lights_state[light])

    with ThreadPoolExecutor() as pool:
        pool.map(action, lights_state)


if __name__ == "__main__":
    # api documentation - http://www.burgestrand.se/hue-api/api/lights/
    # xy color values - https://www.enigmaticdevices.com/philips-hue-lights-popular-xy-color-values/
    start = time.time()
    # red_alert()
    print(f"{USERNAME = }")
    print(f"{HUE_BRIDGE_ADDR = }")
    print(f"took {time.time() - start}")
