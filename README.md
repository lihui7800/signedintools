# 掘金自动签到工具

![Build](https://github.com/<OWNER>/<REPO>/actions/workflows/build.yml/badge.svg)

> 使用前请将上方 `<OWNER>/<REPO>` 替换为你的 GitHub 用户名（或组织）和仓库名。

这是一个基于 Playwright 的掘金自动签到工具，支持 Cookie 自动管理和手动登录引导。

## 功能特性

- 🍪 **Cookie 自动管理**：优先使用 Cookie 登录，Cookie 过期时自动引导用户重新登录并更新
- 🔒 **安全登录方式**：不再使用账号密码登录，完全依赖 Cookie 认证
- 🔄 **智能状态检测**：自动检测登录状态，无需手动干预
- 📱 **多种登录方式**：支持微信扫码、账号密码等多种登录方式
- 🤖 **无头模式支持**：可在后台静默运行
- 📝 **完整日志记录**：详细的日志输出，便于调试和问题追踪
- ⚙️ **灵活配置**：支持浏览器模式、超时时间等自定义配置

## 工具要求

- Python 3.7+
- Playwright
- Chromium 浏览器

## 安装指南

1. 克隆或下载项目代码

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装 Playwright 浏览器：
   ```bash
   playwright install chromium
   ```

## 配置说明

编辑 `config/config.yaml` 文件：

```yaml
account:
  cookies: []              # Cookie 数组，首次运行时会自动引导登录并填充
                           # 示例格式：
                           # - name: "sessionid"
                           #   value: "your_session_value"
                           #   domain: ".juejin.cn"
                           #   path: "/"
                           #   expires: 1234567890

browser:
  headless: true           # 是否以无头模式运行 (true/false)
  timeout: 30000           # 页面操作超时时间（毫秒）

logging:
  level: "INFO"            # 日志级别 (DEBUG/INFO/WARNING/ERROR)
  file: "juejin_checkin.log"  # 日志文件路径
```

## 使用方法

### 首次使用（需要登录）

1. 直接运行自动签到程序：
   ```bash
   python main.py
   ```

2. 程序会自动打开浏览器并导航到掘金登录页面

3. 在浏览器中完成登录（支持微信扫码、账号密码等方式）

4. 登录完成后：
   - **自动检测**：程序会每 3 秒自动检测登录状态，检测到登录成功后自动继续
   - **手动继续**：也可以在终端按 `Ctrl+C` 立触继续

5. 程序会自动获取 Cookie 并保存到配置文件，然后执行签到

### 后续使用

配置文件中已有 Cookie 后，再次运行：
```bash
python main.py
```

程序会：
1. 使用配置中的 Cookie 自动登录
2. 检测登录状态
3. 如果 Cookie 过期，自动打开浏览器引导用户重新登录并更新 Cookie
4. 执行签到操作

## 登录流程详解

```
启动程序
    ↓
加载配置文件中的 Cookie
    ↓
设置 Cookie 并导航到掘金首页
    ↓
检查登录状态
    ↓
    ├─ 已登录 → 继续执行签到
    │
    └─ 未登录 → 打开浏览器引导用户登录
            ↓
        等待用户完成登录（最多30分钟）
            ↓
        检测到登录成功 → 获取新 Cookie
            ↓
        更新配置文件
            ↓
        继续执行签到
```

## 项目结构

```
├── config/                 # 配置文件目录
│   └── config.yaml        # 工具配置文件
├── config_manager.py       # 配置管理模块
├── browser_automation.py   # 浏览器自动化模块
├── login_module.py         # 登录模块（含 Cookie 管理）
├── checkin_module.py       # 签到模块
├── error_handler.py        # 错误处理模块
├── logger_setup.py         # 日志记录模块
├── main.py                # 主程序入口
├── test_modules.py         # 模块测试脚本
├── requirements.txt        # 依赖包列表
└── README.md              # 说明文档
```

## 注意事项

1. **Cookie 安全性**：配置文件中的 Cookie 是敏感信息，请妥善保管，不要泄露给他人
2. **Cookie 有效期**：Cookie 有过期时间，过期后程序会自动引导重新登录
3. **登录超时**：手动登录等待时间为 30 分钟，超时后程序会退出
4. **平台规则**：请遵守掘金平台的使用条款和用户协议
5. **运行频率**：建议合理设置签到频率，避免过于频繁的操作

## 定时任务设置

## GitHub 自动构建

项目已包含 GitHub Actions 工作流文件：`.github/workflows/build.yml`。

触发条件：
- 推送到 `main` 或 `master` 分支
- 任意 Pull Request

构建流程：
1. 使用 Python 3.10 / 3.11 / 3.12 矩阵构建
2. 安装 `requirements.txt` 依赖
3. 执行 `python -m compileall .` 进行语法构建检查

### Windows

使用任务计划程序创建每日运行的定时任务：

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（如每天上午 9:00）
4. 设置操作：启动程序 `python.exe`，参数为 `main.py`，起始目录为项目路径
5. 完成设置

### Linux/macOS

使用 cron 表达式设置定时任务：

编辑 crontab：
```bash
crontab -e
```

添加定时任务（每天上午 9:00 执行）：
```
0 9 * * * cd /path/to/project && /usr/bin/python3 main.py >> /path/to/project/cron.log 2>&1
```

## 常见问题

### 1. Cookie 过期了怎么办？

程序会自动检测 Cookie 是否有效。如果过期，会自动打开浏览器引导你重新登录，登录成功后会自动更新配置文件中的 Cookie。

### 2. 浏览器无法显示微信二维码？

请确保配置文件中 `browser.headless` 设置为 `false`，这样浏览器会以可视模式运行。程序已优化为非阻塞模式，不会影响二维码显示。

### 3. 如何查看运行日志？

日志保存在配置文件中指定的路径（默认为 `juejin_checkin.log`），可以直接查看该文件了解运行详情。

### 4. 如何调试问题？

将配置文件中 `logging.level` 设置为 `DEBUG`，可以获得更详细的日志输出。

## 维护与更新

- 定期检查日志文件了解运行状况
- 如掘金网站界面发生变化，可能需要更新选择器
- 保持依赖包的更新：`pip install -r requirements.txt --upgrade`
- 更新 Playwright 浏览器：`playwright install chromium --force`

## 开发说明

### 模块说明

- **config_manager.py**：负责配置文件的读取、验证和更新
- **browser_automation.py**：封装 Playwright 浏览器操作
- **login_module.py**：处理登录逻辑、Cookie 管理和登录状态检测
- **checkin_module.py**：执行签到操作和签到状态验证
- **error_handler.py**：统一的错误处理和重试机制
- **logger_setup.py**：日志工具配置和初始化

### 扩展开发

如需添加新功能或修改现有功能，建议遵循以下原则：
1. 保持模块间的职责分离
2. 添加适当的日志记录
3. 完善错误处理
4. 更新相关文档

## License

MIT License