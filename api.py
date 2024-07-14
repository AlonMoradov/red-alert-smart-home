import dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from utils import add_to_env_file, get_hue_bridge_ip_addr, get_hue_bridge_username

app = Flask(__name__)

@app.route("/get_recent_alerts", methods=["POST"])
def get_recent_alerts():
    """
    Get recent alerts from the Oref API
    
    mode 1 = alerts in the last 24 hours
    mode 2 = alerts in the last 7 days
    mode 3 = alerts in the last 30 days
    """
    mode = request.json.get("mode", 1)
    current_city = dotenv.get_key(".env", "CITY") or "אביגדור"

    params = {
        'lang': 'he',
        'mode': str(mode) if mode in [1, 2, 3] else '1',
        'city_0': current_city,
    }

    response = requests.get(
        'https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx',
        params=params,
    )
    
    match response.status_code:
        case 200:
            return response.json()
        case _:
            return jsonify({"error": "Failed to get recent alerts"})

@app.route("/get_cities_list", methods=["GET"])
def get_cities_list():
    with open('/home/ubuntu/red_alert_hue_lights/cities.json', 'r') as f:
        cities = f.read()
    return cities


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


@app.route("/load_all_settings_status", methods=["GET"])
def load_all_settings():
    if dotenv.get_key(".env", "USERNAME") is None:
        return jsonify({"message": "Please press the button on the Hue Bridge"})
    if dotenv.get_key(".env", "IP_ADDR") is None:
        return jsonify({"message": "Looking for the Hue Bridge IP address"})
    if dotenv.get_key(".env", "CITY") is None:
        return jsonify({"message": "Please set the city"})
    if dotenv.get_key(".env", "MAC_ADDR") is None:
        return jsonify({"message": "Looking for the Hue Bridge MAC address"})
    return jsonify({"message": "Done"})


@app.route("/reconnect", methods=["GET"])
def reset_settings():
    dotenv.set_key(".env", "USERNAME", None)
    dotenv.set_key(".env", "IP_ADDR", None)
    dotenv.set_key(".env", "CITY", None)
    dotenv.set_key(".env", "MAC_ADDR", None)
    with open(".env", "w") as f:
        f.write("")
    get_bridge_ip_addr()
    get_bridge_username()
    get_current_city()
    get_bridge_mac_addr()
    return jsonify({"message": "Settings reset"})


if __name__ == "__main__":
    CORS(app)
    app.run(host="0.0.0.0", port=5555, debug=True)
