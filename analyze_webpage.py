#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网页结构分析脚本

用于分析网页结构，寻找正确的文章选择器
"""

import requests
from bs4 import BeautifulSoup

def analyze_webpage(url):
    """分析网页结构，寻找可能的文章选择器"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print(f"正在分析网页: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 可能的文章选择器
    selectors = [
        "article", 
        "div.relative", 
        "div.group", 
        "div.flex", 
        "div.duet--article--article-body-component",
        "div.c-entry-box--compact",
        "div.c-compact-river__entry",
        "div.l-col__main",
        "div.c-entry-box--compact--article",
        "div.wh8b41h",
        "div.a18g6gd",
        "div.a18g6gd a",
        "div.wh8b41h a",
        "div.i0ukxu0",
        "li.a18g6gd",
        "div.a18g6gd div"
    ]
    
    print("\n可能的文章选择器:")
    for selector in selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        
        if elements and len(elements) > 0:
            print(f"  示例: {elements[0].get_text()[:100].strip()}...")
            
            # 检查是否包含标题和链接
            title_selectors = ["h1", "h2", "h3", ".title", ".headline"]
            link_selectors = ["a", "a.permalink", "a.title"]
            
            for title_selector in title_selectors:
                title_elements = elements[0].select(title_selector)
                if title_elements:
                    print(f"  - 找到标题元素 ({title_selector}): {title_elements[0].get_text().strip()}")
                    break
            
            for link_selector in link_selectors:
                link_elements = elements[0].select(link_selector)
                if link_elements:
                    print(f"  - 找到链接元素 ({link_selector}): {link_elements[0].get('href')}")
                    break
    
    # 查找所有h2标签，通常是文章标题
    print("\n所有h2标签:")
    h2_elements = soup.find_all("h2")
    for i, h2 in enumerate(h2_elements[:5]):  # 只显示前5个
        print(f"[{i+1}] {h2.get_text().strip()}")
        # 查找父元素
        parent = h2.parent
        print(f"  父元素: {parent.name}.{' '.join(parent.get('class', []))}")
        # 查找链接
        links = h2.find_all("a")
        for link in links:
            print(f"  链接: {link.get('href')}")
    
    # 查找所有a标签，可能是文章链接
    print("\n所有a标签 (前10个):")
    a_elements = soup.find_all("a")
    for i, a in enumerate(a_elements[:10]):
        if a.get_text().strip():
            print(f"[{i+1}] {a.get_text().strip()[:50]}...")
            print(f"  链接: {a.get('href')}")
            print(f"  父元素: {a.parent.name}.{' '.join(a.parent.get('class', []))}")
    
    # 查找可能的文章列表容器
    print("\n可能的文章列表容器:")
    list_selectors = ["ul", "ol", "div.feed", "div.list", "div.grid", "div.articles", "section"]
    for selector in list_selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)} 个元素")
        
        if elements and len(elements) > 0:
            # 检查是否包含多个文章
            for i, element in enumerate(elements[:3]):  # 只检查前3个
                links = element.find_all("a")
                if len(links) > 3:  # 如果包含多个链接，可能是文章列表
                    print(f"  - 元素 {i+1} 包含 {len(links)} 个链接，可能是文章列表")
                    for j, link in enumerate(links[:3]):  # 只显示前3个链接
                        print(f"    链接 {j+1}: {link.get_text().strip()[:30]}... -> {link.get('href')}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    # 分析The Verge AI网页
    analyze_webpage("https://www.theverge.com/ai-artificial-intelligence") 