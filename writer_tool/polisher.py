"""
文章润色模块
调用大模型 API 改善文章表达
"""

import os
import json
import http.client
import urllib.parse


class Polisher:
    """文章润色器"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get("POLISH_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "POLISH_API_URL",
            "https://api.siliconflow.cn/v1/chat/completions"
        )
        self.model = os.environ.get("POLISH_MODEL", "Qwen/Qwen2.5-7B-Instruct")

    def polish(self, text: str, style: str = "natural") -> str:
        """
        润色文章

        Args:
            text: 原文
            style: 润色风格（natural/formal/casual/literary）

        Returns:
            润色后的文章
        """
        if not self.api_key:
            return self._polish_local(text, style)

        return self._polish_api(text, style)

    def _build_prompt(self, text: str, style: str) -> list[dict]:
        """构建 prompt"""
        style_map = {
            "natural": "保持原文风格，自然流畅",
            "formal": "书面正式风格",
            "casual": "轻松口语风格",
            "literary": "文学优美风格",
        }
        style_desc = style_map.get(style, "自然流畅")

        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个专业的中文写作润色助手。你的任务是：\n"
                    "1. 修正错别字和病句\n"
                    "2. 改善表达，使文章更流畅通顺\n"
                    "3. 保持原文的语气和风格\n"
                    "4. 不改变原文的核心意思\n\n"
                    "输出格式要求：\n"
                    "只输出润色后的文章正文，不要任何解释、标注或说明。"
                )
            },
            {
                "role": "user",
                "content": f"请将以下文章润色为「{style_desc}」的表达：\n\n{text}"
            }
        ]
        return messages

    def _polish_api(self, text: str, style: str) -> str:
        """通过 API 润色"""
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": self._build_prompt(text, style),
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        parsed = urllib.parse.urlparse(self.base_url)
        host = parsed.netloc

        conn = http.client.HTTPSConnection(host, context=ctx, timeout=30)
        conn.request(
            "POST",
            parsed.path if parsed.path else "/v1/chat/completions",
            body=json.dumps(payload),
            headers=headers
        )
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))

        if resp.status != 200:
            raise RuntimeError(f"API 请求失败: {resp.status} {data}")

        return data["choices"][0]["message"]["content"].strip()

    def _polish_local(self, text: str, style: str) -> str:
        """本地简单润色（无 API 时使用规则方法）"""
        import re

        # 简单的本地润色规则
        result = text

        # 去除多余空格
        result = re.sub(r" +", " ", result)
        result = re.sub(r"\n{3,}", "\n\n", result)

        # 常见连接词优化
        replacements = [
            ("然后就", "随后"),
            ("其实我觉得", "笔者认为"),
            ("非常非常", "极为"),
            ("特别特别", "格外"),
            ("我觉得", "本文认为"),
            ("这个东西", "该事物"),
            ("所以说", "因此"),
            ("因为所以", "因为"),
        ]
        for old, new in replacements:
            result = result.replace(old, new)

        # 标点修正
        result = re.sub(r"，，", "，", result)
        result = re.sub(r"。。", "。", result)
        result = re.sub(r"！！", "！", result)
        result = re.sub(r"？？", "？", result)

        return result
