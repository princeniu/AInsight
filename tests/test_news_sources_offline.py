"""新闻源诊断契约回归：只使用合成输入，不导入真实配置或请求网络。"""
import contextlib
import importlib.util
import io
from pathlib import Path
import types
import unittest
from unittest.mock import patch


_DIAGNOSTIC = Path(__file__).with_name("test_news_sources.py")
_spec = importlib.util.spec_from_file_location("news_sources_diagnostic", _DIAGNOSTIC)
diag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(diag)


def source(name):
    return {"name": name, "url": "https://invalid.example/", "category": "fixture"}


def news(_source):
    return [{"title": "synthetic headline"}]


def fixture_module(rss=news, web=news):
    return types.SimpleNamespace(
        RSS_SOURCES=[source("rss-a"), source("rss-b")],
        WEB_SOURCES=[source("web-a"), source("web-b")],
        fetch_from_rss=rss,
        fetch_from_web=web,
    )


class NewsSourceDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.stdout = contextlib.redirect_stdout(io.StringIO())
        self.stderr = contextlib.redirect_stderr(io.StringIO())
        self.stdout.__enter__()
        self.stderr.__enter__()
        self.addCleanup(self.stderr.__exit__, None, None, None)
        self.addCleanup(self.stdout.__exit__, None, None, None)

    def test_rss_limit_and_delay(self):
        calls, delays = [], []
        diag.test_rss_sources(2, fetcher=lambda s: calls.append(s["name"]) or news(s),
                              sources=[source("a"), source("b"), source("c")], sleep=delays.append)
        self.assertEqual(calls, ["a", "b"])
        self.assertEqual(delays, [1])

    def test_web_limit_and_delay(self):
        calls, delays = [], []
        diag.test_web_sources(2, fetcher=lambda s: calls.append(s["name"]) or news(s),
                              sources=[source("a"), source("b"), source("c")], sleep=delays.append)
        self.assertEqual(calls, ["a", "b"])
        self.assertEqual(delays, [2])

    def test_source_exception_is_propagated_after_remaining_sources(self):
        calls = []
        def fetch(item):
            calls.append(item["name"])
            if item["name"] == "bad":
                raise OSError("synthetic failure")
            return news(item)
        with self.assertRaises(diag.SourceCheckError):
            diag.test_rss_sources(fetcher=fetch, sources=[source("bad"), source("good")], sleep=lambda _: None)
        self.assertEqual(calls, ["bad", "good"])

    def test_empty_result_is_inconclusive(self):
        with self.assertRaises(diag.SourceCheckInconclusive):
            diag.test_web_sources(fetcher=lambda _: [], sources=[source("empty")])

    def test_empty_source_set_is_inconclusive(self):
        with self.assertRaises(diag.SourceCheckInconclusive):
            diag.test_rss_sources(fetcher=news, sources=[])

    def test_partial_injection_cannot_fall_back_to_real_loader(self):
        with patch.object(diag, "_load_fetcher") as loader:
            for check in (diag.test_rss_sources, diag.test_web_sources):
                with self.assertRaises(ValueError):
                    check(fetcher=news)
                with self.assertRaises(ValueError):
                    check(sources=[source("a")])
        loader.assert_not_called()

    def test_invalid_return_shape_is_failure(self):
        for value in (None, "", {}):
            with self.subTest(value=type(value).__name__), self.assertRaises(diag.SourceCheckError):
                diag.test_rss_sources(fetcher=lambda _, value=value: value, sources=[source("invalid")])

    def test_invalid_item_structure_is_failure(self):
        with self.assertRaises(diag.SourceCheckError):
            diag.test_web_sources(fetcher=lambda _: [{}], sources=[source("invalid")])

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            diag.test_rss_sources(0, fetcher=news, sources=[source("a")])

    def test_original_default_entry_loads_implementation(self):
        fixture = fixture_module()
        with patch.object(diag, "_load_fetcher", return_value=fixture) as loader:
            diag.test_rss_sources(sleep=lambda _: None)
            diag.test_web_sources(sleep=lambda _: None)
        self.assertEqual(loader.call_count, 2)

    def test_main_success_returns_zero(self):
        self.assertEqual(diag.main(loader=fixture_module, sleep=lambda _: None), 0)

    def test_main_failure_checks_other_kind_and_returns_one(self):
        web_calls = []
        def failed(_):
            raise OSError("synthetic failure")
        fixture = fixture_module(rss=failed, web=lambda s: web_calls.append(s["name"]) or news(s))
        self.assertEqual(diag.main(loader=lambda: fixture, sleep=lambda _: None), 1)
        self.assertEqual(web_calls, ["web-a", "web-b"])

    def test_main_empty_returns_two(self):
        self.assertEqual(diag.main(loader=lambda: fixture_module(rss=lambda _: []), sleep=lambda _: None), 2)

    def test_main_failure_takes_priority_over_inconclusive(self):
        def failed(_):
            raise OSError("synthetic failure")
        self.assertEqual(diag.main(loader=lambda: fixture_module(rss=lambda _: [], web=failed), sleep=lambda _: None), 1)

    def test_main_missing_dependency_returns_one(self):
        def unavailable():
            raise ModuleNotFoundError("synthetic missing dependency")
        self.assertEqual(diag.main(loader=unavailable, sleep=lambda _: None), 1)

    def test_exact_source_loader_does_not_use_top_level_module(self):
        fake_modules = {name: types.ModuleType(name) for name in ("feedparser", "requests", "bs4", "dateutil")}
        fake_modules["bs4"].BeautifulSoup = object
        fake_modules["dateutil"].parser = types.SimpleNamespace(parse=lambda _: None)
        fake_modules["news_fetcher"] = types.ModuleType("news_fetcher")
        with patch.dict("sys.modules", fake_modules):
            implementation = diag._load_fetcher()
        expected = _DIAGNOSTIC.resolve().parents[1] / "src" / "core" / "news_fetcher.py"
        self.assertEqual(Path(implementation.__file__).resolve(), expected)
        self.assertTrue(callable(implementation.fetch_from_rss))
        self.assertTrue(callable(implementation.fetch_from_web))


if __name__ == "__main__":
    unittest.main()
