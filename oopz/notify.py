"""钉钉群机器人通知（纯标准库）。

支持两种机器人：
1. 普通自定义机器人：只需 webhook（DINGTALK_WEBHOOK）。
2. 加签机器人：额外配置 DINGTALK_SECRET，自动计算签名。
"""

import base64
import hashlib
import hmac
import json
import time
import urllib.parse
import urllib.request

from . import config


def _signed_url() -> str:
    """返回带签名参数（加签机器人）的 webhook 地址。"""
    webhook = config.DINGTALK_WEBHOOK
    secret = config.DINGTALK_SECRET
    if not secret:
        return webhook
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(digest))
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={timestamp}&sign={sign}"


def enabled() -> bool:
    return bool(config.DINGTALK_WEBHOOK)


def send_text(content: str) -> bool:
    """发送文本通知，返回是否发送成功。未配置 webhook 时返回 False。"""
    if not config.DINGTALK_WEBHOOK:
        return False
    payload = json.dumps({"msgtype": "text", "text": {"content": content}}, ensure_ascii=False)
    req = urllib.request.Request(
        _signed_url(),
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("errcode") == 0
    except Exception:
        return False
