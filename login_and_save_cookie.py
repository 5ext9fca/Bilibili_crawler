"""Scan Bilibili QR login, fetch cookies, and persist them to config.json."""
from lib.utils.login_utils import CONFIG_PATH, login_and_save_cookie


def main() -> None:
    if login_and_save_cookie():
        print(f"已写入 {CONFIG_PATH}，可直接运行爬虫。")
    else:
        print("未获取到Cookie，未更新配置。")


if __name__ == "__main__":
    main()
