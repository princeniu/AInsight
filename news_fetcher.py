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
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/research/rss",
        "category": "ai_company"
    },
    {
        "name": "DeepMind",
        "url": "https://www.deepmind.com/news.xml",
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
    }
]

# 定义网页爬虫源
WEB_SOURCES = [
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence",
        "category": "tech_news"
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/tag/artificial-intelligence/",
        "category": "tech_news"
    }
]

# 用户代理列表，避免被网站封锁
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
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
        feed = feedparser.parse(source["url"])
        
        for entry in feed.entries:
            # 提取标题
            title = entry.get("title", "").strip()
            
            # 提取摘要
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            
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


def fetch_from_web(source: Dict[str, str]) -> List[Dict[str, Any]]:
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
            articles = soup.select("div.c-entry-box--compact")
            for article in articles[:10]:  # 限制为前10篇文章
                title_elem = article.select_one("h2")
                link_elem = article.select_one("a")
                date_elem = article.select_one("time")
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get("href", "")
                    
                    # 获取摘要（可能需要访问文章页面）
                    summary = ""
                    
                    # 获取发布日期
                    published_date = datetime.now().strftime("%Y-%m-%d")
                    if date_elem and date_elem.get("datetime"):
                        published_date = parse_date(date_elem["datetime"])
                    
                    if title and link:
                        news_item = {
                            "title": title,
                            "summary": summary,
                            "link": link,
                            "published_date": published_date,
                            "source": source["name"],
                            "category": source["category"]
                        }
                        news_list.append(news_item)
        
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