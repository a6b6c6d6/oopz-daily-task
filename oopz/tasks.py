"""每日任务业务逻辑：登录、签到、打开商店、领取任务。"""

import json

from . import config, crypto, client

LOGIN_PATH = "/client/v1/login/v2/login"


def login() -> tuple[str, str]:
    """登录，返回 (jwt, uid)。"""
    code = crypto.encrypt_password(config.PASSWORD)
    body = json.dumps(
        {
            "auto": True,
            "autoRegister": True,
            "clientVersion": "0.85.914",
            "code": code,
            "deviceId": config.DEVICE_ID,
            "deviceProcessor": "0",
            "deviceRam": "TBD",
            "graphics": "TBD",
            "loggedIn": config.DEVICE_ID,
            "loginType": "PASSWORD",
            "osEdition": "web",
            "osVersion": "web/_BrowserName.edge",
            "phone": config.PHONE,
            "resolution": "TBD",
        },
        separators=(",", ":"),
    )
    result = client.http("POST", LOGIN_PATH, body)
    if result.get("status"):
        data = result["data"]
        return data["signature"], data["uid"]
    raise RuntimeError("登录失败: " + json.dumps(result, ensure_ascii=False))


def get_monthly_detail(jwt: str, uid: str) -> dict:
    """签到详情（含签到状态与每日任务列表）。"""
    return client.http("GET", "/uni/activity/monthlyTask/v1/detail", jwt=jwt, uid=uid)


def sign_in(jwt: str, uid: str) -> dict:
    """每日签到（body 为 {}）。"""
    return client.http("POST", "/uni/activity/monthlyTask/v1/signIn", "{}", jwt, uid)


def open_shop(jwt: str, uid: str, blind_box_id: int = 6) -> dict:
    """打开商店（每日任务「进入商城」的前置）。"""
    return client.http(
        "GET", f"/uni/blind_box_rank/v1/entry?blindBoxID={blind_box_id}", jwt=jwt, uid=uid
    )


def claim_daily_task(jwt: str, uid: str, task_id: int = 30003) -> dict:
    """领取每日任务奖励。task_id=30003 即「进入商城」。"""
    body = json.dumps({"taskId": task_id}, separators=(",", ":"))
    return client.http(
        "POST", "/uni/activity/dailyTask/v1/reward/claim", body, jwt, uid
    )
