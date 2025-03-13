#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文章生成模块

使用GPT-4o生成高质量AI文章。
"""

import os
import logging
import json
import time
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

# 配置日志
logger = logging.getLogger(__name__)

# 获取OpenAI API密钥
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("未设置OPENAI_API_KEY环境变量，请设置后再运行")

# 创建OpenAI客户端
client = OpenAI(api_key=OPENAI_API_KEY)

# 文章生成提示模板
ARTICLE_PROMPT_TEMPLATE = """
你是一位专业的AI领域科技记者，需要根据以下新闻信息撰写一篇引人入胜的文章。

新闻标题: {title}
新闻摘要: {summary}
新闻链接: {link}
发布日期: {published_date}

请按照以下要求撰写文章:

1. 文章结构:
   - 标题：吸引人的标题，可以适当修改原标题使其更吸引人
   - 引言：设置悬念或提出问题，引起读者兴趣
   - 正文：详细分析新闻内容，解释技术要点，探讨AI发展趋势
   - 专家观点：添加1-2位AI领域专家的观点（可以创造虚构专家）
   - 结论：总结文章要点，并引导读者思考或讨论

2. 文章风格:
   - 长度：800-1200字
   - 段落简短：每段2-3句话，提高可读性
   - 语言风格：通俗易懂，适合普通读者
   - 加入适量表情符号，增加亲和力
   - 使用一些吸引人的小标题分隔内容

3. 内容要求:
   - 确保内容准确，不要过度夸大
   - 解释复杂的AI概念时要通俗易懂
   - 分析这一新闻对AI行业的影响
   - 提供一些相关背景信息
   - 在结尾提出1-2个引导读者思考的问题

请直接输出完整的文章内容，不需要包含任何额外的说明。
"""

def generate_article(news: Dict[str, Any], max_retries: int = 3) -> Optional[str]:
    """
    使用GPT-4o生成文章
    
    Args:
        news: 新闻信息，包含title, summary, link, published_date
        max_retries: 最大重试次数
        
    Returns:
        生成的文章内容，如果生成失败则返回None
    """
    if not OPENAI_API_KEY:
        logger.error("未设置OPENAI_API_KEY环境变量，无法生成文章")
        return None
    
    # 准备提示内容
    prompt = ARTICLE_PROMPT_TEMPLATE.format(
        title=news.get("title", ""),
        summary=news.get("summary", ""),
        link=news.get("link", ""),
        published_date=news.get("published_date", "")
    )
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            logger.info(f"正在生成文章: {news.get('title')} (尝试 {attempt + 1}/{max_retries})")
            
            # 调用GPT-4o API
            response = client.chat.completions.create(
                model="gpt-4o",  # 使用GPT-4o模型
                messages=[
                    {"role": "system", "content": "你是一位专业的AI领域科技记者，擅长撰写通俗易懂、引人入胜的AI新闻文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # 控制创造性
                max_tokens=2000,  # 最大输出长度
                top_p=0.95,
                frequency_penalty=0.5,  # 减少重复
                presence_penalty=0.5,  # 鼓励多样性
            )
            
            # 提取生成的文章内容
            article_content = response.choices[0].message.content.strip()
            
            if article_content:
                logger.info(f"文章生成成功: {len(article_content)} 字符")
                return article_content
            else:
                logger.warning("生成的文章内容为空")
        
        except Exception as e:
            logger.error(f"生成文章时出错: {str(e)}")
            
            # 如果不是最后一次尝试，则等待后重试
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    logger.error(f"在 {max_retries} 次尝试后仍未能生成文章")
    return None


def optimize_title(title: str) -> str:
    """
    优化文章标题，使其更吸引人
    
    Args:
        title: 原始标题
        
    Returns:
        优化后的标题
    """
    if not OPENAI_API_KEY:
        logger.warning("未设置OPENAI_API_KEY环境变量，无法优化标题")
        return title
    
    try:
        logger.info(f"正在优化标题: {title}")
        
        # 调用GPT-4o API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位标题优化专家，擅长创作吸引人的标题。"},
                {"role": "user", "content": f"请优化以下AI新闻标题，使其更吸引人、更容易引起读者点击，但不要过度夸大或使用误导性内容。保持在20个字以内。\n\n原标题: {title}"}
            ],
            temperature=0.7,
            max_tokens=50,
            top_p=0.95,
        )
        
        # 提取优化后的标题
        optimized_title = response.choices[0].message.content.strip()
        
        # 移除可能的引号和前缀
        optimized_title = optimized_title.replace('"', '').replace('"', '')
        optimized_title = optimized_title.replace('"', '').replace("'", "")
        optimized_title = optimized_title.replace("优化标题：", "").replace("优化后的标题：", "")
        
        logger.info(f"标题优化成功: {optimized_title}")
        return optimized_title
    
    except Exception as e:
        logger.error(f"优化标题时出错: {str(e)}")
        return title


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试数据
    test_news = {
        "title": "OpenAI发布GPT-4o，多模态能力大幅提升",
        "summary": "OpenAI今日发布了GPT-4o，这是一个具有强大多模态能力的大型语言模型，支持实时语音交互和视觉理解。",
        "link": "https://example.com/news/1",
        "published_date": "2023-05-20"
    }
    
    # 测试生成文章
    article = generate_article(test_news)
    
    if article:
        print("\n" + "=" * 50 + "\n")
        print(article)
        print("\n" + "=" * 50) 