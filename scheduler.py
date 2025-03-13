#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定时任务模块

使用schedule库实现定时运行任务，每天08:00自动执行。
"""

import os
import sys
import time
import logging
import schedule
import subprocess
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "main.py")


def run_task():
    """
    运行主程序任务
    """
    logger.info("开始执行定时任务")
    
    try:
        # 使用Python解释器运行main.py
        result = subprocess.run(
            [sys.executable, MAIN_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("任务执行成功")
        logger.debug(f"输出: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"错误输出: {result.stderr}")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"任务执行失败: {str(e)}")
        logger.error(f"错误输出: {e.stderr}")
    
    except Exception as e:
        logger.error(f"运行任务时出错: {str(e)}", exc_info=True)
    
    logger.info("定时任务执行完毕")


def setup_schedule():
    """
    设置定时任务
    """
    # 每天08:00运行任务
    schedule.every().day.at("08:00").do(run_task)
    logger.info("已设置定时任务: 每天08:00运行")
    
    # 如果当前时间已经过了08:00，则立即运行一次（仅在首次启动时）
    current_hour = datetime.now().hour
    if current_hour >= 8:
        logger.info("首次启动，立即执行一次任务")
        run_task()


def generate_cron_config():
    """
    生成cron配置
    """
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    cron_line = f"0 8 * * * {python_path} {script_path} > /tmp/ai_news_cron.log 2>&1"
    
    print("\n=== Cron配置 ===")
    print("要设置cron定时任务，请运行以下命令:")
    print(f"(crontab -l 2>/dev/null; echo '{cron_line}') | crontab -")
    print("\n这将在每天08:00自动运行任务")


def main():
    """
    主函数
    """
    logger.info("AI热点新闻自动化采集与文章生成定时器已启动")
    
    # 设置定时任务
    setup_schedule()
    
    # 生成cron配置（仅供参考）
    generate_cron_config()
    
    # 运行定时任务循环
    logger.info("开始定时任务循环，按Ctrl+C退出")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("定时任务已手动停止")
    except Exception as e:
        logger.error(f"定时任务循环出错: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main() 