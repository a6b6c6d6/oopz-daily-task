#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oopz 每日任务入口。

流程：自动登录 → 拿最新 JWT → 签到 → 打开商店 → 领取每日任务 → 钉钉通知。

用法：
    OOPZ_PHONE=xxx OOPZ_PASSWORD=xxx OOPZ_DEVICE_ID=xxx python main.py
"""

import json
import sys

from oopz import config, notify, tasks


def _status_text(result: dict) -> str:
    if result.get("status") is True:
        return "成功"
    if "_http_error" in result:
        return f"HTTP {result['_http_error']}"
    msg = str(result.get("message") or result.get("code") or "失败")
    if "重复" in msg:
        return "今日已完成"
    return msg


def _print(title: str, result: dict) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(result, ensure_ascii=False)[:700])


def run() -> int:
    try:
        config.assert_configured()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    lines = ["【oopz 每日任务】"]

    print("登录中...")
    try:
        jwt, uid = tasks.login()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        notify.send_text("\n".join(lines + [f"登录: 失败 {exc}"]))
        return 1
    print(f"登录成功, uid = {uid}")
    lines.append("登录: 成功")

    steps = [
        ("签到", tasks.sign_in),
        ("打开商店", tasks.open_shop),
        ("领取任务30003", tasks.claim_daily_task),
    ]
    for title, fn in steps:
        result = fn(jwt, uid)
        _print(title, result)
        lines.append(f"{title}: {_status_text(result)}")

    _print("签到详情", tasks.get_monthly_detail(jwt, uid))

    content = "\n".join(lines)
    if notify.enabled():
        sent = notify.send_text(content)
        print("\n钉钉通知:", "已发送" if sent else "发送失败")
    else:
        print("\n钉钉通知: 未配置")
    return 0


if __name__ == "__main__":
    sys.exit(run())
