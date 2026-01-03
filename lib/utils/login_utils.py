"""Utilities for logging into Bilibili and storing cookies in config.json."""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import qrcode

from lib.utils import extract_bili_jct, merge_config
from lib.utils.file_utils import load_json_config
from lib.utils.network_utils import (
    http_get,
    get_query_string, get_random_string, to_query_string,
)
from lib.utils.platform_utils import get_sign
from lib.utils.time_utils import get_timestamp

CONFIG_PATH = Path("config.json")
DEFAULT_LOGIN_DIR = Path("data/login")


def get_login_data_dir(config_path: Path = CONFIG_PATH) -> Path:
    config = load_json_config(str(config_path)) or {}
    return Path(config.get("login_data_dir", DEFAULT_LOGIN_DIR))


def get_tv_login_params() -> Dict[str, str]:
    now = datetime.now()
    device_id = get_random_string(20)
    buvid = get_random_string(37)
    fingerprint = now.strftime("%Y%m%d%H%M%S%f")[:-3] + get_random_string(45)
    params = {
        "appkey": "4409e2ce8ffd12b8",
        "auth_code": "",
        "bili_local_id": device_id,
        "build": "102801",
        "buvid": buvid,
        "channel": "master",
        "device": "OnePlus",
        "device_id": device_id,
        "device_name": "OnePlus7TPro",
        "device_platform": "Android10OnePlusHD1910",
        "fingerprint": fingerprint,
        "guid": buvid,
        "local_fingerprint": fingerprint,
        "local_id": buvid,
        "mobi_app": "android_tv_yst",
        "networkstate": "wifi",
        "platform": "android",
        "sys_ver": "29",
        "ts": get_timestamp(True),
    }
    params["sign"] = get_sign(to_query_string(params))
    return params


# ---------- Login implementation ----------

class BilibiliLogin:
    WEB_QRCODE_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header"
    WEB_QRCODE_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    TV_AUTH_CODE_URL = "https://passport.snm0516.aisee.tv/x/passport-tv-login/qrcode/auth_code"
    TV_POLL_URL = "https://passport.bilibili.com/x/passport-tv-login/qrcode/poll"

    def __init__(self, save_dir: Optional[Path] = None, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.save_dir = save_dir or get_login_data_dir(config_path)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _generate_qrcode(self, url: str, filename: str = "qrcode.png") -> None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qrcode_path = self.save_dir / filename
        img.save(qrcode_path)
        print(f"生成二维码成功: {qrcode_path}, 请打开并扫描")
        self._print_qrcode_terminal(url)

    def _print_qrcode_terminal(self, url: str) -> None:
        qr = qrcode.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)

    async def _get_web_login_status(self, qrcode_key: str) -> Dict:
        query_url = f"{self.WEB_QRCODE_POLL_URL}?qrcode_key={qrcode_key}&source=main-fe-header"
        response = await http_get(query_url)
        return json.loads(response)

    async def login_web(self) -> Tuple[bool, Optional[str]]:
        try:
            print("获取登录地址...")
            response = await http_get(self.WEB_QRCODE_GENERATE_URL)
            data = json.loads(response)
            url = data["data"]["url"]
            qrcode_key = get_query_string("qrcode_key", url)
            print("生成二维码...")
            self._generate_qrcode(url)
            flag = False
            while True:
                await asyncio.sleep(1)
                status_data = await self._get_web_login_status(qrcode_key)
                code = status_data["data"]["code"]
                if code == 86038:
                    print("二维码已过期, 请重新执行登录指令.")
                    return False, "二维码已过期"
                if code == 86101:
                    continue
                if code == 86090:
                    if not flag:
                        print("扫码成功, 请确认...")
                        flag = True
                    continue
                url_with_params = status_data["data"]["url"]
                sessdata = get_query_string("SESSDATA", url_with_params)
                print(f"登录成功: SESSDATA={sessdata}")
                cookie_str = url_with_params[url_with_params.index("?") + 1 :]
                cookie_str = cookie_str.replace("&", ";").replace(",", "%2C")
                data_file = self.save_dir / "BBDown.data"
                with open(data_file, "w", encoding="utf-8") as f:
                    f.write(cookie_str)
                qrcode_file = self.save_dir / "qrcode.png"
                if qrcode_file.exists():
                    qrcode_file.unlink()
                return True, sessdata
        except Exception as e:
            print(f"登录失败: {e}")
            return False, str(e)

    def get_saved_cookie(self, login_type: str = "web") -> Optional[str]:
        data_file = self.save_dir / ("BBDown.data" if login_type == "web" else "BBDownTV.data")
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        return None


async def fetch_web_cookies(
    data_dir: Optional[Path] = None,
    config_path: Path = CONFIG_PATH,
    allow_cached: bool = True,
) -> Optional[str]:
    login = BilibiliLogin(save_dir=data_dir, config_path=config_path)
    if allow_cached:
        cached = login.get_saved_cookie()
        if cached:
            return cached
    success, _ = await login.login_web()
    if not success:
        return None
    return login.get_saved_cookie()


def login_and_save_cookie(
    config_path: Path = CONFIG_PATH,
    data_dir: Optional[Path] = None,
    allow_cached: bool = True,
) -> bool:
    cookies_str = asyncio.run(
        fetch_web_cookies(data_dir=data_dir or get_login_data_dir(config_path), config_path=config_path, allow_cached=allow_cached)
    )
    if not cookies_str:
        return False
    bili_jct = extract_bili_jct(cookies_str)
    return merge_config(cookies_str, bili_jct, config_path=config_path)
