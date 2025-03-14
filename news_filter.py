#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻筛选模块

筛选高质量新闻，去除重复和不相关内容。
"""

import sqlite3
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# 下载必要的NLTK数据
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# 配置日志
logger = logging.getLogger(__name__)

def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度
    
    Args:
        text1: 第一段文本
        text2: 第二段文本
        
    Returns:
        相似度得分 (0-1)
    """
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except Exception as e:
        logger.warning(f"计算文本相似度时出错: {str(e)}")
        return 0.0

def is_duplicate_news(news: Dict[str, Any], existing_articles: List[Dict[str, Any]], 
                     similarity_threshold: float = 0.8) -> bool:
    """
    检查新闻是否重复
    
    Args:
        news: 待检查的新闻
        existing_articles: 已存在的文章列表
        similarity_threshold: 相似度阈值
        
    Returns:
        是否重复
    """
    # 检查链接是否完全匹配
    if any(article['original_link'] == news['link'] for article in existing_articles):
        logger.info(f"发现重复链接: {news['link']}")
        return True
    
    # 检查标题是否完全匹配
    if any(article['title'] == news['title'] for article in existing_articles):
        logger.info(f"发现重复标题: {news['title']}")
        return True
    
    # 计算标题和摘要的相似度
    news_text = f"{news['title']} {news.get('summary', '')}"
    for article in existing_articles:
        article_text = f"{article['title']} {article.get('content', '')[:200]}"  # 只比较内容前200个字符
        similarity = calculate_similarity(news_text, article_text)
        
        if similarity > similarity_threshold:
            logger.info(f"发现相似内容 (相似度: {similarity:.2f}): {news['title']}")
            return True
    
    return False

def filter_news(news_list: List[Dict[str, Any]], db_path: str = "database/articles.db",
                days_limit: int = 7) -> List[Dict[str, Any]]:
    """
    筛选新闻，去除重复和不相关的内容
    
    Args:
        news_list: 新闻列表
        db_path: 数据库路径
        days_limit: 只检查最近几天的文章
        
    Returns:
        筛选后的新闻列表
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最近的文章
        date_limit = (datetime.now() - timedelta(days=days_limit)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT title, content, original_link, published_date 
            FROM articles 
            WHERE published_date >= ?
        """, (date_limit,))
        
        # 转换为字典列表，方便处理
        existing_articles = []
        for row in cursor.fetchall():
            existing_articles.append({
                'title': row[0],
                'content': row[1],
                'original_link': row[2],
                'published_date': row[3]
            })
        
        # 过滤新闻
        filtered_news = []
        for news in news_list:
            if not is_duplicate_news(news, existing_articles):
                filtered_news.append(news)
            else:
                logger.info(f"跳过重复新闻: {news['title']}")
        
        logger.info(f"筛选前: {len(news_list)} 条新闻, 筛选后: {len(filtered_news)} 条新闻")
        return filtered_news
        
    except Exception as e:
        logger.error(f"筛选新闻时出错: {str(e)}")
        return []
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试数据
    test_news = [
        {
            "title": "OpenAI发布GPT-4重大更新",
            "summary": "GPT-4模型获得重大升级，性能显著提升",
            "link": "https://example.com/1"
        },
        {
            "title": "最新：OpenAI的GPT-4模型重大更新发布",
            "summary": "GPT-4模型进行了重大升级，带来性能提升",
            "link": "https://example.com/2"
        }
    ]
    
    # 测试查重功能
    filtered = filter_news(test_news)
    print(f"过滤后的新闻数量: {len(filtered)}")
    for news in filtered:
        print(f"- {news['title']}") 