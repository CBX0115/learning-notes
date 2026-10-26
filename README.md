# 学习笔记

记录学习过程中的练习项目与笔记。

## 项目列表

| 项目 | 说明 | 技术栈 |
|------|------|--------|
| [weibo-baekhyun-crawler](./weibo-baekhyun-crawler/) | 微博关键词爬虫，抓取指定关键词的近期动态并生成结构化数据 | Python · requests · BeautifulSoup |

## 目录结构

```
learning-notes/
└── weibo-baekhyun-crawler/
    ├── baekhyun_crawler.py   # 爬虫主脚本
    ├── requirements.txt      # 依赖清单
    ├── .gitignore            # 排除凭证与抓取结果
    └── README.md             # 项目说明
```

> 各项目内的登录凭证（如 `cookie.txt`）不会提交到仓库，需自行在本地创建。
