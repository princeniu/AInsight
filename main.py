#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI热点新闻自动化采集与文章生成主程序

此脚本整合了新闻获取、筛选、文章生成和存储的完整流程。
"""

import os
import logging
import time
import argparse
from datetime import datetime
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# 导入自定义模块
from news_fetcher import fetch_news
from news_filter import filter_news
from article_generator import generate_article, get_available_models
from article_storage import save_article_to_markdown, save_article_to_db

# 导入配置
try:
    from config import MAX_ARTICLES_PER_RUN, MODEL_CONFIG
    DEFAULT_MODEL = MODEL_CONFIG.get("default_model", "gpt-4o")
except ImportError:
    MAX_ARTICLES_PER_RUN = 5  # 默认值
    DEFAULT_MODEL = "gpt-4o"  # 默认模型

# 初始化colorama
colorama.init()

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


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="AI热点新闻自动化采集与文章生成")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"要使用的OpenAI模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--max-articles", type=int, default=MAX_ARTICLES_PER_RUN,
                        help=f"最多生成的文章数量 (默认: {MAX_ARTICLES_PER_RUN})")
    parser.add_argument("--list-models", action="store_true",
                        help="列出所有可用的模型")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示详细的进度信息")
    
    args = parser.parse_args()
    
    # 如果指定了--list-models参数，打印可用模型并退出
    if args.list_models:
        print("\n可用的模型:")
        for model in get_available_models():
            if model == DEFAULT_MODEL:
                print(f"* {model} (默认)")
            else:
                print(f"* {model}")
        exit(0)
    
    return args


def print_status(message, status="进行中", color=Fore.BLUE, verbose=True):
    """
    打印带颜色的状态信息
    
    Args:
        message: 要显示的消息
        status: 状态文本
        color: 颜色代码
        verbose: 是否显示详细信息
    """
    if verbose:
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_text = f"{color}[{status}]{Style.RESET_ALL}"
        print(f"[{timestamp}] {status_text} {message}")


def main():
    """
    主函数，执行完整的新闻获取、筛选、生成和存储流程
    """
    # 解析命令行参数
    args = parse_arguments()
    model = args.model
    max_articles = args.max_articles
    verbose = args.verbose
    
    start_time = time.time()
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}AI热点新闻自动化采集与文章生成{Style.RESET_ALL}")
    print(f"使用模型: {Fore.GREEN}{model}{Style.RESET_ALL}")
    print(f"最大文章数: {Fore.GREEN}{max_articles}{Style.RESET_ALL}")
    print("=" * 60 + "\n")
    
    logger.info(f"开始执行AI热点新闻自动化采集与文章生成 (使用模型: {model})")
    
    try:
        # 步骤1: 获取新闻
        print_status("开始获取新闻...", "步骤1", Fore.BLUE, verbose)
        logger.info("步骤1: 开始获取新闻")
        
        with tqdm(total=100, desc="获取新闻", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            pbar.update(10)  # 初始进度
            news_list = fetch_news()
            pbar.update(90)  # 完成进度
        
        if not news_list:
            print_status("没有获取到任何新闻，程序终止", "失败", Fore.RED, True)
            logger.warning("没有获取到任何新闻，程序终止")
            return
        
        print_status(f"获取到 {len(news_list)} 条原始新闻", "完成", Fore.GREEN, True)
        logger.info(f"获取到 {len(news_list)} 条原始新闻")
        
        # 步骤2: 筛选新闻
        print_status("开始筛选新闻...", "步骤2", Fore.BLUE, verbose)
        logger.info("步骤2: 开始筛选新闻")
        
        with tqdm(total=100, desc="筛选新闻", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            pbar.update(10)  # 初始进度
            filtered_news = filter_news(news_list)
            pbar.update(90)  # 完成进度
        
        if not filtered_news:
            print_status("筛选后没有剩余新闻，程序终止", "失败", Fore.RED, True)
            logger.warning("筛选后没有剩余新闻，程序终止")
            return
        
        print_status(f"筛选后剩余 {len(filtered_news)} 条新闻", "完成", Fore.GREEN, True)
        logger.info(f"筛选后剩余 {len(filtered_news)} 条新闻")
        
        # 步骤3: 为每条筛选后的新闻生成文章
        print_status("开始生成文章...", "步骤3", Fore.BLUE, verbose)
        logger.info("步骤3: 开始生成文章")
        
        # 限制文章数量
        articles_to_process = filtered_news[:max_articles]
        
        # 创建总进度条
        with tqdm(total=len(articles_to_process), desc="文章生成总进度", ncols=100, 
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as total_pbar:
            
            for i, news in enumerate(articles_to_process):
                print_status(f"正在处理第 {i+1}/{len(articles_to_process)} 条新闻: {news['title']}", "处理中", Fore.YELLOW, verbose)
                logger.info(f"正在处理第 {i+1}/{min(max_articles, len(filtered_news))} 条新闻: {news['title']}")
                
                try:
                    # 生成文章
                    with tqdm(total=100, desc=f"生成文章 {i+1}/{len(articles_to_process)}", 
                              ncols=100, leave=False, 
                              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as article_pbar:
                        article_pbar.update(10)  # 开始生成
                        article = generate_article(news, model=model)
                        article_pbar.update(90)  # 完成生成
                    
                    if not article:
                        print_status(f"文章生成失败: {news['title']}", "失败", Fore.RED, True)
                        logger.warning(f"文章生成失败: {news['title']}")
                        total_pbar.update(1)
                        continue
                    
                    # 步骤4: 存储文章
                    print_status(f"存储文章: {news['title']}", "步骤4", Fore.BLUE, verbose)
                    logger.info(f"步骤4: 存储文章 - {news['title']}")
                    
                    # 创建文章元数据
                    article_data = {
                        "title": news["title"],
                        "content": article,
                        "source_url": news["link"],
                        "published_date": news["published_date"],
                        "model_used": model  # 记录使用的模型
                    }
                    
                    # 保存到Markdown
                    with tqdm(total=100, desc="保存为Markdown", ncols=100, leave=False, 
                              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as save_pbar:
                        save_pbar.update(50)
                        md_path = save_article_to_markdown(article_data)
                        save_pbar.update(50)
                    
                    print_status(f"文章已保存为Markdown: {md_path}", "完成", Fore.GREEN, verbose)
                    logger.info(f"文章已保存为Markdown: {md_path}")
                    
                    # 保存到数据库
                    with tqdm(total=100, desc="保存到数据库", ncols=100, leave=False, 
                              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as db_pbar:
                        db_pbar.update(50)
                        article_id = save_article_to_db(article_data)
                        db_pbar.update(50)
                    
                    print_status(f"文章已保存到数据库，ID: {article_id}", "完成", Fore.GREEN, verbose)
                    logger.info(f"文章已保存到数据库，ID: {article_id}")
                    
                    # 更新总进度条
                    total_pbar.update(1)
                    
                except Exception as e:
                    print_status(f"处理新闻时出错: {str(e)}", "错误", Fore.RED, True)
                    logger.error(f"处理新闻时出错: {str(e)}", exc_info=True)
                    total_pbar.update(1)
        
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"{Fore.GREEN}AI热点新闻自动化采集与文章生成完成!{Style.RESET_ALL}")
        print(f"总耗时: {Fore.YELLOW}{elapsed_time:.2f}秒{Style.RESET_ALL}")
        print(f"成功生成文章数: {Fore.GREEN}{len(articles_to_process)}{Style.RESET_ALL}")
        print("=" * 60 + "\n")
        
        logger.info(f"AI热点新闻自动化采集与文章生成完成，耗时: {elapsed_time:.2f}秒")
        
    except Exception as e:
        print_status(f"程序执行过程中出错: {str(e)}", "错误", Fore.RED, True)
        logger.error(f"程序执行过程中出错: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 确保存储目录存在
    os.makedirs("articles", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    
    # 执行主程序
    main() 