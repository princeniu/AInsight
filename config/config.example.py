#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件示例

请复制此文件为 config.py 并填入你的实际配置信息
"""

# OpenAI API配置
OPENAI_API_KEY = "your-openai-api-key-here"

# 模型配置
MODEL_CONFIG = {
    "default_model": "gpt-4o",  # 默认使用的模型
    "available_models": [
        "gpt-4o",        # 最强大的多模态模型
        "gpt-4-turbo",   # 强大的文本模型
        "gpt-3.5-turbo"  # 经济实惠的模型
    ]
}

# RSS源配置（可选，如需修改默认RSS源可在此处配置）
RSS_SOURCES = [
    # 示例：
    # {
    #     "name": "OpenAI Blog",
    #     "url": "https://openai.com/research/rss",
    #     "category": "ai_company"
    # },
]

# 定时任务配置
SCHEDULE_TIME = "08:00"  # 每天运行的时间

# 文章生成配置
MAX_ARTICLES_PER_RUN = 5  # 每次运行最多生成的文章数量 