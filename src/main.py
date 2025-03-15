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
import sys
from datetime import datetime
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入自定义模块
from src.core.news_fetcher import fetch_news
from src.core.news_filter import filter_news
from src.core.article_generator import generate_article, get_available_models
from src.storage.article_storage import save_article_to_markdown, save_article_to_db

# 导入配置
try:
    from config.config import MAX_ARTICLES_PER_RUN, MODEL_CONFIG
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
        logging.FileHandler("logs/ai_news_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description="AI热点新闻自动化采集与文章生成")
    
    # 添加模型选择参数
    parser.add_argument("--model", type=str, default=None,
                        help=f"要使用的OpenAI模型 (默认: {DEFAULT_MODEL})")
    
    # 添加列出可用模型的参数
    parser.add_argument("--list-models", action="store_true",
                        help="列出所有可用的模型")
    
    # 添加最大文章数量参数，使用配置文件中的值作为默认值
    parser.add_argument("--max-articles", type=int, default=MAX_ARTICLES_PER_RUN,
                        help=f"最大生成文章数量 (默认: {MAX_ARTICLES_PER_RUN})")
    
    # 添加详细输出参数
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示详细的进度信息")
    
    # 添加健康检查参数
    parser.add_argument("--skip-health-check", action="store_true",
                        help="跳过新闻源健康检查")
    
    # 添加最大源数量参数
    parser.add_argument("--max-sources", type=int, default=None,
                        help="每种类型的最大源数量 (默认: 不限制)")
    
    return parser.parse_args()


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


def main(model: str = None, max_articles: int = None, verbose: bool = False):
    """
    主程序入口
    
    Args:
        model: 要使用的模型名称
        max_articles: 最大文章数量，如果为None则使用配置文件中的值
        verbose: 是否显示详细进度
    """
    # 使用配置文件中的值作为默认值
    if max_articles is None:
        max_articles = MAX_ARTICLES_PER_RUN
    
    start_time = time.time()
    
    # 打印标题
    print("\n" + "=" * 60)
    print(f"AI热点新闻自动化采集与文章生成")
    print(f"使用模型: {model or DEFAULT_MODEL}")
    print(f"最大文章数: {max_articles} (来自{'命令行参数' if max_articles != MAX_ARTICLES_PER_RUN else '配置文件'})")
    print("=" * 60 + "\n")
    
    # 步骤1: 获取新闻
    print_status("开始获取新闻...", "步骤1", Fore.BLUE)
    logger.info("步骤1: 开始获取新闻")
    
    try:
        with tqdm(total=100, desc="获取新闻", ncols=100, disable=not verbose) as pbar:
            # 使用健康检查和最大源数量限制
            news_list = fetch_news(max_sources=20, check_health=True)
            pbar.update(100)
        
        print_status(f"获取到 {len(news_list)} 条原始新闻", "完成", Fore.GREEN)
        logger.info(f"获取到 {len(news_list)} 条原始新闻")
        
        if not news_list:
            print_status("未获取到任何新闻，程序终止", "错误", Fore.RED)
            logger.error("未获取到任何新闻，程序终止")
            return
    except Exception as e:
        print_status(f"获取新闻时出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"获取新闻时出错: {str(e)}")
        return
    
    # 步骤2: 筛选新闻
    print_status("开始筛选新闻...", "步骤2", Fore.BLUE)
    logger.info("步骤2: 开始筛选新闻")
    
    try:
        with tqdm(total=100, desc="筛选新闻", ncols=100, disable=not verbose) as pbar:
            filtered_news = filter_news(news_list)
            pbar.update(100)
        
        print_status(f"筛选后剩余 {len(filtered_news)} 条新闻", "完成", Fore.GREEN)
        logger.info(f"筛选后剩余 {len(filtered_news)} 条新闻")
        
        if not filtered_news:
            print_status("筛选后没有符合条件的新闻，程序终止", "警告", Fore.YELLOW)
            logger.warning("筛选后没有符合条件的新闻，程序终止")
            return
    except Exception as e:
        print_status(f"筛选新闻时出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"筛选新闻时出错: {str(e)}")
        return
    
    # 步骤3: 生成文章
    print_status("开始生成文章...", "步骤3", Fore.BLUE)
    logger.info("步骤3: 开始生成文章")
    
    # 限制文章数量
    filtered_news = filtered_news[:max_articles]
    
    # 生成文章
    articles = []
    with tqdm(total=len(filtered_news), desc="文章生成总进度", ncols=100, disable=not verbose) as pbar:
        for i, news in enumerate(filtered_news):
            print_status(f"正在处理第 {i+1}/{len(filtered_news)} 条新闻: {news['title']}", "处理中", Fore.YELLOW)
            logger.info(f"正在处理第 {i+1}/{len(filtered_news)} 条新闻: {news['title']}")
            
            try:
                # 生成文章
                print_status(f"正在使用模型 {model or DEFAULT_MODEL} 生成文章 (尝试 1/3)", "生成", Fore.YELLOW)
                print_status(f"文章标题: {news['title']}", "标题", Fore.CYAN)
                article_content = generate_article(news, model=model, verbose=verbose)
                
                if article_content:
                    # 创建文章对象
                    article = {
                        "title": news["title"],
                        "content": article_content,
                        "source_url": news["link"],
                        "published_date": news["published_date"],
                        "model_used": model or DEFAULT_MODEL
                    }
                    articles.append(article)
                    
                    # 步骤4: 存储文章
                    print_status(f"存储文章: {article['title']}", "步骤4", Fore.BLUE)
                    logger.info(f"步骤4: 存储文章 - {article['title']}")
                    
                    try:
                        # 保存文章到Markdown和纯文本
                        md_path, txt_path = save_article_to_markdown(article)
                        print_status(f"文章已保存为Markdown: {md_path}", "完成", Fore.GREEN)
                        print_status(f"文章已保存为纯文本: {txt_path}", "完成", Fore.GREEN)
                        logger.info(f"文章已保存为Markdown: {md_path}")
                        logger.info(f"文章已保存为纯文本: {txt_path}")
                        
                        # 保存文章到数据库
                        article_id = save_article_to_db(article)
                        print_status(f"文章已保存到数据库，ID: {article_id}", "完成", Fore.GREEN)
                        logger.info(f"文章已保存到数据库，ID: {article_id}")
                        
                        # 发送Telegram通知
                        word_count = len(article_content.split())
                        telegram.send_article_notification(
                            title=article['title'],
                            source=news['source'],
                            file_path=md_path,
                            word_count=word_count,
                            model_used=model,
                            content=article_content if telegram.include_preview else None
                        )
                        
                        # 如果配置了发送完整文章
                        if telegram and telegram.send_full_article:
                            telegram.send_full_article(title=article['title'], content=article_content)
                    except Exception as e:
                        print_status(f"保存文章时出错: {str(e)}", "错误", Fore.RED)
                        logger.error(f"保存文章时出错: {str(e)}")
                else:
                    print_status(f"文章生成失败: {news['title']}", "失败", Fore.RED)
                    logger.error(f"文章生成失败: {news['title']}")
            except Exception as e:
                print_status(f"处理新闻时出错: {str(e)}", "错误", Fore.RED)
                logger.error(f"处理新闻时出错: {str(e)}")
            
            pbar.update(1)
    
    # 总结
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"AI热点新闻自动化采集与文章生成完成!")
    print(f"总耗时: {elapsed_time:.2f}秒")
    print(f"成功生成文章数: {len(articles)}")
    print("=" * 60 + "\n")
    
    logger.info(f"AI热点新闻自动化采集与文章生成完成，耗时: {elapsed_time:.2f}秒")


if __name__ == "__main__":
    # 确保存储目录存在
    os.makedirs("data/articles", exist_ok=True)
    os.makedirs("data/database", exist_ok=True)
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/ai_news_generator.log"),
            logging.StreamHandler()
        ]
    )
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果请求列出模型，则显示可用模型并退出
    if args.list_models:
        models = get_available_models()
        print("\n可用的模型:")
        for i, model in enumerate(models):
            if model == DEFAULT_MODEL:
                print(f"  {model} (默认)")
            else:
                print(f"  {model}")
        print()
        sys.exit(0)
    
    # 运行主程序
    try:
        main(
            model=args.model,
            max_articles=args.max_articles,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序执行过程中出错: {str(e)}")
        logger.error(f"程序执行过程中出错: {str(e)}", exc_info=True)
        sys.exit(1) 