#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定时任务模块

使用schedule库实现定时运行任务，每天自动执行。
"""

import os
import sys
import time
import logging
import schedule
import subprocess
import argparse
from datetime import datetime
import colorama
from colorama import Fore, Style

# 导入配置
try:
    from config import SCHEDULE_TIME, MODEL_CONFIG
    DEFAULT_MODEL = MODEL_CONFIG.get("default_model", "gpt-4o")
except ImportError:
    SCHEDULE_TIME = "08:00"  # 默认值
    DEFAULT_MODEL = "gpt-4o"  # 默认模型

# 初始化colorama
colorama.init()

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


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="AI热点新闻自动化采集与文章生成定时器")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"要使用的OpenAI模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示详细的进度信息")
    
    return parser.parse_args()


def print_status(message, status="信息", color=Fore.BLUE):
    """
    打印带颜色的状态信息
    
    Args:
        message: 要显示的消息
        status: 状态文本
        color: 颜色代码
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_text = f"{color}[{status}]{Style.RESET_ALL}"
    print(f"[{timestamp}] {status_text} {message}")


def run_task(model=None, verbose=False):
    """
    运行主程序任务
    
    Args:
        model: 要使用的模型名称，如果为None则使用默认模型
        verbose: 是否显示详细进度
    """
    if model is None:
        model = DEFAULT_MODEL
    
    print_status(f"开始执行定时任务 (使用模型: {model})", "开始", Fore.GREEN)
    logger.info(f"开始执行定时任务 (使用模型: {model})")
    
    try:
        # 构建命令参数
        cmd = [sys.executable, MAIN_SCRIPT, "--model", model]
        if verbose:
            cmd.append("--verbose")
        
        # 显示执行的命令
        print_status(f"执行命令: {' '.join(cmd)}", "命令", Fore.YELLOW)
        
        # 使用Python解释器运行main.py，并传递模型参数
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时显示输出
        print_status("任务正在执行中，以下是实时输出:", "输出", Fore.CYAN)
        print("-" * 60)
        
        # 读取并显示输出
        for line in process.stdout:
            print(line.rstrip())
        
        # 等待进程完成
        process.wait()
        
        # 检查返回码
        if process.returncode == 0:
            print("-" * 60)
            print_status("任务执行成功", "成功", Fore.GREEN)
            logger.info("任务执行成功")
        else:
            print("-" * 60)
            print_status(f"任务执行失败，返回码: {process.returncode}", "失败", Fore.RED)
            logger.error(f"任务执行失败: 返回码 {process.returncode}")
            
            # 显示错误输出
            stderr_output = process.stderr.read()
            if stderr_output:
                print_status("错误输出:", "错误", Fore.RED)
                print(stderr_output)
    
    except Exception as e:
        print_status(f"运行任务时出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"运行任务时出错: {str(e)}", exc_info=True)
    
    print_status("定时任务执行完毕", "完成", Fore.GREEN)
    logger.info("定时任务执行完毕")


def setup_schedule(model=None, verbose=False):
    """
    设置定时任务
    
    Args:
        model: 要使用的模型名称
        verbose: 是否显示详细进度
    """
    # 创建一个带有模型参数的任务函数
    def scheduled_task():
        run_task(model, verbose)
    
    # 使用配置的时间运行任务
    schedule.every().day.at(SCHEDULE_TIME).do(scheduled_task)
    print_status(f"已设置定时任务: 每天{SCHEDULE_TIME}运行 (使用模型: {model})", "设置", Fore.GREEN)
    logger.info(f"已设置定时任务: 每天{SCHEDULE_TIME}运行 (使用模型: {model})")
    
    # 解析配置的时间
    try:
        schedule_hour = int(SCHEDULE_TIME.split(":")[0])
        
        # 如果当前时间已经过了设定时间，则立即运行一次（仅在首次启动时）
        current_hour = datetime.now().hour
        if current_hour >= schedule_hour:
            print_status("首次启动，立即执行一次任务", "首次", Fore.YELLOW)
            logger.info("首次启动，立即执行一次任务")
            run_task(model, verbose)
    except (ValueError, IndexError):
        print_status(f"无法解析时间格式: {SCHEDULE_TIME}，使用默认行为", "警告", Fore.YELLOW)
        logger.warning(f"无法解析时间格式: {SCHEDULE_TIME}，使用默认行为")


def generate_cron_config(model=None, verbose=False):
    """
    生成cron配置
    
    Args:
        model: 要使用的模型名称
        verbose: 是否显示详细进度
    """
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    # 解析配置的时间
    try:
        hour, minute = SCHEDULE_TIME.split(":")
        cron_time = f"{minute} {hour} * * *"
    except (ValueError, IndexError):
        cron_time = "0 8 * * *"  # 默认为每天8:00
        print_status(f"无法解析时间格式: {SCHEDULE_TIME}，使用默认cron时间: {cron_time}", "警告", Fore.YELLOW)
        logger.warning(f"无法解析时间格式: {SCHEDULE_TIME}，使用默认cron时间: {cron_time}")
    
    # 添加模型参数
    model_param = f"--model {model}" if model else ""
    verbose_param = "--verbose" if verbose else ""
    cron_line = f"{cron_time} {python_path} {script_path} {model_param} {verbose_param} > /tmp/ai_news_cron.log 2>&1"
    
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}Cron配置{Style.RESET_ALL}")
    print("要设置cron定时任务，请运行以下命令:")
    print(f"{Fore.YELLOW}(crontab -l 2>/dev/null; echo '{cron_line}') | crontab -{Style.RESET_ALL}")
    print(f"\n这将在每天{SCHEDULE_TIME}自动运行任务")
    if model:
        print(f"使用模型: {Fore.GREEN}{model}{Style.RESET_ALL}")
    if verbose:
        print(f"显示详细进度: {Fore.GREEN}是{Style.RESET_ALL}")
    print("=" * 60)


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()
    model = args.model
    verbose = args.verbose
    
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}AI热点新闻自动化采集与文章生成定时器{Style.RESET_ALL}")
    print(f"使用模型: {Fore.GREEN}{model}{Style.RESET_ALL}")
    print(f"定时执行时间: {Fore.GREEN}{SCHEDULE_TIME}{Style.RESET_ALL}")
    print(f"显示详细进度: {Fore.GREEN}{verbose}{Style.RESET_ALL}")
    print("=" * 60 + "\n")
    
    logger.info(f"AI热点新闻自动化采集与文章生成定时器已启动 (使用模型: {model})")
    
    # 设置定时任务
    setup_schedule(model, verbose)
    
    # 生成cron配置（仅供参考）
    generate_cron_config(model, verbose)
    
    # 运行定时任务循环
    print_status("开始定时任务循环，按Ctrl+C退出", "循环", Fore.CYAN)
    logger.info("开始定时任务循环，按Ctrl+C退出")
    
    try:
        # 显示下一次运行时间
        next_run = schedule.next_run()
        if next_run:
            time_diff = next_run - datetime.now()
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print_status(f"下一次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (还有 {hours}小时 {minutes}分钟 {seconds}秒)", "计划", Fore.YELLOW)
        
        # 定时任务循环
        while True:
            schedule.run_pending()
            
            # 每分钟更新一次下一次运行时间
            if datetime.now().second == 0:
                next_run = schedule.next_run()
                if next_run:
                    time_diff = next_run - datetime.now()
                    hours, remainder = divmod(time_diff.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    print_status(f"下一次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (还有 {hours}小时 {minutes}分钟 {seconds}秒)", "计划", Fore.YELLOW)
            
            time.sleep(1)  # 每秒检查一次
    except KeyboardInterrupt:
        print_status("定时任务已手动停止", "停止", Fore.YELLOW)
        logger.info("定时任务已手动停止")
    except Exception as e:
        print_status(f"定时任务循环出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"定时任务循环出错: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main() 