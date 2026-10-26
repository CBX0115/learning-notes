# -*- coding: utf-8 -*-
"""
爬取微博超话/话题中"边伯贤"的近期动态（示例脚本）
依赖安装: pip install requests beautifulsoup4
注意:
  - 微博接口可能随版本调整，若报错请重新抓包获取 containerid
  - 仅供学习使用，请控制请求频率，遵守 robots.txt 与平台条款
"""
import time
import json
import random
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Referer": "https://m.weibo.cn/",
    # 大部分接口不登录可用；若被限制，登录后从浏览器复制 Cookie 填到下面
    # "Cookie": "SUB=xxxx; SUBP=xxxx;",
}

API = "https://m.weibo.cn/api/container/getIndex"

# ====================================================================
# Cookie 获取方法（只需一次，有效期通常几周）：
#   1. 电脑 Chrome 打开 m.weibo.cn 并登录（这就是"手机版网页"，仍在电脑上操作）
#   2. F12 -> Network -> 勾选 Fetch/XHR -> 按 F5 刷新
#   3. 点任一 getIndex 请求 -> Headers -> Request Headers -> 复制 Cookie 整行
#   4. 粘贴到本脚本同目录下的 cookie.txt 文件里（直接新建 txt，粘一行就行）
# 优先级：cookie.txt > 环境变量 WEIBO_COOKIE > 下面的 COOKIE 变量
# ====================================================================
COOKIE = ""  # 例如: "SUB=xxx; SUBP=xxx; XSRF-TOKEN=xxx;"

# 搜索"边伯贤"相关微博的 containerid（type=1 表示实时微博搜索）
CONTAINER_ID = "100103type=1&q=边伯贤"


def load_cookie() -> str:
    """按 cookie.txt -> 环境变量 -> COOKIE 变量的顺序读取 Cookie"""
    import os
    from pathlib import Path

    cookie_file = Path(__file__).with_name("cookie.txt")
    if cookie_file.exists():
        # 忽略以 # 开头的说明行，只取真正的 Cookie 内容
        lines = [
            ln.strip() for ln in cookie_file.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        text = " ".join(lines)
        # 兼容直接粘贴整行 "Cookie: xxx" 的情况
        if text.lower().startswith("cookie:"):
            text = text[7:].strip()
        if text:
            return text
    return os.environ.get("WEIBO_COOKIE", "").strip() or COOKIE


def fetch_page(page: int) -> dict:
    """抓取一页搜索结果"""
    cookie = load_cookie()
    if not cookie:
        raise RuntimeError("未找到 Cookie。请在脚本同目录新建 cookie.txt，把浏览器里的 Cookie 粘进去。")
    HEADERS["Cookie"] = cookie
    params = {"containerid": CONTAINER_ID, "page_type": "searchall", "page": page}
    resp = requests.get(API, headers=HEADERS, params=params, timeout=10)
    if resp.status_code in (418, 432, 403):
        raise RuntimeError(
            f"被微博风控拦截（状态码 {resp.status_code}）。请重新登录微博、更新 cookie.txt 里的 Cookie。"
        )
    try:
        return resp.json()
    except ValueError:
        snippet = resp.text[:200].replace("\n", " ")
        raise RuntimeError(
            f"返回的不是 JSON（状态码 {resp.status_code}）。返回内容开头：{snippet}"
        )


def parse_cards(data: dict) -> list:
    """从返回的 JSON 中提取每条微博的关键信息"""
    results = []
    cards = data.get("data", {}).get("cards", [])
    for card in cards:
        # 搜索结果可能嵌套在 card_group 里
        groups = card.get("card_group") or [card]
        for g in groups:
            mblog = g.get("mblog")
            if not mblog:
                continue
            user = mblog.get("user", {})
            results.append({
                "时间": mblog.get("created_at", ""),
                "用户": user.get("screen_name", ""),
                "认证": user.get("verified_reason", "") or ("V" if user.get("verified") else ""),
                "内容": mblog.get("text", ""),           # 含 HTML 标签
                "点赞": mblog.get("attitudes_count", 0),
                "评论": mblog.get("comments_count", 0),
                "转发": mblog.get("reposts_count", 0),
                "链接": f"https://m.weibo.cn/status/{mblog.get('bid', '')}",
            })
    return results


def clean_html(text: str) -> str:
    """去掉内容里的 HTML 标签"""
    from bs4 import BeautifulSoup
    return BeautifulSoup(text, "html.parser").get_text(strip=True)


def main(pages: int = 3):
    print(f"Cookie 状态: {'已读取（长度 %d）' % len(load_cookie()) if load_cookie() else '未配置 → 请新建 cookie.txt'}")
    all_posts = []
    for page in range(1, pages + 1):
        print(f"正在抓取第 {page} 页 ...")
        try:
            data = fetch_page(page)
        except RuntimeError as e:
            print(f"  第 {page} 页失败: {e}")
            break
        posts = parse_cards(data)
        if not posts:
            print("  本页无更多数据，停止")
            break
        for p in posts:
            p["内容"] = clean_html(p["内容"])
        all_posts.extend(posts)
        # 随机延时 2~4 秒，避免请求过快被封
        time.sleep(random.uniform(2, 4))

    # 按点赞数排个序，方便看热点
    all_posts.sort(key=lambda x: x["点赞"], reverse=True)

    with open("baekhyun_weibo.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"\n共抓到 {len(all_posts)} 条动态，已保存到 baekhyun_weibo.json\n")
    for p in all_posts[:5]:
        print(f"[{p['时间']}] {p['用户']}: {p['内容'][:50]}...  👍{p['点赞']}")


if __name__ == "__main__":
    main(pages=3)
