# AI 快讯抓取器

每隔 30 分钟通过 GitHub Actions 抓取 [baipiao.org AI 快讯](https://baipiao.org/news/) 第一页内容，提取每条新闻的原文链接、标题和简介，自动去重后提交到 `news_data.json`。

## 运行方式

- 定时任务：`schedule` 每 30 分钟触发一次（`.github/workflows/scrape.yml`）
- 手动触发：仓库 Actions 页面点击 "Run workflow"

## 数据文件

`news_data.json` 保存所有抓取到的去重新闻，字段：

| 字段 | 说明 |
| --- | --- |
| id | 新闻唯一 ID（用于去重） |
| title | 标题 |
| url | 原文链接 |
| summary | 简介 |
| source | 来源 |
| date | 发布时间，格式：`某年某月某日某时某分` |

## 本地运行

```bash
python scraper.py
```
