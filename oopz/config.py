"""运行配置：所有敏感信息从环境变量读取，避免硬编码泄露。

本地开发：复制 .env.example 为 .env 并在其中填写，或用 export 设置。
GitHub Actions：在仓库 Settings → Secrets 中配置，workflow 里注入。
"""

import os


def _load_dotenv(path: str = ".env") -> None:
    """零依赖加载 .env（若存在），不覆盖已设置的环境变量。"""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError:
        pass


_load_dotenv()

# 网关地址（一般无需修改）
GATEWAY = os.environ.get("OOPZ_GATEWAY", "https://gateway.oopz.cn")

# 登录手机号（敏感，走环境变量 / GitHub Secrets）
PHONE = os.environ.get("OOPZ_PHONE", "")

# 登录密码（敏感，走环境变量 / GitHub Secrets）
PASSWORD = os.environ.get("OOPZ_PASSWORD", "")

# 设备标识（必填，需自行获取，见 README「获取设备ID」）
DEVICE_ID = os.environ.get("OOPZ_DEVICE_ID", "")

# 客户端版本号（对应 oopz-app-version-number 头）
APP_VERSION = os.environ.get("OOPZ_APP_VERSION", "85914")

# 平台 / 渠道
PLATFORM = os.environ.get("OOPZ_PLATFORM", "windows")
CHANNEL = os.environ.get("OOPZ_CHANNEL", "Web")

# 钉钉群机器人通知（可选，不配置则不发送）
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK", "")
DINGTALK_SECRET = os.environ.get("DINGTALK_SECRET", "")


def assert_configured() -> None:
    """启动前校验必需的环境变量是否已配置。"""
    required = (
        ("OOPZ_PHONE", PHONE),
        ("OOPZ_PASSWORD", PASSWORD),
        ("OOPZ_DEVICE_ID", DEVICE_ID),
    )
    missing = [name for name, val in required if not val]
    if missing:
        raise RuntimeError(
            "缺少必需的环境变量: " + ", ".join(missing)
            + "。请参考 .env.example 配置后再运行。"
        )
