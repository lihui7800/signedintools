import asyncio
import sys
from typing import Dict, Any

# 导入自定义模块
from config_manager import ConfigManager
from browser_automation import BrowserAutomation
from login_module import LoginModule
from checkin_module import CheckInModule
from error_handler import ErrorHandler
from logger_setup import setup_logging


class JueJinCheckInSystem:
    """
    掘金自动签到系统主类
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化系统
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_manager = ConfigManager(config_path)
        if not self.config_manager.validate_config():
            raise ValueError("配置验证失败")
            
        # 设置日志
        log_config = self.config_manager.get_logging_config()
        self.logger = setup_logging(
            level=log_config.get('level', 'INFO'),
            file_path=log_config.get('file', 'juejin_checkin.log')
        )
        
        # 初始化错误处理器
        self.error_handler = ErrorHandler()
        
        # 获取浏览器设置
        browser_config = self.config_manager.get_browser_settings()
        self.browser_automation = BrowserAutomation(
            headless=browser_config.get('headless', True),
            timeout=browser_config.get('timeout', 30000)
        )
        
        # 获取账户信息（只需要cookies）
        self.cookies = self.config_manager.get_cookies()

        self.login_module = None
        self.checkin_module = None
        
    async def initialize(self):
        """
        初始化系统组件
        """
        try:
            self.logger.info("正在初始化浏览器...")
            await self.browser_automation.initialize()
            
            self.logger.info("初始化登录模块...")
            self.login_module = LoginModule(
                self.browser_automation,
                cookies=self.cookies
            )
            
            self.logger.info("初始化签到模块...")
            self.checkin_module = CheckInModule(self.browser_automation)
            
            self.logger.info("系统初始化完成")
        except Exception as e:
            self.logger.error(f"系统初始化失败: {str(e)}")
            raise
            
    async def run_check_in_process(self) -> Dict[str, Any]:
        """
        运行完整的签到流程
        
        Returns:
            包含执行结果的字典
        """
        result = {
            "login_success": False,
            "check_in_success": False,
            "continuous_days": 0,
            "error": None
        }
        
        try:
            # 执行登录
            self.logger.info("开始执行登录流程...")
            login_success = await self.error_handler.handle_error(self.login_module.perform_login)()
            result["login_success"] = login_success
            
            if not login_success:
                self.logger.error("登录失败，无法继续签到")
                result["error"] = "登录失败"
                return result
                
            self.logger.info("登录成功，开始执行签到流程...")
            
            # 检查当前签到状态
            check_in_status = await self.error_handler.handle_error(self.checkin_module.verify_check_in_status)()
            self.logger.info(f"当前签到状态 - 今日已签到: {check_in_status['today_signed']}, 连续签到天数: {check_in_status['continuous_days']}")
            
            result["continuous_days"] = check_in_status["continuous_days"]
            
            if check_in_status["today_signed"]:
                self.logger.info("今日已签到，无需重复签到")
                result["check_in_success"] = True
                return result
                
            # 执行签到
            check_in_success = await self.error_handler.handle_error(self.checkin_module.perform_check_in)()
            result["check_in_success"] = check_in_success
            
            if check_in_success:
                self.logger.info("签到成功")
                
                # 再次验证签到状态
                final_status = await self.error_handler.handle_error(self.checkin_module.verify_check_in_status)()
                if final_status["today_signed"]:
                    self.logger.info("签到状态验证成功")
                else:
                    self.logger.warning("签到后状态验证失败")
            else:
                self.logger.error("签到失败")
                result["error"] = "签到失败"
                
        except Exception as e:
            self.logger.error(f"签到流程执行失败: {str(e)}")
            result["error"] = str(e)
            
        return result
        
    async def close(self):
        """
        关闭系统资源
        """
        try:
            self.logger.info("正在关闭浏览器...")
            await self.browser_automation.close()
            self.logger.info("系统已关闭")
        except Exception as e:
            self.logger.error(f"关闭系统时出错: {str(e)}")
            
    async def run(self) -> Dict[str, Any]:
        """
        运行整个签到系统
        
        Returns:
            包含执行结果的字典
        """
        try:
            # 初始化系统
            await self.initialize()
            
            # 执行签到流程
            result = await self.run_check_in_process()
            
            return result
        finally:
            # 确保资源被释放
            await self.close()


async def main():
    """
    主函数
    """
    try:
        # 创建签到系统实例
        juejin_system = JueJinCheckInSystem()
        
        # 运行签到流程
        result = await juejin_system.run()
        
        # 输出结果
        print("\n=== 签到结果 ===")
        print(f"登录成功: {result['login_success']}")
        print(f"签到成功: {result['check_in_success']}")
        print(f"连续签到天数: {result['continuous_days']}")
        if result['error']:
            print(f"错误信息: {result['error']}")
        print("================")
        
        # 根据结果决定退出码
        if result['login_success'] and result['check_in_success']:
            sys.exit(0)  # 成功
        else:
            sys.exit(1)  # 失败
            
    except Exception as e:
        print(f"系统执行出错: {str(e)}")
        sys.exit(1)  # 失败


if __name__ == "__main__":
    asyncio.run(main())