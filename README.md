# oopz 每日任务

一个使用 Python 编写的 oopz 每日任务自动化脚本。脚本会登录账号，依次执行每日签到、打开商城和领取每日任务奖励，并可将执行结果发送到钉钉机器人。

## 功能

- 使用账号密码登录 oopz
- 自动生成请求签名和加密密码，无需安装第三方 Python 依赖
- 执行每日签到
- 打开商城（默认盲盒商城 ID 为 `6`）
- 领取每日任务奖励（默认任务 ID 为 `30003`）
- 获取当月签到详情
- 通过钉钉自定义机器人发送执行结果
- 支持 GitHub Actions 定时运行和手动触发

## 环境要求

- Python 3.9 及以上（GitHub Actions 使用 Python 3.11）
- 一个可正常登录 oopz 的账号
- 账号对应的 `OOPZ_DEVICE_ID`

项目仅使用 Python 标准库，不需要执行 `pip install`。

## 快速开始

### 1. 准备配置

复制示例配置文件：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，至少填写以下三个必填项：

```dotenv
OOPZ_PHONE=你的登录手机号
OOPZ_PASSWORD=你的登录密码
OOPZ_DEVICE_ID=你的设备ID
```

`.env` 已被 `.gitignore` 忽略，请不要把账号密码或机器人地址提交到仓库。

### 2. 获取设备 ID

设备 ID 必须与请求头中的 `oopz-device-id` 一致。可按以下方式从官方网页获取：

1. 打开 `https://web.oopz.cn` 并登录。
2. 按 `F12` 打开开发者工具，进入 **Network（网络）** 面板。
3. 刷新页面或执行一次需要登录的操作。
4. 在请求的 **Request Headers（请求标头）** 中找到 `oopz-device-id`，复制其值填入 `OOPZ_DEVICE_ID`。

如果网页端生成了新的设备 ID，应使用当前请求中实际出现的值。不要填写手机号、用户 ID 或 JWT。

### 3. 本地运行

在项目根目录执行：

```bash
python main.py
```

也可以临时通过环境变量运行，不创建 `.env` 文件：

```bash
OOPZ_PHONE=你的手机号 \
OOPZ_PASSWORD=你的密码 \
OOPZ_DEVICE_ID=你的设备ID \
python main.py
```

Windows PowerShell：

```powershell
$env:OOPZ_PHONE="你的手机号"
$env:OOPZ_PASSWORD="你的密码"
$env:OOPZ_DEVICE_ID="你的设备ID"
python main.py
```

程序会在终端打印每一步的接口返回结果，并以退出码 `0` 表示流程完成、退出码 `1` 表示启动配置或登录失败。

## 配置项

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `OOPZ_PHONE` | 是 | 无 | 登录手机号 |
| `OOPZ_PASSWORD` | 是 | 无 | 登录密码 |
| `OOPZ_DEVICE_ID` | 是 | 无 | 网页请求中的设备 ID |

## GitHub Actions 自动运行

仓库已包含 `.github/workflows/daily-task.yml`：

- 默认每天北京时间 05:20 执行（GitHub Actions 使用 UTC，配置为 `20 21 * * *`）。
- 支持在 Actions 页面点击 **Run workflow** 手动执行。

在 GitHub 仓库的 **Settings -> Secrets and variables -> Actions** 中添加以下 Repository secrets：

```text
OOPZ_PHONE
OOPZ_PASSWORD
OOPZ_DEVICE_ID
DINGTALK_WEBHOOK       # 可选
DINGTALK_SECRET        # 可选
```

提交代码并启用 Actions 后，无需常驻本地电脑即可按计划执行。GitHub Actions 的定时任务可能因平台排队出现延迟。

## 执行流程

```text
读取 .env / 环境变量
        |
        v
登录并获取 JWT、用户 ID
        |
        +--> 每日签到
        +--> 打开商城
        +--> 领取每日任务 30003
        +--> 获取当月签到详情
        |
        v
可选：发送钉钉通知
```

核心模块位于 `oopz/`：

- `config.py`：读取和校验运行配置
- `crypto.py`、`keys.py`：密码加密和请求签名
- `client.py`：统一 HTTP 请求及请求头构造
- `tasks.py`：登录、签到、商城和任务接口
- `notify.py`：钉钉机器人通知
- `main.py`：命令行入口和流程编排

## 常见问题

### 提示缺少必需的环境变量

确认 `.env` 位于项目根目录（与 `main.py` 同级），并检查变量名是否完全一致。也可以在当前终端中直接设置环境变量后重试。

### 登录失败或返回 HTTP 错误

检查手机号、密码和设备 ID 是否有效；确认网络可以访问 `https://gateway.oopz.cn`。如果网页端更新了客户端版本或请求格式，可能需要同步调整 `OOPZ_APP_VERSION` 或代码中的接口参数。

### 钉钉没有收到消息

确认 Webhook 未过期、机器人安全设置允许当前请求，并检查是否同时配置了正确的加签密钥。未配置 `DINGTALK_WEBHOOK` 时，脚本会正常执行但不会发送通知。

## 安全与使用说明

- `.env`、GitHub Secrets 和钉钉 Webhook 都属于敏感信息，请勿提交到公开仓库或粘贴到日志中。
- 设备 ID 和账号登录信息仅用于访问你有权使用的 oopz 账号。
- 请遵守 oopz 服务条款，合理设置运行频率；本项目不保证第三方接口长期稳定。

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。
