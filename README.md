# Bilibili_crawler

> **基于 Bilibili API 的评论爬取与登录工具集**  
> 支持视频/动态评论批量爬取（主评+楼中楼）、用户动态抓取、数据分析，以及 Web/TV 二维码登录；已完成模块化与面向对象重构。

---

## 📋 项目简介
- ✅ 爬取视频评论（BV/AV 均可）与动态评论，支持主评与楼中楼，自动处理置顶评论
- ✅ 批量爬取：读取 `data/user/` 任务文件，顺序执行
- ✅ 断点恢复：可用记录文件手动续爬
- ✅ 数据分析：时间/IP/等级/性别分布、热力图等
- ✅ 工具：BV/AV 互转、用户空间动态列表抓取
- ✅ 登录模块：Web/TV 二维码登录，自动生成二维码并保存凭证

> ⚠️ 长整型 UID/RPID 在 Excel 中会被转为科学计数法，**不要直接保存**；导入时将对应列设为文本，或用 `pandas.read_csv(..., dtype={'uid': str, 'rpid': str})`。

---

## 🚀 快速开始
> 仓库使用 `uv` 管理依赖，文件行尾统一 LF。Windows 建议：
> ```powershell
> git config --global core.autocrlf false
> git config --global core.eol lf
> ```

### 1️⃣ 安装依赖
```bash
uv sync
```
常用依赖：`httpx`, `requests`, `pandas`, `matplotlib`, `seaborn`, `pytz`, `qrcode[pil]`, `Pillow`。

### 2️⃣ 配置 `config.json`
```json
{
  "cookies_str": "写入您的cookies",
  "bili_jct": "cookie中的bili_jct",
  "ps": "20",
  "start": 1,
  "end": 99999,
  "oid": "可选：单目标 ID",
  "type": 1,
  "file_path_1": "comments/主评论.csv",
  "file_path_2": "comments/子评论.csv",
  "file_path_3": "comments/总评论.csv",
  "down": 1,
  "up": 100
}
```
- `type`: 1=视频，11=图文动态，17=转发/文字动态。
- 推荐用登录模块获取最新 cookie 再填入。

### 3️⃣ 获取 Cookie 快速指引
1. 浏览器登录 B 站，F12 打开 Network，刷新评论区
2. 找到 `main?oid=` 请求，在 Headers 中复制 `Cookie` 到 `cookies_str`
3. 从 Cookie 中取 `bili_jct`

---

## 📦 项目结构（重构版）
```
Bilibili_crawler/
├── lib/
│   ├── core/        # 配置、API 客户端、爬虫调度
│   ├── utils/       # 时间/文件/登录/网络等工具
│   ├── models/      # 数据模型
│   └── analyzers/   # 评论分析
├── Bilibili_crawler.py       # 批量爬虫入口（读 data/user/）
├── simple_crawler.py         # 单目标爬虫入口
├── bili_user_space.py        # 获取用户空间动态列表
├── common_func.py            # 数据分析脚本
├── bv2oid.py                 # BV/AV 转换
├── wbi_sign_crawler.py       # WBI 签名示例
├── login_and_save_cookie.py  # 独立登录脚本（Web/TV）
├── config.json
└── data/ (comments/, user/, login/)
```

### 架构要点
- **职责分离**：`ConfigManager` 统一配置；`BilibiliApiClient` 封装 API；`BilibiliCrawler` 调度流程
- **模块化**：`utils`/`models`/`core`/`analyzers` 分层复用
- **日志与错误**：统一日志、异常处理、进度记录
- **配置验证**：参数校验与默认值提示
- **性能与安全**：连接复用、随机延迟（0.2–0.4s）、防重复请求、基础缓存

---

## 📖 使用教程
### 方式一：按用户批量爬取
1. 获取动态列表（生成任务文件）
```bash
python bili_user_space.py
```
按提示输入 UID，输出 `data/user/{uid}.csv`（含 comment_id_str、comment_type）。

2. 批量爬评论
```bash
python Bilibili_crawler.py
```
自动读取 `data/user/` 下任务，输出至 `data/comments/`（主评/子评/合并）。

### 方式二：单个视频/动态爬取
1. 在 `config.json` 写入目标 `oid` 与 `type`
2. 运行
```bash
python simple_crawler.py
```

### 方式三：WBI 签名示例
```bash
python wbi_sign_crawler.py
```
按脚本注释修改 `oid` 后运行。

### 数据分析
1. 将目标评论 CSV 重命名为 `data.csv` 放项目根目录
2. 运行
```bash
python common_func.py
```
输出：`nickname_counts.csv`、时间分布图（分钟/小时）、`top_25_ip_pie_chart.png`、`level_pie_chart.png`、`gender_pie_chart.png`、`level_likes_heatmap.png`。

### BV/AV 转换
```bash
python bv2oid.py
```
支持单个或批量双向转换。

---

## 🔐 登录模块
- 支持 Web 与 TV 二维码登录，自动生成 PNG 与终端二维码
- 登录后保存：Web → `BBDown.data`（完整 Cookie），TV → `BBDownTV.data`（AccessToken）
- 可独立运行 `login_and_save_cookie.py`，或在代码中复用 `BilibiliLogin`

#### Web 登录示例
```python
import asyncio
from lib.utils.login_utils import BilibiliLogin

async def main():
    login = BilibiliLogin()
    success, result = await login.login_web()
    if success:
        print(f"登录成功，SESSDATA: {result}")
        print(login.get_saved_cookie(login_type="web"))
    else:
        print(f"登录失败: {result}")

asyncio.run(main())
```

#### TV 登录示例
```python
import asyncio
from lib.utils.login_utils import BilibiliLogin

async def main():
    login = BilibiliLogin()
    success, result = await login.login_tv()
    if success:
        print(f"登录成功，AccessToken: {result}")
        print(login.get_saved_cookie(login_type="tv"))
    else:
        print(f"登录失败: {result}")

asyncio.run(main())
```

---

## 📌 常见问题
- **中断恢复**：将生成的记录文件移至 `data/user/`，删除原任务文件后重跑，已完成部分会跳过。
- **Excel 科学计数法**：导入时将 `uid/rpid` 设为文本，或用 pandas 指定 dtype。
- **重复数据**：API 懒加载可能重复，分析前去重。
- **防封策略**：已内置 0.2–0.4s 随机延迟，可酌情加大。
- **凭证过期**：重新扫码登录，更新 `cookies_str` 与 `bili_jct`。

---

## ⚠️ 免责声明
- 仅供学习交流，请遵守 B 站用户协议及相关法律法规，勿用于商业用途
- 勿高频、大规模爬取，避免对服务器造成压力
- 凭证文件含敏感信息，请妥善保管；由使用本工具产生的责任由使用者自行承担

---

## 📝 开发与致谢
- 登录代码移植自 [BBDown](https://github.com/nilaoda/BBDown)
- MIT 许可证，详见 `LICENSE`
- 如果本项目对你有帮助，欢迎点 Star ⭐ 与提交 Issue/PR

**最后更新时间**：2026-01-02
