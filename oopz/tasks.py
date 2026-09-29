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
    if "_http_error" in result:
        raise RuntimeError(f"HTTP {result['_http_error']}")
    raise RuntimeError(str(result.get("message") or result.get("code") or "未知错误"))


def get_monthly_detail(jwt: str, uid: str) -> dict:
    """签到详情（含签到状态与每日任务列表）。"""
    return client.http("GET", "/uni/activity/monthlyTask/v1/detail", jwt=jwt, uid=uid)


def sign_in(jwt: str, uid: str) -> dict:
    """每日签到（body 为 {}）。"""
    return client.http("POST", "/uni/activity/monthlyTask/v1/signIn", "{}", jwt, uid)


def open_shop(jwt: str, uid: str, tab_type: str = "FEATURE") -> dict:
    """打开商城 —— 每日任务「进入一次商城」的触发动作。

    该任务在月度活动详情里的定义是：
        taskId=30003, taskType=ENTER_SHOP, uri=oopz://oopz.route/mall/browser
    对应的接口就是 GET /uni/shop/v1/mall，必须调它服务端才会记录进度。

    注意：旧版这里调用的是 /uni/blind_box_rank/v1/entry（盲盒排行榜入口）。
    那个接口仍然存在并且返回 200，但它属于排行榜模块，不会推进 ENTER_SHOP
    任务，任务会一直停在 state=0，随后领奖时返回
    「不满足领取条件」（ERR.022.00002）。
    """
    return client.http("GET", f"/uni/shop/v1/mall?tabType={tab_type}", jwt=jwt, uid=uid)


def claim_daily_task(jwt: str, uid: str, task_id: int = 30003) -> dict:
    """领取每日任务奖励。task_id=30003 即「进入商城」。"""
    body = json.dumps({"taskId": task_id}, separators=(",", ":"))
    return client.http(
        "POST", "/uni/activity/dailyTask/v1/reward/claim", body, jwt, uid
    )
