import asyncio
from typing import Dict
import logging
from browser_automation import BrowserAutomation


class CheckInModule:
    def __init__(self, browser_automation: BrowserAutomation):
        """
        初始化签到模块
        
        Args:
            browser_automation: 浏览器自动化实例
        """
        self.browser = browser_automation
        
    async def perform_check_in(self) -> bool:
        """
        执行签到流程
        
        Returns:
            签到是否成功
        """
        try:
            # 导航到掘金首页
            logging.info("正在导航到掘金首页...")
            await self.browser.navigate_to_url("https://juejin.cn/")
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 查找签到相关按钮或链接
            # 尝试多种可能的选择器
            sign_in_selectors = [
                "text=签到",
                "text=立即签到",
                ".sign-btn",
                "[data-type='sign']",
                ".signin-button",
                "text=补签",
                ".checkin-btn"
            ]
            
            sign_in_found = False
            for selector in sign_in_selectors:
                if await self.browser.wait_for_selector(selector, timeout=5000):
                    # 检查按钮是否可用（未禁用）
                    element = await self.browser.page.query_selector(selector)
                    if element:
                        is_disabled = await element.is_disabled() if hasattr(element, 'is_disabled') else False
                        if not is_disabled:
                            await self.browser.click_element(selector)
                            sign_in_found = True
                            logging.info(f"找到并点击签到按钮: {selector}")
                            
                            # 等待签到结果反馈
                            await asyncio.sleep(2)
                            
                            # 检查是否有签到成功的提示
                            success_messages = [
                                "签到成功",
                                "已签到",
                                "打卡成功",
                                ".success-message"
                            ]
                            
                            for msg_selector in success_messages:
                                if await self.browser.wait_for_selector(msg_selector, timeout=3000):
                                    logging.info("检测到签到成功消息")
                                    return True
                                    
                            # 如果没有立即看到成功消息，再等一会儿
                            await asyncio.sleep(3)
                            
                            # 再次检查成功消息
                            for msg_selector in success_messages:
                                if await self.browser.wait_for_selector(msg_selector, timeout=3000):
                                    logging.info("检测到签到成功消息")
                                    return True
                                    
                            logging.info("已点击签到按钮，但未检测到明确的成功消息，可能已签到")
                            return True
                            
            if not sign_in_found:
                # 尝试通过掘金的特定签到页面
                logging.info("未找到签到按钮，尝试访问签到页面")
                await self.browser.navigate_to_url("https://juejin.cn/checkin/index")
                
                await asyncio.sleep(3)
                
                # 在签到页面查找签到按钮
                checkin_page_selectors = [
                    "text=签到",
                    "text=立即签到",
                    ".btn-sign",
                    "[data-action='sign']",
                    ".checkin-btn"
                ]
                
                for selector in checkin_page_selectors:
                    if await self.browser.wait_for_selector(selector, timeout=5000):
                        await self.browser.click_element(selector)
                        logging.info(f"在签到页面找到并点击按钮: {selector}")
                        
                        # 等待签到结果
                        await asyncio.sleep(3)
                        
                        # 检查签到成功消息
                        success_messages = [
                            "签到成功",
                            "已签到",
                            "打卡成功",
                            ".success-message"
                        ]
                        
                        for msg_selector in success_messages:
                            if await self.browser.wait_for_selector(msg_selector, timeout=3000):
                                logging.info("检测到签到成功消息")
                                return True
                                
                        logging.info("已点击签到按钮，但未检测到明确的成功消息")
                        return True
                        
                logging.warning("在签到页面也未找到签到按钮")
                
            return False
            
        except Exception as e:
            logging.error(f"签到过程中发生错误: {str(e)}")
            return False
            
    async def verify_check_in_status(self) -> Dict[str, bool]:
        """
        验证签到状态
        
        Returns:
            包含签到状态的字典
        """
        try:
            # 导航到个人中心或签到页面查看状态
            await self.browser.navigate_to_url("https://juejin.cn/checkin/index")
            await asyncio.sleep(2)
            
            # 检查今天是否已经签到
            today_signed_selectors = [
                "text=已签到",
                ".signed-today",
                "[data-signed='true']"
            ]
            
            today_signed = False
            for selector in today_signed_selectors:
                if await self.browser.wait_for_selector(selector, timeout=3000):
                    today_signed = True
                    break
                    
            # 检查连续签到天数
            continuous_days = 0
            days_selectors = [
                ".continuous-days",
                "[data-days]",
                "text=/连续签到\\d+天/"
            ]
            
            for selector in days_selectors:
                if await self.browser.wait_for_selector(selector, timeout=3000):
                    text = await self.browser.get_element_text(selector)
                    # 提取数字
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        continuous_days = int(numbers[0])
                        break
                        
            return {
                "today_signed": today_signed,
                "continuous_days": continuous_days
            }
            
        except Exception as e:
            logging.error(f"验证签到状态时发生错误: {str(e)}")
            return {"today_signed": False, "continuous_days": 0}


# 示例用法
async def main():
    from browser_automation import BrowserAutomation
    
    # 初始化浏览器
    browser_auto = BrowserAutomation(headless=False, timeout=30000)
    await browser_auto.initialize()
    
    try:
        # 初始化签到模块
        checkin_module = CheckInModule(browser_auto)
        
        # 验证当前签到状态
        status = await checkin_module.verify_check_in_status()
        print(f"今日已签到: {status['today_signed']}, 连续签到天数: {status['continuous_days']}")
        
        # 执行签到
        if not status['today_signed']:
            success = await checkin_module.perform_check_in()
            print(f"签到{'成功' if success else '失败'}")
        else:
            print("今日已签到")
            
    finally:
        await browser_auto.close()


if __name__ == "__main__":
    asyncio.run(main())