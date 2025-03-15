#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.telegram_notifier import TelegramNotifier

def test_telegram_notification():
    """测试Telegram通知功能"""
    print("开始测试Telegram通知功能...")
    
    # 从配置文件加载通知器
    notifier = TelegramNotifier.from_config()
    
    if notifier:
        # 发送测试消息
        print("发送基本测试消息...")
        success = notifier.send_message("🎉 AI新闻自动化系统测试消息\n\n如果您看到这条消息，说明Telegram通知功能已成功配置！")
        print(f"通知发送{'成功' if success else '失败'}")
        
        # 测试文章通知
        print("\n测试文章生成通知...")
        test_article_notification(notifier)
        
        # 测试批量处理通知
        print("\n测试批量处理通知...")
        test_batch_notification(notifier)
    else:
        print("无法加载Telegram通知器，请检查配置文件")
        print("请确保config/telegram_config.json文件存在且包含正确的token和chat_id")

def test_article_notification(notifier):
    """测试文章生成通知"""
    # 模拟文章生成通知
    success = notifier.send_article_notification(
        title="AI突破：新型大语言模型展示惊人能力",
        source="OpenAI Blog",
        file_path="data/articles/20240712_AI突破_新型大语言模型展示惊人能力.txt",
        word_count=1200,
        model_used="gpt-4",
        content="近日，OpenAI发布了最新研究成果，展示了新一代大语言模型的惊人能力。这一模型不仅在语言理解和生成方面取得了突破，还能够执行复杂的推理任务。研究人员表示，这一进展将为AI在各行各业的应用带来革命性变化。\n\n专家认为，这项技术将重塑我们与计算机交互的方式，并可能在医疗、教育和科学研究等领域产生深远影响..."
    )
    
    print(f"文章通知测试{'成功' if success else '失败'}")

def test_batch_notification(notifier):
    """测试批量处理通知"""
    # 模拟批量处理完成通知
    success = notifier.send_batch_notification(
        total_fetched=120,
        total_filtered=45,
        total_generated=5,
        models_used=["gpt-4o", "gpt-3.5-turbo"],
        execution_time=187.5
    )
    
    print(f"批量处理通知测试{'成功' if success else '失败'}")

if __name__ == "__main__":
    test_telegram_notification()
