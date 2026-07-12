"""
typo_checker 单元测试
核心防护：
  - test_correct_forms_zero_false_positive：把所有「正确词」拼成大段文本，
    跑检测必须零误报。任何反向条目（正确→错误）都会在这里翻车，
    因为该「正确词」也会被当成错误词命中。
  - test_every_entry_detected：每条词库都能被检测并给出正确修正。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typo_checker as tc


def test_integrity_import_ok():
    """导入即触发 __check_integrity，无自环/空键"""
    assert isinstance(tc.TYPO_MAP, dict)
    assert len(tc.TYPO_MAP) > 0


def test_correct_forms_zero_false_positive():
    """关键防护：所有正确词拼成大段文本，必须零误报"""
    corpus = "".join(sorted(set(tc.TYPO_MAP.values())))
    issues = tc.check_typo(corpus)
    assert issues == [], (
        f"正确词被误报（疑似反向条目）：{[ (i['original'], i['correct']) for i in issues]}"
    )


def test_every_entry_detected():
    """每条词库都能被检测，并返回正确修正"""
    for wrong, correct in tc.TYPO_MAP.items():
        if wrong == correct:
            continue
        issues = tc.check_typo(wrong)
        assert issues, f"未检测到错别字「{wrong}」"
        hit = next((i for i in issues if i["original"] == wrong), None)
        assert hit, f"「{wrong}」未被命中"
        assert hit["correct"] == correct, (
            f"「{wrong}」修正应为「{correct}」，实际「{hit['correct']}」"
        )


def test_apply_fixes_basic():
    text = "这篇文章写的不错，但是有错别字，需要按装软件后再检查。"
    issues = tc.check_typo(text)
    fixed = tc.apply_fixes(text, issues)
    assert "安装" in fixed
    assert "按装" not in fixed


def test_no_false_positive_on_clean_text():
    clean = (
        "中国是一个历史悠久的国家，中华民族拥有灿烂的文化。"
        "我们应当遵循自然规律，因地制宜地发展经济。"
        "他的演讲慷慨激昂，令听众受益匪浅。"
    )
    issues = tc.check_typo(clean)
    assert issues == [], f"干净文本出现误报：{issues}"


def test_highlight_returns_string():
    text = "请按装这个程序。"
    issues = tc.check_typo(text)
    out = tc.highlight_issues(text, issues)
    assert isinstance(out, str)
    assert "安装" in out
