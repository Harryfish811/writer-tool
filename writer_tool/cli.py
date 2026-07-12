#!/usr/bin/env python3
"""
写作润色 CLI 入口
用法：
    python -m writer_tool.cli check "文本内容"
    python -m writer_tool.cli polish "文本内容"
    python -m writer_tool.cli --file article.txt
"""

import argparse
import sys
import os
from .typo_checker import check_typo, highlight_issues
from .polisher import Polisher


def cmd_check(args):
    """检查错别字"""
    text = _get_text(args)

    issues = check_typo(text)

    if not issues:
        print("✅ 未检测到错别字！")
        return

    print(f"🔍 检测到 {len(issues)} 处可能的问题：\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. 「{issue['original']}」 → 「{issue['correct']}」")
        print(f"     原因：{issue['reason']}")
        print()

    print("\n📝 修正预览：")
    highlighted = highlight_issues(text, issues)
    print(highlighted)


def cmd_polish(args):
    """润色文章"""
    text = _get_text(args)

    print("✨ 正在润色...", file=sys.stderr)

    polisher = Polisher()
    style = args.style or "natural"

    try:
        result = polisher.polish(text, style=style)
        print(result)
    except Exception as e:
        print(f"❌ 润色失败：{e}", file=sys.stderr)
        print("\n💡 提示：设置环境变量 POLISH_API_KEY 可以使用 AI 润色", file=sys.stderr)
        print("   或配置 POLISH_API_URL 指定 API 地址", file=sys.stderr)
        sys.exit(1)


def cmd_fix(args):
    """直接修正错别字"""
    text = _get_text(args)

    issues = check_typo(text)
    if not issues:
        print("✅ 无需修正")
        return

    # 应用修正
    result = text
    offset = 0
    for issue in sorted(issues, key=lambda x: x["position"]):
        pos = issue["position"] + offset
        orig_len = len(issue["original"])
        result = result[:pos] + issue["correct"] + result[pos + orig_len:]
        offset += len(issue["correct"]) - orig_len

    print(result)


def _get_text(args) -> str:
    """从参数或文件获取文本"""
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在：{args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    return args.text


def main():
    parser = argparse.ArgumentParser(
        prog="writer",
        description="✏️ 写作润色 & 错别字检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  writer check "这是一段要检查的文字"
  writer polish "这是一段要润色的文字"
  writer fix "这是一段有错别的文字"
  writer check --file article.txt
  writer polish --file article.txt --style formal
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # check 命令
    p_check = subparsers.add_parser("check", help="检查错别字")
    p_check.add_argument("text", nargs="?", help="要检查的文本（省略则从 stdin 读取）")
    p_check.add_argument("-f", "--file", help="从文件读取")
    p_check.set_defaults(func=cmd_check)

    # polish 命令
    p_polish = subparsers.add_parser("polish", help="润色文章")
    p_polish.add_argument("text", nargs="?", help="要润色的文本")
    p_polish.add_argument("-f", "--file", help="从文件读取")
    p_polish.add_argument("-s", "--style", choices=["natural", "formal", "casual", "literary"],
                          default="natural", help="润色风格（默认 natural）")
    p_polish.set_defaults(func=cmd_polish)

    # fix 命令
    p_fix = subparsers.add_parser("fix", help="直接修正错别字")
    p_fix.add_argument("text", nargs="?", help="要修正的文本")
    p_fix.add_argument("-f", "--file", help="从文件读取")
    p_fix.set_defaults(func=cmd_fix)

    args = parser.parse_args()

    # 如果没有文本且没有文件，从 stdin 读取
    if not args.text and not args.file:
        args.text = sys.stdin.read()

    args.func(args)


if __name__ == "__main__":
    main()
