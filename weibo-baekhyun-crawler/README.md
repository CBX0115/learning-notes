# 微博关键词爬虫（以"边伯贤"为例）

一个用于学习网络爬虫原理的示例项目：抓取微博搜索结果中指定关键词的近期动态，解析为结构化数据并生成可视化汇总页。

## 功能

- 调用微博手机版 `getIndex` 接口，按关键词分页抓取动态
- 提取字段：发布时间、用户名、认证信息、正文、点赞/评论/转发数、原帖链接
- 自动清除正文中的 HTML 标签
- 请求间隔随机延时（2~4 秒），避免触发风控
- 输出 JSON 数据文件，可进一步生成 HTML 汇总页

## 目录结构

```
.
├── baekhyun_crawler.py    # 主爬虫脚本
├── cookie.txt             # 登录凭证（本地创建，已被 .gitignore 排除）
├── requirements.txt       # 依赖清单
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Cookie

微博搜索接口需要登录状态，否则会被风控拦截（返回 432）。

1. 电脑浏览器打开 <https://m.weibo.cn> 并登录
2. 按 `F12` 打开开发者工具 → `Network` 面板 → 勾选 `Fetch/XHR`
3. 按 `F5` 刷新页面，点击任意 `getIndex` 请求
4. 在 `Headers → Request Headers` 中找到 `Cookie`，复制整行内容
5. 粘贴到项目根目录的 `cookie.txt` 中（以 `#` 开头的说明行会被自动忽略）

> Cookie 有时效性（通常数周），失效后重新获取即可。脚本不会把 Cookie 提交到仓库。

### 3. 运行

```bash
python baekhyun_crawler.py
```

运行结束后生成 `baekhyun_weibo.json`。

## 修改抓取目标

编辑 `baekhyun_crawler.py`：

```python
CONTAINER_ID = "100103type=1&q=边伯贤"   # 改 q= 后面的关键词即可
```

抓取页数在文件末尾的 `main(pages=3)` 中调整。

## 技术要点

| 环节 | 实现 |
|------|------|
| 请求 | `requests`，自定义 User-Agent 模拟移动端浏览器 |
| 解析 | 直接消费接口返回的 JSON，无需解析 HTML |
| 清洗 | `BeautifulSoup` 去除正文标签 |
| 反爬应对 | 携带登录 Cookie + 随机延时 |
| 存储 | JSON 文件 |

## 免责声明

本项目仅用于学习网络爬虫技术。请遵守目标网站的 `robots.txt` 与服务条款，控制请求频率，不得用于商业用途或侵犯他人隐私。抓取内容的版权归原作者所有。
