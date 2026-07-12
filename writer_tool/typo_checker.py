"""
错别字检测模块
基于常见错别字词库 + 模糊匹配
"""

# 常见错别字映射表：（错误 → 正确）
TYPO_MAP = {
    "的地得": "的",      # 助词混淆，这里特殊处理
    "的得地": "的",
    # 常见错别字
    "已经": "已经",
    "以为": "以为",
    "在见": "再见",
    "再见": "再见",
    "象像": "像",
    "像象": "像",
    "做作": "做",
    "侯候": "候",
    "戊戌": "戊",
    "己经": "已经",
    "兰兰": "蓝",
    "按装": "安装",
    "甘败": "甘拜",
    "自抱自弃": "自暴自弃",
    "针贬": "针砭",
    "泊来品": "舶来品",
    "脉博": "脉搏",
    "松驰": "松弛",
    "精萃": "精粹",
    "幅射": "辐射",
    "重迭": "重叠",
    "复覆": "覆盖",
    "言简意骇": "言简意赅",
    "甘败下风": "甘拜下风",
    "悬梁刺骨": "悬梁刺股",
    "鼎立相助": "鼎力相助",
    "鬼鬼祟祟": "鬼鬼祟祟",
    "趋之若骛": "趋之若鹜",
    "一愁莫展": "一筹莫展",
    "穿流不息": "川流不息",
    "默守成规": "墨守成规",
    "一幅对联": "一副对联",
    "一幅漫画": "一副漫画",
    "天翻地复": "天翻地覆",
    "一股作气": "一鼓作气",
    "食不裹腹": "食不裹腹",
    "迫不急待": "迫不及待",
    "不能自己": "不能自己",
    "一如继往": "一如既往",
    "草管人命": "草菅人命",
    "和霭可亲": "和蔼可亲",
    "禁若寒蝉": "噤若寒蝉",
    "五彩斑斓": "五彩斑斓",
    "砰然心动": "怦然心动",
    "一见衷情": "一见钟情",
    "蜂涌而至": "蜂拥而至",
    "沉yi": "沉溺",
    "沉溺": "沉溺",
}

# 需要特殊检测的常见错误模式（正则）
TYPO_PATTERNS = [
    (r"的地得([^的地得])", r"的\g<1>"),      # 的/地/得混淆简化
    (r"([^的地得])的得", r"\g<1>的"),          # 逆向检测
    (r"象([\u4e00-\u9fa5]{1,3}?)像", r"像\1像"),  # 象/像混淆
    (r"做([\u4e00-\u9fa5]{1,3}?)作", r"做\1作"),  # 做/作混淆
    (r"戊戌变法", "戊戌变法"),                 # 戊/戌混淆
    (r"再([\u4e00-\u9fa5]{1,2})见", r"再\1见"), # 再/在混淆
]


def check_typo(text: str) -> list[dict]:
    """
    检测文本中的错别字
    返回: [{'type': 'typo', 'original': 'xxx', 'correct': 'xxx', 'reason': '...'}, ...]
    """
    issues = []
    import re

    # 1. 词组级别检测（遍历错别字词库）
    for wrong, correct in TYPO_MAP.items():
        if wrong == correct:
            continue
        # 搜索所有出现（不区分大小写，但中文无所谓）
        pattern = wrong
        start = 0
        while True:
            idx = text.find(pattern, start)
            if idx == -1:
                break
            issues.append({
                "type": "typo",
                "subtype": "word",
                "original": pattern,
                "correct": correct,
                "position": idx,
                "reason": f"常见错别字：「{pattern}」→「{correct}」"
            })
            start = idx + 1

    # 2. 模式级别检测（正则）
    for pattern, replacement in TYPO_PATTERNS:
        for match in re.finditer(pattern, text):
            original = match.group()
            # 估算正确写法
            fixed = re.sub(pattern, replacement, original)
            if fixed != original:
                issues.append({
                    "type": "typo",
                    "subtype": "pattern",
                    "original": original,
                    "correct": fixed,
                    "position": match.start(),
                    "reason": "疑似用词错误"
                })

    # 去重（同一位置只保留一个，取最长的）
    issues.sort(key=lambda x: -x["position"])
    filtered = []
    seen_pos = set()
    for issue in issues:
        pos = issue["position"]
        if pos not in seen_pos:
            filtered.append(issue)
            seen_pos.add(pos)
    filtered.sort(key=lambda x: x["position"])

    return filtered


def highlight_issues(text: str, issues: list[dict]) -> str:
    """把检测结果高亮标注出来"""
    result = text
    offset = 0
    for issue in issues:
        pos = issue["position"] + offset
        orig_len = len(issue["original"])
        correct = issue["correct"]
        tag = f"[❌{correct}]"
        result = result[:pos] + tag + result[pos + orig_len:]
        offset += len(tag) - orig_len
    return result
