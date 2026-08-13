"""HTTP 客户端：自动注入 oopz-* 请求头与签名。"""

import json
import time
import urllib.error
import urllib.request
import uuid

from . import config, crypto


def _build_headers(path_with_query: str, body: str, ts: str, jwt: str = "", uid: str = "") -> dict:
    headers = {
        "accept": "*/*",
        "content-type": "application/json;charset=utf-8",
        "oopz-app-version-number": config.APP_VERSION,
        "oopz-channel": config.CHANNEL,
        "oopz-device-id": config.DEVICE_ID,
        "oopz-platform": config.PLATFORM,
        "oopz-request-id": str(uuid.uuid4()),
        "oopz-sign": crypto.oopz_sign(path_with_query, body, ts),
        "oopz-time": ts,
        "oopz-web": "true",
        "origin": "https://web.oopz.cn",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
        ),
    }
    # 已登录请求才携带鉴权头；登录接口本身不带。
    if jwt:
        headers["oopz-signature"] = jwt
        headers["oopz-person"] = uid
    return headers


def http(method: str, path_with_query: str, body: str = "", jwt: str = "", uid: str = "") -> dict:
    """发送带签名与鉴权的请求，返回解析后的 JSON。"""
    ts = str(int(time.time() * 1000))
    req = urllib.request.Request(
        config.GATEWAY + path_with_query,
        data=body.encode("utf-8") if body else None,
        headers=_build_headers(path_with_query, body, ts, jwt, uid),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "replace")}
