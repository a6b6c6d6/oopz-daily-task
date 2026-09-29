#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oopz 接口诊断脚本（只读探测，不修改任何账号数据）。

用法：在项目根目录（与 main.py 同级）执行

    python diagnose.py

前置：.env 已按 .env.example 填好 OOPZ_PHONE / OOPZ_PASSWORD / OOPZ_DEVICE_ID。

结果判读（重要）：
    200                    -> 通道正常
    428 + TencentEdgeOne   -> oopz 网关的「未登录 / 路径不被允许」统一拒绝码
    404                    -> 路径已下线，接口确实换了
    200 但 status=false    -> 接口在，业务侧拒绝，看 message

脚本先用一个公开接口 /uni/sidebar/v1/menus 做基线：
它不需要登录，正常情况一定返回 200；若它也 428，说明是网络或客户端特征问题。
"""

import json
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

from oopz import client, config, tasks


def probe(title: str, method: str, path: str, body: str, jwt: str, uid: str) -> int:
    ts = str(int(time.time() * 1000))
    req = urllib.request.Request(
        config.GATEWAY + path,
        data=body.encode("utf-8") if body else None,
        headers=client._build_headers(path, body, ts, jwt, uid),
        method=method,
    )
    server = "-"
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            code, headers, text = resp.status, resp.headers, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        code, headers, text = exc.code, exc.headers, exc.read().decode("utf-8", "replace")
    except Exception as exc:
        code, headers, text = "ERR", {}, f"{type(exc).__name__}: {exc}"

    if headers:
        server = headers.get("Server", "-") or "-"

    print(f"--- {title}")
    print(f"    {method} {path}")
    print(f"    HTTP {code} | Server: {server}")
    print(f"    body: {text[:300]}")
    print()
    return code if isinstance(code, int) else -1


def main() -> int:
    try:
        config.assert_configured()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f" gateway       : {config.GATEWAY}")
    print(f" app_version   : {config.APP_VERSION}   (当前前端实际版本为 88053)")
    print(f" device_id     : {config.DEVICE_ID[:8]}…\n")

    print("=" * 70)
    print("基线：公开接口（不需要登录，正常应为 200）")
    print("=" * 70)
    base = probe("公开菜单接口", "GET", "/uni/sidebar/v1/menus", "", "", "")
    if base == 428:
        print("!! 连公开接口都 428：属于网络 / 客户端特征问题，先解决这一层。\n")

    print("登录中...")
    try:
        jwt, uid = tasks.login()
    except RuntimeError as exc:
        print("登录失败:", exc, file=sys.stderr)
        return 1
    print(f"登录成功, uid = {uid}\n")

    print("=" * 70)
    print("登录后：商城类接口 —— 本次故障重点")
    print("=" * 70)
    probe("★ 商城主页（当前前端在用）", "GET", "/uni/shop/v1/mall?tabType=0&subtab=0", "", jwt, uid)
    probe("商城主页（不带参数）", "GET", "/uni/shop/v1/mall", "", jwt, uid)
    probe("★ 盲盒排行入口（脚本现用，疑似已下线）", "GET", "/uni/blind_box_rank/v1/entry?blindBoxID=6", "", jwt, uid)
    probe("盲盒排行列表", "GET", "/uni/blind_box_rank/v1/list?blindBoxID=6", "", jwt, uid)
    probe("背包列表", "GET", "/uni/backpack/v1/list?tabType=0&page=1&pageSize=10", "", jwt, uid)

    print("=" * 70)
    print("登录后：活动 / 签到类接口")
    print("=" * 70)
    probe("当月任务详情（脚本现用）", "GET", "/uni/activity/monthlyTask/v1/detail", "", jwt, uid)
    probe("会员资料", "GET", "/uni/member/v1/profile", "", jwt, uid)
    probe("会员等级配置（公开）", "GET", "/uni/member/v1/level/config", "", jwt, uid)

    print("=" * 70)
    print("完成。把上面全部输出复制回来即可定位。")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
