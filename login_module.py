import asyncio
import logging
from browser_automation import BrowserAutomation
from config_manager import ConfigManager


class LoginModule:
    def __init__(self, browser_automation: BrowserAutomation, cookies: list = None):
        """
        初始化登录模块

        Args:
            browser_automation: 浏览器自动化实例
            cookies: Cookie列表
        """
        self.browser = browser_automation
        self.cookies = cookies or []
        self.config_manager = ConfigManager()

    async def check_login_status(self) -> bool:
        """
        检查当前登录状态

        Returns:
            是否已登录
        """
        try:
            success_indicators = [
                ".avatar-wrapper",
                ".logout"
            ]

            for selector in success_indicators:
                if await self.browser.wait_for_selector(selector, timeout=3000):
                    logging.info("检测到已登录状态")
                    return True

            logging.info("未检测到登录状态")
            return False

        except Exception as e:
            logging.error(f"检查登录状态时发生错误: {str(e)}")
            return False

    async def setup_cookies_and_navigate(self) -> bool:
        """
        设置Cookie并导航到掘金首页

        Returns:
            设置和导航是否成功
        """
        try:
            # 设置Cookie
            if self.cookies:
                await self.browser.set_cookies(self.cookies)
                logging.info(f"已设置 {len(self.cookies)} 个Cookie")

            # 导航到掘金首页
            logging.info("正在导航到掘金首页...")
            await self.browser.navigate_to_url("https://juejin.cn/")

            # 等待页面加载
            await asyncio.sleep(3)

            return True

        except Exception as e:
            logging.error(f"设置Cookie和导航时发生错误: {str(e)}")
            return False

    async def guide_manual_login(self) -> bool:
        """
        引导用户手动登录，并获取更新后的Cookies

        Returns:
            是否成功获取并更新Cookies
        """
        try:
            logging.info("========================================")
            logging.info("当前未登录，请手动登录掘金账号")
            logging.info("========================================")

            # 使用非阻塞方式等待用户登录
            logging.info("请在浏览器中完成登录操作")
            logging.info("支持扫码登录或账号密码登录")
            logging.info("登录完成后，请按 Ctrl+C 继续程序...")

            # 等待用户手动登录，循环检测登录状态
            max_wait_minutes = 30  # 最多等待30分钟
            check_interval = 3      # 每3秒检查一次登录状态
            max_checks = (max_wait_minutes * 60) // check_interval

            check_count = 0
            while check_count < max_checks:
                try:
                    # 检查登录状态
                    is_logged_in = await self.check_login_status()
                    if is_logged_in:
                        logging.info("检测到登录成功！")

                        # 获取新的cookies
                        logging.info("正在从浏览器获取Cookies...")
                        cookies = await self.browser.get_cookies()

                        if cookies:
                            logging.info(f"成功获取 {len(cookies)} 个Cookies")

                            # 更新配置文件
                            self.config_manager.update_cookies(cookies)
                            logging.info("Cookies已更新到配置文件")

                            # 更新当前cookies
                            self.cookies = cookies

                            return True
                        else:
                            logging.error("未能获取到任何Cookies")
                            return False

                    # 未登录，继续等待
                    check_count += 1
                    if check_count % 10 == 0:  # 每30秒输出一次等待提示
                        elapsed = check_count * check_interval
                        logging.info(f"等待登录中... 已等待 {elapsed} 秒")

                    await asyncio.sleep(check_interval)

                except KeyboardInterrupt:
                    # 用户按 Ctrl+C，检测是否已登录
                    logging.info("收到中断信号，检查登录状态...")
                    is_logged_in = await self.check_login_status()

                    if is_logged_in:
                        # 获取新的cookies
                        logging.info("正在从浏览器获取Cookies...")
                        cookies = await self.browser.get_cookies()

                        if cookies:
                            logging.info(f"成功获取 {len(cookies)} 个Cookies")

                            # 更新配置文件
                            self.config_manager.update_cookies(cookies)
                            logging.info("Cookies已更新到配置文件")

                            # 更新当前cookies
                            self.cookies = cookies

                            return True
                        else:
                            logging.error("未能获取到任何Cookies")
                            return False
                    else:
                        logging.warning("检测到登录未完成，继续等待...")

            # 超时
            logging.error(f"等待登录超时（{max_wait_minutes}分钟），程序终止")
            return False

        except Exception as e:
            logging.error(f"引导手动登录过程中发生错误: {str(e)}")
            return False

    async def perform_login(self) -> bool:
        """
        执行登录流程：
        1. 根据配置中的Cookie启动浏览器
        2. 检查登录状态
        3. 如果未登录，引导用户手动登录并更新Cookie
        4. 验证登录成功

        Returns:
            登录是否成功
        """
        try:
            # 步骤1：设置Cookie并导航到掘金首页
            setup_success = await self.setup_cookies_and_navigate()
            if not setup_success:
                logging.error("设置Cookie和导航失败")
                return False

            # 步骤2：检查登录状态
            is_logged_in = await self.check_login_status()

            # 步骤3：如果未登录，引导用户手动登录
            if not is_logged_in:
                logging.info("Cookie无效或已过期，需要重新登录")

                # 引导用户手动登录并获取新Cookie
                manual_login_success = await self.guide_manual_login()
                if not manual_login_success:
                    logging.error("手动登录失败")
                    return False

                # 使用新Cookie再次验证登录状态
                logging.info("正在验证新Cookie的登录状态...")
                await asyncio.sleep(2)
                is_logged_in = await self.check_login_status()

                if not is_logged_in:
                    logging.error("新Cookie验证失败，请检查登录是否成功")
                    return False

            # 步骤4：登录成功
            logging.info("========================================")
            logging.info("登录验证成功，可以继续执行签到操作")
            logging.info("========================================")
            return True

        except Exception as e:
            logging.error(f"登录流程执行失败: {str(e)}")
            return False


# 示例用法
async def main():
    # 加载配置
    config_manager = ConfigManager()
    cookies = config_manager.get_cookies()

    # 初始化浏览器
    browser_auto = BrowserAutomation(headless=False, timeout=30000)
    await browser_auto.initialize()

    try:
        # 初始化登录模块（只传入cookies）
        login_module = LoginModule(browser_auto, cookies=cookies)

        # 执行登录
        success = await login_module.perform_login()
        print(f"登录{'成功' if success else '失败'}")

    finally:
        await browser_auto.close()


if __name__ == "__main__":
    asyncio.run(main())