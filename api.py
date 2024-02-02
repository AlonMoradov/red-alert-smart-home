import dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from utils import add_to_env_file, get_hue_bridge_ip_addr, get_hue_bridge_username

app = Flask(__name__)


@app.route("/get_cities_list", methods=["GET"])
def get_cities_list():
    headers = {
        "Accept": "*/*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://www.oref.org.il/12481-he/Pakar.aspx",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    params = (("lang", "he"),)

    response = requests.get(
        "https://www.oref.org.il/Shared/Ajax/GetDistricts.aspx",
        headers=headers,
        params=params,
    )
    return jsonify(response.json())


@app.route("/get_current_city", methods=["GET"])
def get_current_city():
    current_city = dotenv.get_key(".env", "CITY") or "אביגדור"
    return jsonify({"city": current_city})


@app.route("/set_current_city", methods=["POST"])
def set_current_city():
    city = request.json.get("city")
    add_to_env_file(("CITY", city))
    return jsonify({"city": city, "success": True})


@app.route("/get_hue_bridge_ip_addr", methods=["GET"])
def get_bridge_ip_addr():
    ip_addr = dotenv.get_key(".env", "IP_ADDR") or get_hue_bridge_ip_addr()
    return jsonify({"ip_addr": ip_addr})


@app.route("/get_hue_bridge_username", methods=["GET"])
def get_bridge_username():
    try:
        username = dotenv.get_key(".env", "USERNAME") or get_hue_bridge_username()
    except Exception as e:
        return jsonify({"error": str(e)})
    return jsonify({"username": username})


@app.route("/get_hue_bridge_mac_addr", methods=["GET"])
def get_bridge_mac_addr():
    return jsonify({"mac_addr": dotenv.get_key(".env", "MAC_ADDR")})


if __name__ == "__main__":
    CORS(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
