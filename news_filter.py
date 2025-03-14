#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻筛选模块

对获取的新闻进行筛选，包括去重、关键词匹配和排序。
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Set
import re
from dateutil import parser as date_parser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 配置日志
logger = logging.getLogger(__name__)

# 定义AI相关关键词
AI_KEYWORDS = [
    "人工智能", "AI", "机器学习", "ML", "深度学习", "DL", "神经网络", "NN",
    "GPT", "ChatGPT", "大语言模型", "LLM", "生成式AI", "Generative AI",
    "OpenAI", "DeepMind", "Anthropic", "Claude", "Gemini", "Llama",
    "计算机视觉", "CV", "自然语言处理", "NLP", "强化学习", "RL",
    "语音识别", "图像生成", "DALL-E", "Midjourney", "Stable Diffusion",
    "多模态", "Multimodal", "AGI", "通用人工智能", "transformer", "注意力机制",
    "微调", "Fine-tuning", "提示工程", "Prompt Engineering", "RAG",
    "向量数据库", "Vector Database", "嵌入", "Embedding"
]

# 编译正则表达式模式
AI_PATTERN = re.compile("|".join(r"\b{}\b".format(re.escape(kw)) for kw in AI_KEYWORDS), re.IGNORECASE)


def is_ai_related(text: str) -> bool:
    """
    判断文本是否与AI相关
    
    Args:
        text: 要检查的文本
        
    Returns:
        如果文本包含AI关键词，返回True，否则返回False
    """
    return bool(AI_PATTERN.search(text))


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度
    
    Args:
        text1: 第一段文本
        text2: 第二段文本
        
    Returns:
        两段文本的余弦相似度，范围为0到1
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception as e:
        logger.warning(f"计算文本相似度时出错: {str(e)}")
        return 0.0


def calculate_news_score(news: Dict[str, Any]) -> float:
    """
    计算新闻的得分
    
    Args:
        news: 新闻项
        
    Returns:
        新闻的得分，范围为0到100
    """
    score = 50.0  # 基础分数
    
    # 根据来源调整分数
    source_category = news.get("category", "")
    if source_category == "ai_company":
        score += 20  # AI公司的官方博客更可靠
    elif source_category == "tech_news":
        score += 10  # 科技新闻网站较可靠
    
    # 根据发布日期调整分数（越新越好）
    try:
        published_date = date_parser.parse(news.get("published_date", ""))
        days_old = (datetime.now() - published_date).days
        
        # 最近7天的新闻得分更高
        if days_old <= 1:
            score += 20  # 今天发布
        elif days_old <= 3:
            score += 15  # 3天内发布
        elif days_old <= 7:
            score += 10  # 一周内发布
        else:
            score -= min(days_old, 30)  # 最多减30分
    except Exception:
        pass
    
    # 根据标题和摘要中的AI关键词数量调整分数
    title = news.get("title", "")
    summary = news.get("summary", "")
    
    title_keywords = len(re.findall(AI_PATTERN, title))
    summary_keywords = len(re.findall(AI_PATTERN, summary))
    
    score += min(title_keywords * 5, 15)  # 标题中的关键词，最多加15分
    score += min(summary_keywords * 2, 10)  # 摘要中的关键词，最多加10分
    
    # 确保分数在0-100范围内
    return max(0, min(score, 100))


def remove_duplicates(news_list: List[Dict[str, Any]], similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    移除重复的新闻
    
    Args:
        news_list: 新闻列表
        similarity_threshold: 相似度阈值，超过此值的新闻被视为重复
        
    Returns:
        去重后的新闻列表
    """
    if not news_list:
        return []
    
    unique_news = []
    seen_titles: Set[str] = set()
    
    # 按分数降序排序，保留高分新闻
    sorted_news = sorted(news_list, key=lambda x: x.get("score", 0), reverse=True)
    
    for news in sorted_news:
        title = news.get("title", "").lower()
        summary = news.get("summary", "")
        
        # 检查标题是否完全相同
        if title in seen_titles:
            continue
        
        # 检查与已保留新闻的相似度
        is_duplicate = False
        for unique_news_item in unique_news:
            unique_title = unique_news_item.get("title", "")
            unique_summary = unique_news_item.get("summary", "")
            
            # 计算标题相似度
            title_similarity = calculate_similarity(title, unique_title.lower())
            
            # 如果标题相似度高，进一步检查摘要相似度
            if title_similarity > similarity_threshold:
                summary_similarity = calculate_similarity(summary, unique_summary)
                if summary_similarity > similarity_threshold:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            seen_titles.add(title)
            unique_news.append(news)
    
    return unique_news


def filter_news(news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    筛选新闻
    
    Args:
        news_list: 原始新闻列表
        
    Returns:
        筛选后的新闻列表
    """
    if not news_list:
        return []
    
    logger.info(f"开始筛选 {len(news_list)} 条新闻")
    
    # 步骤1: 过滤掉非AI相关的新闻
    ai_related_news = []
    for news in news_list:
        title = news.get("title", "")
        summary = news.get("summary", "")
        combined_text = f"{title} {summary}"
        
        if is_ai_related(combined_text):
            ai_related_news.append(news)
    
    logger.info(f"AI相关新闻: {len(ai_related_news)}/{len(news_list)}")
    
    # 步骤2: 计算每条新闻的得分
    scored_news = []
    for news in ai_related_news:
        score = calculate_news_score(news)
        news["score"] = score
        scored_news.append(news)
    
    # 步骤3: 去除重复新闻
    unique_news = remove_duplicates(scored_news)
    logger.info(f"去重后的新闻: {len(unique_news)}/{len(scored_news)}")
    
    # 步骤4: 按得分排序
    sorted_news = sorted(unique_news, key=lambda x: x.get("score", 0), reverse=True)
    
    # 步骤5: 只保留得分超过60分的新闻
    filtered_news = [news for news in sorted_news if news.get("score", 0) >= 60]
    logger.info(f"最终筛选后的新闻: {len(filtered_news)}/{len(news_list)}")
    
    return filtered_news


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试数据
    test_news = [
        {
            "title": "OpenAI发布GPT-4o，多模态能力大幅提升",
            "summary": "OpenAI今日发布了GPT-4o，这是一个具有强大多模态能力的大型语言模型。",
            "link": "https://example.com/1",
            "published_date": "2023-05-20",
            "source": "Tech News",
            "category": "tech_news"
        },
        {
            "title": "OpenAI推出GPT-4o模型，支持实时语音和视觉",
            "summary": "OpenAI发布了最新的GPT-4o模型，支持实时语音交互和视觉理解能力。",
            "link": "https://example.com/2",
            "published_date": "2023-05-20",
            "source": "AI Blog",
            "category": "ai_company"
        },
        {
            "title": "苹果发布新款MacBook Pro",
            "summary": "苹果公司今日发布了搭载M3芯片的新款MacBook Pro。",
            "link": "https://example.com/3",
            "published_date": "2023-05-19",
            "source": "Tech News",
            "category": "tech_news"
        }
    ]
    
    # 测试筛选
    filtered = filter_news(test_news)
    
    # 打印结果
    print(json.dumps(filtered, indent=2, ensure_ascii=False)) 