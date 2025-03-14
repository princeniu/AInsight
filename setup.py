#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ai_news_generator",
    version="1.0.0",
    description="AI热点新闻自动化采集与文章生成",
    author="Prince Niu",
    author_email="example@example.com",
    url="https://github.com/princeniu/AInsight",
    packages=find_packages(),
    install_requires=[
        "feedparser>=6.0.10",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "openai>=1.55.3",
        "schedule>=1.2.1",
        "python-dateutil>=2.8.2",
        "nltk>=3.8.1",
        "scikit-learn>=1.3.2",
        "httpx<0.28",
        "tqdm>=4.65.0",
        "colorama>=0.4.6",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-news=src.main:main",
            "ai-news-scheduler=src.scheduler.scheduler:main",
        ],
    },
) 