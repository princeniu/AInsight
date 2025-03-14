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
            
            # 检查内容类型是否为XML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'xml' not in content_type and 'rss' not in content_type and 'application/atom+xml' not in content_type:
                logger.warning(f"{source['name']} 返回的内容类型不是XML: {content_type}")
                # 尝试强制解析，但记录警告
            
            # 使用响应内容而不是URL来解析，避免重复请求
            feed = feedparser.parse(response.content)
            
            # 检查是否成功解析到条目
            if not feed.entries and 'backup_url' in source:
                logger.warning(f"{source['name']} 主URL未返回条目，尝试备用URL")
                backup_response = requests.get(source["backup_url"], headers=headers, timeout=10)
                backup_response.raise_for_status()
                feed = feedparser.parse(backup_response.content)
        
        except requests.exceptions.HTTPError as e:
            # HTTP错误（如404, 500等）
            if 'backup_url' in source:
                logger.warning(f"{source['name']} 主URL HTTP错误: {str(e)}，尝试备用URL")
                try:
                    backup_response = requests.get(source["backup_url"], headers=headers, timeout=10)
                    backup_response.raise_for_status()
                    feed = feedparser.parse(backup_response.content)
                except Exception as be:
                    logger.error(f"{source['name']} 备用URL也失败: {str(be)}")
                    return []
            else:
                logger.error(f"{source['name']} HTTP错误: {str(e)}")
                return []
                
        except requests.exceptions.ConnectionError as e:
            # 连接错误
            logger.error(f"{source['name']} 连接错误: {str(e)}")
            return []
            
        except requests.exceptions.Timeout as e:
            # 超时错误
            logger.error(f"{source['name']} 请求超时: {str(e)}")
            return []
            
        except requests.exceptions.RequestException as e:
            # 其他请求错误
            logger.error(f"{source['name']} 请求错误: {str(e)}")
            return []
        
        # 检查feed是否有错误
        if hasattr(feed, 'bozo') and feed.bozo:
            logger.warning(f"{source['name']} RSS解析警告: {getattr(feed, 'bozo_exception', 'Unknown error')}")
            # 如果解析错误但仍有条目，继续处理
            if not feed.entries:
                logger.error(f"{source['name']} RSS解析失败且没有条目")
                return []
        
        # 记录获取到的条目数量
        logger.debug(f"{source['name']} 获取到 {len(feed.entries)} 条原始条目")
        
        for entry in feed.entries:
            try:
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
                    try:
                        soup = BeautifulSoup(summary, "html.parser")
                        summary = soup.get_text().strip()
                    except Exception as e:
                        logger.warning(f"清理HTML标签失败: {str(e)}")
                        # 如果BeautifulSoup失败，尝试简单的HTML标签移除
                        summary = summary.replace('<', ' <').replace('>', '> ')
                
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
            except Exception as e:
                logger.warning(f"处理 {source['name']} 的条目时出错: {str(e)}")
                continue
        
        logger.info(f"从 {source['name']} 获取到 {len(news_list)} 条新闻")
        
    except Exception as e:
        logger.error(f"从 {source['name']} 获取RSS新闻失败: {str(e)}")
    
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
        
        try:
            # 增加重试机制
            max_retries = 3
            retry_delay = 2  # 秒
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(source["url"], headers=headers, timeout=15)
                    response.raise_for_status()
                    break  # 成功获取，跳出循环
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"{source['name']} 请求失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                        time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    else:
                        raise  # 最后一次尝试仍失败，抛出异常
            
            # 检查响应内容是否为空
            if not response.text:
                logger.warning(f"{source['name']} 返回了空内容")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 根据不同网站使用不同的解析逻辑
            if "selector" in source:
                # 使用自定义选择器
                selector = source["selector"]
                articles = soup.select(selector.get("article", "article"))
                
                if not articles:
                    logger.warning(f"{source['name']} 未找到文章元素，选择器可能需要更新")
                    return []
                
                for article in articles[:10]:  # 限制为前10篇文章
                    try:
                        # 提取标题
                        title_elem = article.select_one(selector.get("title", "h2"))
                        title = title_elem.get_text().strip() if title_elem else ""
                        
                        # 提取链接
                        link_elem = article.select_one(selector.get("link", "a"))
                        link = link_elem.get("href", "") if link_elem else ""
                        
                        # 确保链接是完整的URL
                        if link and not link.startswith(("http://", "https://")):
                            # 从源URL中提取域名
                            domain = "/".join(source["url"].split("/")[:3])
                            link = domain + (link if link.startswith("/") else "/" + link)
                        
                        # 提取摘要
                        summary_elem = article.select_one(selector.get("summary", "p"))
                        summary = summary_elem.get_text().strip() if summary_elem else ""
                        
                        # 提取日期
                        date_elem = article.select_one(selector.get("date", "time"))
                        published_date = datetime.now().strftime("%Y-%m-%d")
                        if date_elem:
                            date_text = date_elem.get_text().strip()
                            if date_text:
                                published_date = parse_date(date_text)
                        
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
                    except Exception as e:
                        logger.warning(f"处理 {source['name']} 的文章时出错: {str(e)}")
                        continue
            else:
                # 特定网站的自定义解析逻辑
                # ... 其他特定网站的解析逻辑 ...
                pass
            
            logger.info(f"从 {source['name']} 爬取到 {len(news_list)} 条新闻")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"{source['name']} HTTP错误: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"{source['name']} 连接错误: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"{source['name']} 请求超时: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"{source['name']} 请求错误: {str(e)}")
        except Exception as e:
            logger.error(f"{source['name']} 爬取网页新闻失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"从 {source['name']} 爬取网页新闻时发生未预期错误: {str(e)}")
    
    return news_list


def check_source_health(sources: List[Dict[str, Any]], source_type: str = "rss") -> List[Dict[str, Any]]:
    """
    检查新闻源的健康状态，标记或更新失效的源
    
    Args:
        sources: 新闻源列表
        source_type: 源类型，"rss"或"web"
        
    Returns:
        更新后的新闻源列表
    """
    healthy_sources = []
    unhealthy_sources = []
    
    for source in sources:
        try:
            headers = {'User-Agent': get_random_user_agent()}
            response = requests.get(source["url"], headers=headers, timeout=5)
            
            if response.status_code >= 400:
                logger.warning(f"{source['name']} 返回状态码 {response.status_code}，可能不健康")
                unhealthy_sources.append(source)
            else:
                healthy_sources.append(source)
                
        except Exception as e:
            logger.warning(f"{source['name']} 健康检查失败: {str(e)}")
            unhealthy_sources.append(source)
    
    # 记录不健康的源
    if unhealthy_sources:
        logger.warning(f"发现 {len(unhealthy_sources)} 个不健康的{source_type}源: " + 
                      ", ".join([s["name"] for s in unhealthy_sources]))
    
    return healthy_sources


def fetch_news(max_sources: int = None, check_health: bool = True) -> List[Dict[str, Any]]:
    """
    从所有来源获取新闻
    
    Args:
        max_sources: 最大源数量，None表示不限制
        check_health: 是否检查源健康状态
        
    Returns:
        新闻列表
    """
    all_news = []
    
    # 检查RSS源健康状态
    rss_sources = RSS_SOURCES
    if check_health:
        rss_sources = check_source_health(RSS_SOURCES, "rss")
    
    # 限制源数量
    if max_sources:
        rss_sources = rss_sources[:max_sources]
    
    # 从RSS源获取新闻
    for source in rss_sources:
        news = fetch_from_rss(source)
        all_news.extend(news)
        # 添加短暂延迟，避免请求过于频繁
        time.sleep(0.5)
    
    # 检查网页源健康状态
    web_sources = WEB_SOURCES
    if check_health:
        web_sources = check_source_health(WEB_SOURCES, "web")
    
    # 限制源数量
    if max_sources:
        web_sources = web_sources[:max_sources]
    
    # 从网页源获取新闻
    for source in web_sources:
        news = fetch_from_web(source)
        all_news.extend(news)
        # 添加短暂延迟，避免请求过于频繁
        time.sleep(0.5)
    
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