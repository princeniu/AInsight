#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""新闻源手工联网诊断（不会发送通知）。

离线回归：python -m unittest discover -s tests -p test_news_sources_offline.py
原手工诊断：python tests/test_news_sources.py（会请求真实RSS/网页）
"""

import importlib.util
from pathlib import Path
import sys
import time


class SourceCheckError(RuntimeError):
    """至少一个新闻源检查抛出异常或返回无效结构。"""


class SourceCheckInconclusive(RuntimeError):
    """空结果不能证明源可用，也不能证明源已失效。"""


def _load_fetcher():
    """从实现文件加载，避免依赖调用时的工作目录或顶层同名模块。"""
    path = Path(__file__).resolve().parents[1] / "src" / "core" / "news_fetcher.py"
    spec = importlib.util.spec_from_file_location("news_sources_fetcher", path)
    if spec is None or spec.loader is None:
        raise ImportError("无法加载新闻获取实现")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_sources(sources, fetcher, label, delay, sleep):
    if not sources:
        raise SourceCheckInconclusive(f"{label}: 没有可检查的新闻源")
    failures = []
    inconclusive = []
    print(f"\n===== 测试{label}源 =====")
    for i, source in enumerate(sources):
        print(f"\n[{i + 1}/{len(sources)}] 测试 {source['name']}...")
        try:
            news = fetcher(source)
            if not isinstance(news, list):
                raise TypeError("抓取结果必须为新闻列表")
            if not news:
                inconclusive.append(source['name'])
                print(f"⚠️ {source['name']}: 返回空结果，可用性未确认")
            else:
                print(f"✅ {source['name']}: 获取到 {len(news)} 条新闻")
                print(f"  - 示例标题: {news[0]['title'][:50]}...")
        except Exception as error:
            failures.append(source['name'])
            # 不展开异常内容，以免第三方异常夹带请求或认证字段。
            print(f"❌ {source['name']}: 获取失败 ({type(error).__name__})")
        if i < len(sources) - 1:
            sleep(delay)
    if failures:
        raise SourceCheckError(f"{label}: {len(failures)}/{len(sources)} 个源检查失败")
    if inconclusive:
        raise SourceCheckInconclusive(f"{label}: {len(inconclusive)}/{len(sources)} 个源可用性未确认")


def test_rss_sources(limit=3, *, fetcher=None, sources=None, sleep=time.sleep):
    """保留手工联网诊断；离线检查同时注入抓取函数与源。"""
    if (fetcher is None) != (sources is None):
        raise ValueError("离线检查必须同时注入fetcher和sources")
    if fetcher is None:
        module = _load_fetcher()
        fetcher, sources = module.fetch_from_rss, module.RSS_SOURCES
    if limit < 1:
        raise ValueError("limit 必须大于0")
    _check_sources(sources[:limit], fetcher, "RSS", 1, sleep)


def test_web_sources(limit=2, *, fetcher=None, sources=None, sleep=time.sleep):
    """保留手工联网诊断；离线检查同时注入抓取函数与源。"""
    if (fetcher is None) != (sources is None):
        raise ValueError("离线检查必须同时注入fetcher和sources")
    if fetcher is None:
        module = _load_fetcher()
        fetcher, sources = module.fetch_from_web, module.WEB_SOURCES
    if limit < 1:
        raise ValueError("limit 必须大于0")
    _check_sources(sources[:limit], fetcher, "网页", 2, sleep)


def main(*, loader=None, sleep=time.sleep):
    try:
        module = (loader or _load_fetcher)()
    except Exception as error:
        print(f"无法加载新闻获取实现 ({type(error).__name__})", file=sys.stderr)
        return 1
    failures = 0
    inconclusive = 0
    for check, fetcher, sources in (
        (test_rss_sources, module.fetch_from_rss, module.RSS_SOURCES),
        (test_web_sources, module.fetch_from_web, module.WEB_SOURCES),
    ):
        try:
            check(fetcher=fetcher, sources=sources, sleep=sleep)
        except SourceCheckInconclusive:
            inconclusive += 1
            print("源诊断返回空结果，可用性未确认", file=sys.stderr)
        except Exception as error:
            failures += 1
            print(f"源诊断失败 ({type(error).__name__})", file=sys.stderr)
    print("\n测试失败！" if failures else "\n测试未确认！" if inconclusive else "\n测试完成！")
    return 1 if failures else 2 if inconclusive else 0


if __name__ == "__main__":
    raise SystemExit(main())
