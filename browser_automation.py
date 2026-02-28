import asyncio
from playwright.async_api import async_playwright
from typing import Optional
import logging


class BrowserAutomation:
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        初始化浏览器自动化类
        
        Args:
            headless: 是否以无头模式运行
            timeout: 页面操作超时时间（毫秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.page = None
        self.playwright_instance = None
        
    async def initialize(self):
        """
        初始化浏览器实例
        """
        try:
            self.playwright_instance = await async_playwright().start()
            self.browser = await self.playwright_instance.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            self.page = await self.browser.new_page()
            
            # 设置页面默认超时
            self.page.set_default_timeout(self.timeout)
            
            # 修改navigator.webdriver属性，避免被检测为自动化工具
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            logging.info("浏览器初始化成功")
        except Exception as e:
            logging.error(f"浏览器初始化失败: {str(e)}")
            raise
            
    async def set_cookies(self, cookies: list):
        """
        设置浏览器Cookies

        Args:
            cookies: Cookie列表
        """
        try:
            if cookies:
                await self.page.context.add_cookies(cookies)
                logging.info(f"成功设置 {len(cookies)} 个Cookie")
            else:
                logging.info("没有提供Cookie，跳过设置")
        except Exception as e:
            logging.error(f"设置Cookie失败: {str(e)}")
            raise

    async def get_cookies(self) -> list:
        """
        获取浏览器Cookies

        Returns:
            Cookie列表
        """
        try:
            cookies = await self.page.context.cookies()
            logging.info(f"成功获取 {len(cookies)} 个Cookie")
            return cookies
        except Exception as e:
            logging.error(f"获取Cookie失败: {str(e)}")
            return []
            
    async def navigate_to_url(self, url: str):
        """
        导航到指定URL
        
        Args:
            url: 目标URL
        """
        try:
            await self.page.goto(url, wait_until="networkidle")
            logging.info(f"成功导航到: {url}")
        except Exception as e:
            logging.error(f"导航到 {url} 失败: {str(e)}")
            raise
            
    async def close(self):
        """
        关闭浏览器实例
        """
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright_instance:
                await self.playwright_instance.stop()
            logging.info("浏览器已关闭")
        except Exception as e:
            logging.error(f"关闭浏览器时出错: {str(e)}")
            
    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> Optional[str]:
        """
        等待页面元素出现
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            元素是否存在
        """
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            return element is not None
        except:
            return False
            
    async def click_element(self, selector: str):
        """
        点击页面元素
        
        Args:
            selector: 元素选择器
        """
        try:
            element = await self.page.wait_for_selector(selector, state="visible")
            await element.click()
            logging.info(f"成功点击元素: {selector}")
        except Exception as e:
            logging.error(f"点击元素 {selector} 失败: {str(e)}")
            raise
            
    async def fill_input(self, selector: str, text: str):
        """
        填充输入框
        
        Args:
            selector: 输入框选择器
            text: 要填充的文本
        """
        try:
            element = await self.page.wait_for_selector(selector, state="visible")
            await element.fill(text)
            logging.info(f"成功填充输入框 {selector} 为: {text}")
        except Exception as e:
            logging.error(f"填充输入框 {selector} 失败: {str(e)}")
            raise
            
    async def get_element_text(self, selector: str) -> str:
        """
        获取元素文本内容
        
        Args:
            selector: 元素选择器
            
        Returns:
            元素文本内容
        """
        try:
            element = await self.page.wait_for_selector(selector, state="visible")
            text = await element.text_content()
            return text.strip() if text else ""
        except Exception as e:
            logging.error(f"获取元素 {selector} 文本失败: {str(e)}")
            return ""
            
    async def screenshot(self, path: str):
        """
        截图保存
        
        Args:
            path: 截图保存路径
        """
        try:
            await self.page.screenshot(path=path)
            logging.info(f"截图已保存至: {path}")
        except Exception as e:
            logging.error(f"截图失败: {str(e)}")


# 示例用法
async def main():
    browser_auto = BrowserAutomation(headless=False, timeout=30000)
    try:
        await browser_auto.initialize()
        await browser_auto.navigate_to_url("https://www.baidu.com")
        await asyncio.sleep(2)  # 等待页面加载
        await browser_auto.screenshot("example_screenshot.png")
    finally:
        await browser_auto.close()


if __name__ == "__main__":
    asyncio.run(main())