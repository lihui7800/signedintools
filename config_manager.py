import yaml
import os
import logging
from typing import Dict, Any


class ConfigManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config_data = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置数据字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
        
    def validate_config(self) -> bool:
        """
        验证配置项

        Returns:
            配置是否有效
        """
        required_keys = ['account', 'browser', 'logging']
        for key in required_keys:
            if key not in self.config_data:
                print(f"缺少必需的配置项: {key}")
                return False

        return True
        
    def get_account_info(self) -> Dict[str, str]:
        """
        获取账户信息
        
        Returns:
            包含用户名和密码的字典
        """
        account = self.config_data.get('account', {})
        return {
            'username': account.get('username'),
            'password': account.get('password')
        }
        
    def get_cookies(self) -> list:
        """
        获取Cookie信息
        
        Returns:
            Cookie列表
        """
        account = self.config_data.get('account', {})
        return account.get('cookies', [])

    def update_cookies(self, cookies: list):
        """
        更新配置文件中的Cookies
        
        Args:
            cookies: 新的Cookie列表
        """
        import yaml
        # 更新内存中的配置
        self.config_data['account']['cookies'] = cookies
        
        # 保存到文件
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config_data, file, default_flow_style=False, allow_unicode=True)
        logging.info(f"Cookies已更新到配置文件: {self.config_path}")
        
    def get_browser_settings(self) -> Dict[str, Any]:
        """
        获取浏览器设置
        
        Returns:
            浏览器配置参数
        """
        return self.config_data.get('browser', {})
        
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置参数
        """
        return self.config_data.get('logging', {})


# 示例用法
if __name__ == "__main__":
    config_manager = ConfigManager()
    if config_manager.validate_config():
        print("配置加载成功")
        print("账户信息:", config_manager.get_account_info())
        print("浏览器设置:", config_manager.get_browser_settings())
        print("日志配置:", config_manager.get_logging_config())
    else:
        print("配置验证失败")