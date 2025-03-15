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

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入自定义模块
from src.utils.telegram_notifier import TelegramNotifier  # 导入Telegram通知模块

# 导入配置
try:
    from config.config import SCHEDULE_TIME, MODEL_CONFIG
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
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
MAIN_SCRIPT = os.path.join(ROOT_DIR, "src", "main.py")

# 初始化Telegram通知器
telegram = TelegramNotifier.from_config()


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
        model: 要使用的模型名称
        verbose: 是否显示详细进度
    """
    print_status("开始执行任务", "任务", Fore.BLUE)
    logger.info("开始执行任务")
    
    # 确保目录存在
    os.makedirs(os.path.join(ROOT_DIR, "data", "articles"), exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, "data", "database"), exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, "logs"), exist_ok=True)
    
    if model is None:
        model = DEFAULT_MODEL
    
    print_status(f"开始执行定时任务 (使用模型: {model})", "开始", Fore.GREEN)
    logger.info(f"开始执行定时任务 (使用模型: {model})")
    
    # 发送Telegram通知：任务开始
    if telegram:
        start_message = (
            f"<b>🔄 定时任务开始执行</b>\n\n"
            f"<b>⏰ 开始时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<b>🤖 使用模型:</b> {model}\n\n"
            f"<i>任务正在执行中，完成后将发送结果通知...</i>"
        )
        telegram.send_message(start_message)
        if verbose:
            print_status("已发送Telegram开始通知", "通知", Fore.CYAN)
    
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
            
            # 发送Telegram通知：任务成功
            if telegram:
                success_message = (
                    f"<b>✅ 定时任务执行成功</b>\n\n"
                    f"<b>⏰ 完成时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"<b>🤖 使用模型:</b> {model}\n\n"
                    f"<i>文章已生成并保存，详细结果请查看主程序通知</i>"
                )
                telegram.send_message(success_message)
                if verbose:
                    print_status("已发送Telegram成功通知", "通知", Fore.CYAN)
        else:
            print("-" * 60)
            print_status(f"任务执行失败，返回码: {process.returncode}", "失败", Fore.RED)
            logger.error(f"任务执行失败: 返回码 {process.returncode}")
            
            # 显示错误输出
            stderr_output = process.stderr.read()
            
            # 发送Telegram通知：任务失败
            if telegram:
                error_message = (
                    f"<b>❌ 定时任务执行失败</b>\n\n"
                    f"<b>⏰ 失败时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"<b>🤖 使用模型:</b> {model}\n"
                    f"<b>📋 返回码:</b> {process.returncode}\n\n"
                )
                
                if stderr_output:
                    # 截取错误输出的前300个字符
                    error_preview = stderr_output[:300] + ("..." if len(stderr_output) > 300 else "")
                    error_message += f"<b>🔍 错误信息:</b>\n<pre>{error_preview}</pre>\n\n"
                
                error_message += "<i>请检查日志文件获取详细错误信息</i>"
                telegram.send_message(error_message)
                if verbose:
                    print_status("已发送Telegram失败通知", "通知", Fore.CYAN)
            
            if stderr_output:
                print_status("错误输出:", "错误", Fore.RED)
                print(stderr_output)
    
    except Exception as e:
        print_status(f"运行任务时出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"运行任务时出错: {str(e)}", exc_info=True)
        
        # 发送Telegram通知：任务异常
        if telegram:
            exception_message = (
                f"<b>⚠️ 定时任务执行异常</b>\n\n"
                f"<b>⏰ 异常时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"<b>🤖 使用模型:</b> {model}\n"
                f"<b>🔍 异常信息:</b> {str(e)}\n\n"
                f"<i>请检查日志文件获取详细错误信息</i>"
            )
            telegram.send_message(exception_message)
            if verbose:
                print_status("已发送Telegram异常通知", "通知", Fore.CYAN)
    
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
    
    # 发送Telegram通知：定时器启动
    if telegram:
        schedule_message = (
            f"<b>🕒 AI新闻自动化定时器已启动</b>\n\n"
            f"<b>📅 执行计划:</b> 每天 {SCHEDULE_TIME}\n"
            f"<b>🤖 使用模型:</b> {model}\n"
            f"<b>📊 详细输出:</b> {'开启' if verbose else '关闭'}\n\n"
            f"<i>定时器将按计划自动执行任务</i>"
        )
        telegram.send_message(schedule_message)
        if verbose:
            print_status("已发送Telegram定时器启动通知", "通知", Fore.CYAN)
    
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
    if telegram:
        print(f"Telegram通知: {Fore.GREEN}已启用{Style.RESET_ALL}")
    else:
        print(f"Telegram通知: {Fore.YELLOW}未启用{Style.RESET_ALL}")
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
        
        # 发送Telegram通知：定时器停止
        if telegram:
            stop_message = (
                f"<b>🛑 AI新闻自动化定时器已停止</b>\n\n"
                f"<b>⏰ 停止时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"<b>📋 停止原因:</b> 用户手动停止\n\n"
                f"<i>定时器已停止运行，需要手动重启</i>"
            )
            telegram.send_message(stop_message)
            if verbose:
                print_status("已发送Telegram定时器停止通知", "通知", Fore.CYAN)
    except Exception as e:
        print_status(f"定时任务循环出错: {str(e)}", "错误", Fore.RED)
        logger.error(f"定时任务循环出错: {str(e)}", exc_info=True)
        
        # 发送Telegram通知：定时器异常
        if telegram:
            error_message = (
                f"<b>⚠️ AI新闻自动化定时器异常</b>\n\n"
                f"<b>⏰ 异常时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"<b>🔍 异常信息:</b> {str(e)}\n\n"
                f"<i>定时器已停止运行，请检查日志并手动重启</i>"
            )
            telegram.send_message(error_message)
            if verbose:
                print_status("已发送Telegram定时器异常通知", "通知", Fore.CYAN)


if __name__ == "__main__":
    main() 