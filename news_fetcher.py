#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻获取模块

从多个AI资讯来源获取最新新闻，包括RSS源和网页爬虫。
"""

import logging
import json
import time
import random
import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

# 配置日志
logger = logging.getLogger(__name__)

# 定义RSS源列表
RSS_SOURCES = [
    # OpenAI Blog无法访问，暂时移除
    # {
    #     "name": "OpenAI Blog",
    #     "url": "https://openai.com/blog/rss",
    #     "category": "ai_company"
    # },
    {
        "name": "DeepMind",
        "url": "https://deepmind.com/blog/feed/basic",  # 使用备用URL作为主URL
        "category": "ai_company"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "tech_news"
    },
    {
        "name": "Reddit AI",
        "url": "https://www.reddit.com/r/artificial/.rss",
        "category": "community"
    },
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
        "category": "tech_news"
    },
    # 新增RSS源
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "tech_news"
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "category": "ai_company"
    },
    {
        "name": "MIT News AI",
        "url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
        "category": "research"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "tech_news"
    },
    {
        "name": "Towards Data Science",
        "url": "https://towardsdatascience.com/feed",
        "category": "research"
    },
    {
        "name": "AI Trends",
        "url": "https://www.aitrends.com/feed/",
        "category": "tech_news"
    },
    # Anthropic没有公开的RSS源，暂时移除
    # {
    #     "name": "Anthropic Blog",
    #     "url": "https://www.anthropic.com/blog/rss.xml",
    #     "category": "ai_company",
    #     "backup_url": "https://www.anthropic.com/blog/feed"
    # },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "ai_company"
    },
    {
        "name": "The AI Track",
        "url": "https://theaitrack.com/feed/",
        "category": "tech_news"
    },
    {
        "name": "AI News Daily",
        "url": "https://ainewsdaily.com/feed/",
        "category": "tech_news"
    },
    {
        "name": "Analytics Vidhya",
        "url": "https://www.analyticsvidhya.com/feed/",
        "category": "research"
    },
    {
        "name": "KDnuggets",
        "url": "https://www.kdnuggets.com/feed",
        "category": "research"
    },
    {
        "name": "Distill.pub",
        "url": "https://distill.pub/rss.xml",
        "category": "research"
    }
]

# 定义网页爬虫源
WEB_SOURCES = [
    # The Verge AI无法正常爬取，暂时移除
    # {
    #     "name": "The Verge AI",
    #     "url": "https://www.theverge.com/ai-artificial-intelligence",
    #     "category": "tech_news"
    # },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/tag/artificial-intelligence/",
        "category": "tech_news"
    },
    # Forbes AI无法正常爬取，暂时移除
    # {
    #     "name": "Forbes AI",
    #     "url": "https://www.forbes.com/sites/artificial-intelligence/",
    #     "category": "tech_news",
    #     "selector": {
    #         "article": "div.stream-item",
    #         "title": "h2.stream-item__title",
    #         "link": "a.stream-item__title",
    #         "summary": "div.stream-item__description",
    #         "date": "time.stream-item__date"
    #     }
    # },
    {
        "name": "NVIDIA AI News",
        "url": "https://blogs.nvidia.com/blog/category/deep-learning/",
        "category": "ai_company",
        "selector": {
            "article": "article.blog-item",
            "title": "h2.blog-item__title",
            "link": "a.blog-item__title-link",
            "summary": "div.blog-item__excerpt",
            "date": "time.blog-item__date"
        }
    },
    {
        "name": "AI News",
        "url": "https://artificialintelligence-news.com/",
        "category": "tech_news",
        "selector": {
            "article": "article.type-post",
            "title": "h2.entry-title",
            "link": "h2.entry-title a",
            "summary": "div.entry-content",
            "date": "time.entry-date"
        }
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/",
        "category": "tech_news",
        "selector": {
            "article": "article.article-item",
            "title": "h2.article-title",
            "link": "a.article-link",
            "summary": "p.article-excerpt",
            "date": "time.article-date"
        }
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "category": "tech_news",
        "selector": {
            "article": "div.cardItem___3V2v3",
            "title": "h3.cardItemTitle___2yCF8",
            "link": "a.cardItemTitle___2yCF8",
            "summary": "p.cardItemDescription___3JhZl",
            "date": "time"
        }
    }
]

# 用户代理列表，避免被网站封锁
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/96.0.4664.53 Mobile/15E148 Safari/604.1"
]


def get_random_user_agent() -> str:
    """返回随机用户代理字符串"""
    return random.choice(USER_AGENTS)


def parse_date(date_str: str) -> str:
    """
    解析日期字符串为标准格式 (YYYY-MM-DD)
    
    Args:
        date_str: 日期字符串
        
    Returns:
        标准格式的日期字符串
    """
    try:
        dt = date_parser.parse(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"日期解析失败: {date_str}, 错误: {str(e)}")
        return datetime.now().strftime("%Y-%m-%d")  # 默认使用当前日期


def fetch_from_rss(source: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    从RSS源获取新闻
    
    Args:
        source: RSS源信息，包含name和url
        
    Returns:
        新闻列表，每条新闻包含title, summary, link, published_date
    """
    news_list = []
    
    try:
        logger.info(f"正在从 {source['name']} 获取RSS新闻")
        
        # 添加用户代理和超时设置
        headers = {'User-Agent': get_random_user_agent()}
        
        # 尝试使用主URL获取RSS
        try:
            # 先尝试直接请求RSS URL，检查是否可访问
            response = requests.get(source["url"], headers=headers, timeout=10)
            response.raise_for_status()  # 如果状态码不是200，会抛出异常
            
            logger.debug(f"{source['name']} RSS源可访问，状态码: {response.status_code}")
            feed = feedparser.parse(source["url"])
            
            # 检查是否成功解析到条目
            if not feed.entries and 'backup_url' in source:
                logger.warning(f"{source['name']} 主URL未返回条目，尝试备用URL")
                feed = feedparser.parse(source["backup_url"])
        
        except Exception as e:
            # 如果主URL失败且有备用URL，尝试备用URL
            if 'backup_url' in source:
                logger.warning(f"{source['name']} 主URL访问失败: {str(e)}，尝试备用URL")
                feed = feedparser.parse(source["backup_url"])
            else:
                # 没有备用URL，重新抛出异常
                raise
        
        # 检查feed是否有错误
        if hasattr(feed, 'bozo_exception'):
            logger.warning(f"{source['name']} RSS解析警告: {feed.bozo_exception}")
        
        # 记录获取到的条目数量
        logger.debug(f"{source['name']} 获取到 {len(feed.entries)} 条原始条目")
        
        for entry in feed.entries:
            # 提取标题
            title = entry.get("title", "").strip()
            
            # 提取摘要
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            elif hasattr(entry, "content"):
                # 有些RSS源使用content字段
                for content in entry.content:
                    if content.get('type') == 'text/html':
                        summary = content.value
                        break
            
            # 清理HTML标签
            if summary:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text().strip()
            
            # 提取链接
            link = entry.get("link", "")
            
            # 提取发布日期
            published_date = datetime.now().strftime("%Y-%m-%d")
            if hasattr(entry, "published"):
                published_date = parse_date(entry.published)
            elif hasattr(entry, "updated"):
                published_date = parse_date(entry.updated)
            elif hasattr(entry, "pubDate"):
                published_date = parse_date(entry.pubDate)
            
            # 创建新闻项
            if title and link:
                news_item = {
                    "title": title,
                    "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                    "link": link,
                    "published_date": published_date,
                    "source": source["name"],
                    "category": source["category"]
                }
                news_list.append(news_item)
        
        logger.info(f"从 {source['name']} 获取到 {len(news_list)} 条新闻")
        
    except Exception as e:
        logger.error(f"从 {source['name']} 获取RSS新闻失败: {str(e)}", exc_info=True)
    
    return news_list


def fetch_from_web(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从网页爬取新闻
    
    Args:
        source: 网页源信息，包含name和url
        
    Returns:
        新闻列表，每条新闻包含title, summary, link, published_date
    """
    news_list = []
    
    try:
        logger.info(f"正在从 {source['name']} 爬取网页新闻")
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        response = requests.get(source["url"], headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 根据不同网站使用不同的解析逻辑
        if source["name"] == "The Verge AI":
            # 更新The Verge AI的选择器
            articles = []
            
            # 尝试找到文章列表容器
            sections = soup.select("section")
            if sections and len(sections) > 0:
                # 找到包含文章的section
                for section in sections:
                    # 查找所有链接
                    links = section.find_all("a")
                    # 过滤掉导航链接和非文章链接
                    article_links = []
                    for link in links:
                        href = link.get("href", "")
                        # 文章链接通常包含数字ID
                        if href and "/" in href and any(c.isdigit() for c in href) and not href.startswith(("/auth", "/tech", "/reviews")):
                            article_links.append(link)
                    
                    if len(article_links) > 3:  # 如果找到多个文章链接
                        for link in article_links[:10]:  # 限制为前10篇文章
                            title = link.get_text().strip()
                            url = link.get("href", "")
                            
                            # 确保链接是完整的URL
                            if url and not url.startswith(("http://", "https://")):
                                url = "https://www.theverge.com" + url
                            
                            if title and url:
                                # 创建文章对象
                                article = {
                                    "title": title,
                                    "link": url,
                                    "summary": "",  # 没有摘要
                                    "published_date": datetime.now().strftime("%Y-%m-%d"),  # 使用当前日期
                                    "source": source["name"],
                                    "category": source["category"]
                                }
                                articles.append(article)
            
            # 如果找到文章，添加到新闻列表
            if articles:
                news_list.extend(articles)
            else:
                logger.warning(f"无法从 {source['name']} 找到文章")
        
        elif source["name"] == "Wired AI":
            articles = soup.select("div.summary-item")
            for article in articles[:10]:  # 限制为前10篇文章
                title_elem = article.select_one("h3")
                link_elem = article.select_one("a")
                summary_elem = article.select_one("div.summary-item__dek")
                date_elem = article.select_one("time.summary-item__timestamp")
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get("href", "")
                    if not link.startswith("http"):
                        link = "https://www.wired.com" + link
                    
                    # 获取摘要
                    summary = ""
                    if summary_elem:
                        summary = summary_elem.get_text().strip()
                    
                    # 获取发布日期
                    published_date = datetime.now().strftime("%Y-%m-%d")
                    if date_elem and date_elem.get("datetime"):
                        published_date = parse_date(date_elem["datetime"])
                    
                    if title and link:
                        news_item = {
                            "title": title,
                            "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                            "link": link,
                            "published_date": published_date,
                            "source": source["name"],
                            "category": source["category"]
                        }
                        news_list.append(news_item)
        
        # 使用通用选择器处理新增的网页源
        elif "selector" in source:
            selector = source["selector"]
            articles = soup.select(selector["article"])
            for article in articles[:10]:  # 限制为前10篇文章
                title_elem = article.select_one(selector["title"])
                link_elem = article.select_one(selector["link"])
                summary_elem = article.select_one(selector["summary"]) if "summary" in selector else None
                date_elem = article.select_one(selector["date"]) if "date" in selector else None
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    
                    # 获取链接
                    if hasattr(link_elem, "get"):
                        link = link_elem.get("href", "")
                    else:
                        link = link_elem.attrs.get("href", "")
                    
                    # 确保链接是完整的URL
                    if link and not link.startswith(("http://", "https://")):
                        # 提取域名
                        domain = source["url"].split("//")[0] + "//" + source["url"].split("//")[1].split("/")[0]
                        link = domain + (link if link.startswith("/") else "/" + link)
                    
                    # 获取摘要
                    summary = ""
                    if summary_elem:
                        summary = summary_elem.get_text().strip()
                    
                    # 获取发布日期
                    published_date = datetime.now().strftime("%Y-%m-%d")
                    if date_elem:
                        date_str = None
                        if date_elem.get("datetime"):
                            date_str = date_elem.get("datetime")
                        else:
                            date_str = date_elem.get_text().strip()
                        
                        if date_str:
                            published_date = parse_date(date_str)
                    
                    if title and link:
                        news_item = {
                            "title": title,
                            "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                            "link": link,
                            "published_date": published_date,
                            "source": source["name"],
                            "category": source["category"]
                        }
                        news_list.append(news_item)
        
        logger.info(f"从 {source['name']} 爬取到 {len(news_list)} 条新闻")
        
    except Exception as e:
        logger.error(f"从 {source['name']} 爬取网页新闻失败: {str(e)}", exc_info=True)
    
    return news_list


def fetch_news() -> List[Dict[str, Any]]:
    """
    从所有来源获取新闻
    
    Returns:
        所有来源的新闻列表
    """
    all_news = []
    
    # 从RSS源获取新闻
    for source in RSS_SOURCES:
        try:
            news = fetch_from_rss(source)
            all_news.extend(news)
            # 添加随机延迟，避免请求过于频繁
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.error(f"处理RSS源 {source['name']} 时出错: {str(e)}", exc_info=True)
    
    # 从网页爬取新闻
    for source in WEB_SOURCES:
        try:
            news = fetch_from_web(source)
            all_news.extend(news)
            # 添加随机延迟，避免请求过于频繁
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            logger.error(f"处理网页源 {source['name']} 时出错: {str(e)}", exc_info=True)
    
    logger.info(f"总共获取到 {len(all_news)} 条新闻")
    return all_news


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试获取新闻
    news = fetch_news()
    
    # 打印结果
    print(json.dumps(news, indent=2, ensure_ascii=False)) 