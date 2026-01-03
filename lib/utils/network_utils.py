from typing import Dict, Optional
from urllib.parse import urlencode

import httpx
import requests
import random


USER_AGENT = None  # will be set by get_random_user_agent()


def get_random_user_agent() -> str:
    global USER_AGENT
    platforms = [
        "Windows NT 10.0; Win64",
        "Macintosh; Intel Mac OS X 10_15",
        "X11; Linux x86_64",
    ]
    platform = random.choice(platforms)
    version = random.uniform(80, 110)
    browsers = [
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version:.3f} Safari/537.36",
        f"Gecko/20100101 Firefox/{version:.3f}",
    ]
    USER_AGENT = f"Mozilla/5.0 ({platform}) {random.choice(browsers)}"
    return USER_AGENT


# Initialize a random UA once per process
USER_AGENT = get_random_user_agent()


async def http_get(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    default_headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
    }
    if headers:
        default_headers.update(headers)
    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        response = await client.get(url, headers=default_headers)
        response.raise_for_status()
        return response.text


async def http_post(url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> str:
    default_headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if headers:
        default_headers.update(headers)
    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        response = await client.post(url, data=data, headers=default_headers)
        response.raise_for_status()
        return response.text


def get_json(url: str, headers: Dict[str, str]):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_query_string(name: str, url: str) -> str:
    for part in url.replace("?", "&").split("&"):
        if not part:
            continue
        key, _, value = part.partition("=")
        if key == name:
            return value
    return ""


def get_random_string(length: int) -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def to_query_string(params: Dict[str, str]) -> str:
    return urlencode(sorted(params.items()))
