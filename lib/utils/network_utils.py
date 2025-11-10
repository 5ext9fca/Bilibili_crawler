from typing import Dict
import requests


def get_json(url: str, headers: Dict[str, str]):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()
