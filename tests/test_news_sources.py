#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试新闻源脚本

用于测试各个新闻源的可用性和获取到的新闻数量
"""

import logging
import time
from news_fetcher import fetch_from_rss, fetch_from_web, RSS_SOURCES, WEB_SOURCES

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rss_sources(limit=3):
    """测试RSS源
    
    Args:
        limit: 限制测试的源数量
    """
    sources_to_test = RSS_SOURCES[:limit]
    print("\n===== 测试RSS源 =====")
    print(f"共有 {len(RSS_SOURCES)} 个RSS源，测试前 {len(sources_to_test)} 个")
    
    for i, source in enumerate(sources_to_test):
        print(f"\n[{i+1}/{len(sources_to_test)}] 测试 {source['name']}...")
        try:
            news = fetch_from_rss(source)
            print(f"✅ {source['name']}: 获取到 {len(news)} 条新闻")
            if len(news) > 0:
                print(f"  - 示例标题: {news[0]['title'][:50]}...")
        except Exception as e:
            print(f"❌ {source['name']}: 获取失败 - {str(e)}")
        
        # 添加延迟，避免请求过于频繁
        if i < len(sources_to_test) - 1:
            time.sleep(1)

def test_web_sources(limit=2):
    """测试网页源
    
    Args:
        limit: 限制测试的源数量
    """
    sources_to_test = WEB_SOURCES[:limit]
    print("\n===== 测试网页源 =====")
    print(f"共有 {len(WEB_SOURCES)} 个网页源，测试前 {len(sources_to_test)} 个")
    
    for i, source in enumerate(sources_to_test):
        print(f"\n[{i+1}/{len(sources_to_test)}] 测试 {source['name']}...")
        try:
            news = fetch_from_web(source)
            print(f"✅ {source['name']}: 获取到 {len(news)} 条新闻")
            if len(news) > 0:
                print(f"  - 示例标题: {news[0]['title'][:50]}...")
        except Exception as e:
            print(f"❌ {source['name']}: 获取失败 - {str(e)}")
        
        # 添加延迟，避免请求过于频繁
        if i < len(sources_to_test) - 1:
            time.sleep(2)

if __name__ == "__main__":
    print("开始测试新闻源...")
    test_rss_sources(3)  # 只测试前3个RSS源
    test_web_sources(2)  # 只测试前2个网页源
    print("\n测试完成！") 