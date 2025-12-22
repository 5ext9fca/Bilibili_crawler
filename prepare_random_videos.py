#!/usr/bin/env python3
"""
根据B站热门视频随机挑选N个视频，生成 user/random_N.csv
默认随机选择10个（可通过命令行参数 --count 调整）
无需登录配置，使用公开热门接口。
"""
import argparse
import csv
import os
import random
import sys
import time
from typing import List, Dict

import requests

POPULAR_API = "https://api.bilibili.com/x/web-interface/popular"
DEFAULT_PAGES = 6  # 每页最多20条，抓取6页≈120条做候选池
PAGE_SIZE = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def fetch_popular_page(pn: int, ps: int = PAGE_SIZE) -> List[Dict]:
    """拉取一页热门视频列表，返回视频项列表。"""
    params = {"pn": pn, "ps": ps}
    resp = requests.get(POPULAR_API, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"popular接口返回错误: {data.get('message')}")
    return data.get("data", {}).get("list", [])


def collect_candidates(pages: int = DEFAULT_PAGES) -> List[Dict]:
    """收集若干页热门视频作为候选池。"""
    pool: List[Dict] = []
    for pn in range(1, pages + 1):
        try:
            items = fetch_popular_page(pn)
            # 过滤缺失字段的项
            for it in items:
                if "aid" in it and "bvid" in it and "title" in it:
                    pool.append({
                        "aid": it["aid"],
                        "bvid": it["bvid"],
                        "title": it["title"],
                        "owner": (it.get("owner") or {}).get("name", "")
                    })
        except Exception as e:
            print(f"第{pn}页popular抓取失败: {e}")
        time.sleep(random.uniform(0.2, 0.4))
    return pool


def write_user_csv(rows: List[Dict], out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # 与批量爬虫约定的表头：comment_id_str, comment_type
        w.writerow(["comment_id_str", "comment_type"])
        for it in rows:
            # 批量爬虫对视频需要AV号（aid）+ type=1
            w.writerow([str(it["aid"]), 1])


def main():
    parser = argparse.ArgumentParser(description="从B站热门视频随机挑选N个，生成批量爬取清单CSV")
    parser.add_argument("--count", type=int, default=10, help="随机选择的视频数量，默认10")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES, help="抓取热门的页数（每页~20条），默认6页")
    parser.add_argument("--out", type=str, default=None, help="输出CSV路径，默认 user/random_<N>.csv")
    args = parser.parse_args()

    n = max(1, args.count)
    pool = collect_candidates(args.pages)
    if not pool:
        print("未能获取热门视频列表，请稍后重试")
        sys.exit(2)

    if len(pool) < n:
        print(f"候选池数量不足，仅有{len(pool)}个，直接全部使用")
        chosen = pool
    else:
        chosen = random.sample(pool, n)

    out_path = args.out or os.path.join("data/user", f"random_{len(chosen)}.csv")
    write_user_csv(chosen, out_path)

    print("已生成批量清单:", out_path)
    print("示例（前3个）：")
    for it in chosen[:3]:
        print(f"  aid={it['aid']}  bvid={it['bvid']}  title={it['title']}")
    print("接下来可运行: python Bilibili_crawler.py 进行批量爬取")


if __name__ == "__main__":
    main()
