import os
import platform
import re
import subprocess
from typing import Optional

import requests
from dotenv import load_dotenv
from ssdpy import SSDPClient

load_dotenv()

MAC_ADDR = os.environ.get("MAC_ADDR", None)
IP_ADDR = os.environ.get("IP_ADDR", None)
USERNAME = os.environ.get("USERNAME", None)

IP_REGEX_PATTERN = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
MAC_REGEX_PATTERN = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"


def scan_hue_bridge_ip_addr() -> str:
    """
    Scan the network to find the hue bridge address with ssdp

    Returns:
        str: The hue bridge address
    """
    client = SSDPClient()
    while True:
        for _ in client.m_search("ssdp:all"):
            if "Hue" in _["server"]:
                ip_addr = re.search(IP_REGEX_PATTERN, _["location"]).group()
                return ip_addr


def ip_mac_finder(mac_addr: Optional[str] = None, ip_addr: Optional[str] = None) -> str:
    """
    Searches for an IP address or MAC address in the ARP table of the current system.

    This function executes a system command to retrieve the ARP table and then searches it
    for either a specified MAC address or IP address. It's compatible with both Linux and Windows
    operating systems, adjusting the command used based on the OS.

    Parameters:
    mac_addr (Optional[str]): The MAC address to search for in the ARP table. Should be in standard
                            MAC address format (e.g., '00:1A:2B:3C:4D:5E'). If None, the function
                            will search using the provided IP address instead.
    ip_addr (Optional[str]):  The IP address to search for in the ARP table. Should be in standard
                            IPv4 format (e.g., '192.168.1.1'). If None, the function will search
                            using the provided MAC address instead.

    Returns:
    str: The matched IP or MAC address from the ARP table. Returns an empty string if no match
        is found or if both mac_addr and ip_addr are None.

    Note:
    This function requires appropriate system permissions to execute ARP table commands.
    Also, it assumes the existence of IP_REGEX_PATTERN and MAC_REGEX_PATTERN as global
    variables for regex patterns of IP and MAC addresses respectively.
    """
    if not (ip_addr or mac_addr):
        raise ValueError("Either an IP address or a MAC address must be provided.")

    os_type = platform.system().lower()
    arp_command = "ip neigh" if os_type == "linux" else "arp"
    grep_command = "findstr" if os_type == "windows" else "grep -w"

    # ping before arp scan to make sure the device is in the arp table
    if ip_addr:
        if os_type != "windows":
            subprocess.run(
                f"ping -c 1 {ip_addr}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                f"ping -n 1 {ip_addr}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    output = subprocess.check_output(
        f"{arp_command} {'-a' if (os_type != 'linux' and not ip_addr) else ''} {(ip_addr or '') if os_type != 'linux' else ''} "
        f"| {grep_command} '{mac_addr or ip_addr}'",
        shell=True,
    ).decode()

    res = re.search(
        IP_REGEX_PATTERN if mac_addr is not None else MAC_REGEX_PATTERN, output
    )
    if res:
        return res.group()
    else:
        return ""


def add_to_env_file(*args) -> None:
    """
    Appends multiple key-value pairs to the '.env' file.

    This function takes variable arguments, each being a tuple of a key and its corresponding value.
    It writes each pair in the format 'KEY=VALUE' to the '.env' file located in the current directory.
    If the '.env' file doesn't exist, it will be created. Each key-value pair is written on a new line.

    Parameters:
    *args: Variable length argument list. Each argument should be a tuple where the first element
           is the key (str) and the second element is the value (str).

    Returns:
    None

    Example:
    add_to_env_file(("DB_HOST", "localhost"), ("DB_USER", "root"))

    This will add the lines:
    DB_HOST=localhost
    DB_USER=root
    to the '.env' file.
    """
    # Create the .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w"):
            pass
    # if the key already exists, remove it
    with open(".env", "r") as f:
        lines = f.readlines()
    with open(".env", "w") as f:
        for line in lines:
            if not any(line.startswith(f"{key}=") for key, _ in args):
                f.write(line)
    # Add the new key-value pairs
    with open(".env", "a") as f:
        for key, value in args:
            f.write(f"{key}={value}\n")


def get_hue_bridge_ip_addr() -> str:
    """
    Retrieves the IP address of the Hue Bridge.

    This function first checks if a MAC address is already defined (assumed to be stored in
    a global variable 'MAC_ADDR'). If not, it scans for the Hue Bridge IP address, finds the
    corresponding MAC address, stores it in the '.env' file for future reference, and then returns
    the discovered IP address. If a MAC address is already available, it uses it to find the
    associated IP address.

    Returns:
    str: The IP address of the Hue Bridge.
    """
    if MAC_ADDR is None:
        ip_addr = scan_hue_bridge_ip_addr()
        mac_addr = ip_mac_finder(ip_addr=ip_addr)
        add_to_env_file(("MAC_ADDR", mac_addr))
        add_to_env_file(("IP_ADDR", ip_addr))
        return ip_addr

    if IP_ADDR is None:
        ip_addr = ip_mac_finder(mac_addr=MAC_ADDR)
        add_to_env_file(("IP_ADDR", ip_addr))
        return ip_addr

    if ip_mac_finder(ip_addr=IP_ADDR) == MAC_ADDR:
        return IP_ADDR
    else:
        ip_addr = ip_mac_finder(mac_addr=MAC_ADDR)
        add_to_env_file(("IP_ADDR", ip_addr))
        return ip_addr


def get_hue_bridge_username() -> str:
    """
    Retrieves the username of the Hue Bridge.

    This function first checks if a username is already defined (assumed to be stored in
    a global variable 'USERNAME'). If not, it attempts to create a new username and store it
    in the '.env' file for future reference. If a username is already available, it returns it.

    Returns:
    str: The username of the Hue Bridge.
    """
    if USERNAME is None:
        print("Press the button on the Hue Bridge")
        username = requests.post(
            f"http://{get_hue_bridge_ip_addr()}/api",
            json={"devicetype": "red_alert"},
        ).json()[0]
        if "error" in username:
            raise Exception(username["error"]["description"])
        username = username["success"]["username"]
        add_to_env_file(("USERNAME", username))
        return username
    else:
        return USERNAME
