#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI热点新闻自动化采集与文章生成主程序

此脚本整合了新闻获取、筛选、文章生成和存储的完整流程。
"""

import os
import logging
import time
from datetime import datetime

# 导入自定义模块
from news_fetcher import fetch_news
from news_filter import filter_news
from article_generator import generate_article
from article_storage import save_article_to_markdown, save_article_to_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_news_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    主函数，执行完整的新闻获取、筛选、生成和存储流程
    """
    start_time = time.time()
    logger.info("开始执行AI热点新闻自动化采集与文章生成")
    
    try:
        # 步骤1: 获取新闻
        logger.info("步骤1: 开始获取新闻")
        news_list = fetch_news()
        logger.info(f"获取到 {len(news_list)} 条原始新闻")
        
        if not news_list:
            logger.warning("没有获取到任何新闻，程序终止")
            return
        
        # 步骤2: 筛选新闻
        logger.info("步骤2: 开始筛选新闻")
        filtered_news = filter_news(news_list)
        logger.info(f"筛选后剩余 {len(filtered_news)} 条新闻")
        
        if not filtered_news:
            logger.warning("筛选后没有剩余新闻，程序终止")
            return
        
        # 步骤3: 为每条筛选后的新闻生成文章
        logger.info("步骤3: 开始生成文章")
        for i, news in enumerate(filtered_news[:5]):  # 限制为前5条新闻
            logger.info(f"正在处理第 {i+1}/{min(5, len(filtered_news))} 条新闻: {news['title']}")
            
            try:
                # 生成文章
                article = generate_article(news)
                
                if not article:
                    logger.warning(f"文章生成失败: {news['title']}")
                    continue
                
                # 步骤4: 存储文章
                logger.info(f"步骤4: 存储文章 - {news['title']}")
                
                # 创建文章元数据
                article_data = {
                    "title": news["title"],
                    "content": article,
                    "source_url": news["link"],
                    "published_date": news["published_date"]
                }
                
                # 保存到Markdown
                md_path = save_article_to_markdown(article_data)
                logger.info(f"文章已保存为Markdown: {md_path}")
                
                # 保存到数据库
                article_id = save_article_to_db(article_data)
                logger.info(f"文章已保存到数据库，ID: {article_id}")
                
            except Exception as e:
                logger.error(f"处理新闻时出错: {str(e)}", exc_info=True)
        
        elapsed_time = time.time() - start_time
        logger.info(f"AI热点新闻自动化采集与文章生成完成，耗时: {elapsed_time:.2f}秒")
        
    except Exception as e:
        logger.error(f"程序执行过程中出错: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 确保存储目录存在
    os.makedirs("articles", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    
    # 执行主程序
    main() 