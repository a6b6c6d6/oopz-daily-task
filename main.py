#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oopz 每日任务入口。

流程：自动登录 → 拿最新 JWT → 签到 → 打开商店 → 领取每日任务 → 钉钉通知。

用法：
    OOPZ_PHONE=xxx OOPZ_PASSWORD=xxx OOPZ_DEVICE_ID=xxx python main.py
"""

import datetime
import json
import sys

from oopz import config, notify, tasks


def _status_text(result: dict) -> str:
    if result.get("status") is True:
        return "成功"
    if "_http_error" in result:
        return f"失败（HTTP {result['_http_error']}）"
    msg = str(result.get("message") or "").strip()
    if "重复" in msg:
        return "今日已完成"
    reason = msg or str(result.get("code") or "未知错误")
    if len(reason) > 40:
        reason = reason[:40] + "…"
    return f"失败（{reason}）"


def _format_notify(entries: list) -> str:
    """生成钉钉通知文本。entries = [(步骤, 状态), ...]"""
    date = datetime.date.today().strftime("%m/%d")
    lines = [f"【oopz 每日任务】{date}"]
    for title, status in entries:
        ok = "成功" in status or "已完成" in status
        lines.append(f"{'✅' if ok else '❌'} {title}：{status}")
    return "\n".join(lines)


def _print(title: str, result: dict) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(result, ensure_ascii=False)[:700])


def run() -> int:
    try:
        config.assert_configured()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    entries: list = []

    print("登录中...")
    try:
        jwt, uid = tasks.login()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        entries.append(("登录", f"失败（{exc}）"))
        notify.send_text(_format_notify(entries))
        return 1
    print(f"登录成功, uid = {uid}")
    entries.append(("登录", "成功"))

    steps = [
        ("签到", tasks.sign_in),
        ("打开商店", tasks.open_shop),
        ("领取每日任务", tasks.claim_daily_task),
    ]
    for title, fn in steps:
        result = fn(jwt, uid)
        _print(title, result)
        entries.append((title, _status_text(result)))

    _print("签到详情", tasks.get_monthly_detail(jwt, uid))

    if notify.enabled():
        sent = notify.send_text(_format_notify(entries))
        print("\n钉钉通知:", "已发送" if sent else "发送失败")
    else:
        print("\n钉钉通知: 未配置")
    return 0


if __name__ == "__main__":
    sys.exit(run())
