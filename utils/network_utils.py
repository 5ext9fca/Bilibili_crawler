import requests


def get_json(headers: dict[str, str], url: str):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()
