import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class LogConfig:
    """日志配置类"""
    
    def __init__(self, level: str = "INFO", file_path: str = "juejin_checkin.log", max_bytes: int = 10485760, backup_count: int = 5):
        """
        初始化日志配置
        
        Args:
            level: 日志级别
            file_path: 日志文件路径
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 保留的日志文件数量
        """
        self.level = getattr(logging, level.upper())
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count


class LoggerSetup:
    """日志设置类"""
    
    def __init__(self, config: LogConfig):
        """
        初始化日志设置
        
        Args:
            config: 日志配置对象
        """
        self.config = config
        self.logger = None
        self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        # 创建logger
        self.logger = logging.getLogger('JueJinCheckIn')
        self.logger.setLevel(self.config.level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.config.level)
        
        # 创建文件处理器（带轮转功能）
        file_dir = os.path.dirname(self.config.file_path)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir)
            
        file_handler = RotatingFileHandler(
            self.config.file_path,
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.config.level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 为处理器设置格式化器
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
    def get_logger(self) -> logging.Logger:
        """
        获取配置好的日志记录器
        
        Returns:
            配置好的日志记录器
        """
        return self.logger


def setup_logging(level: str = "INFO", file_path: str = "juejin_checkin.log") -> logging.Logger:
    """
    快速设置日志记录器
    
    Args:
        level: 日志级别
        file_path: 日志文件路径
        
    Returns:
        配置好的日志记录器
    """
    config = LogConfig(level=level, file_path=file_path)
    logger_setup = LoggerSetup(config)
    return logger_setup.get_logger()


def log_function_call(logger: logging.Logger):
    """
    装饰器：记录函数调用
    
    Args:
        logger: 日志记录器
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"调用函数: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                raise
        return wrapper
    return decorator


def log_async_function_call(logger: logging.Logger):
    """
    异步装饰器：记录异步函数调用
    
    Args:
        logger: 日志记录器
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger.info(f"调用异步函数: {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"异步函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                logger.error(f"异步函数 {func.__name__} 执行失败: {str(e)}")
                raise
        return wrapper
    return decorator


# 示例用法
if __name__ == "__main__":
    # 设置日志
    logger = setup_logging(level="INFO", file_path="test_log.log")
    
    # 记录一些日志
    logger.info("日志系统初始化成功")
    logger.warning("这是一个警告消息")
    logger.error("这是一个错误消息")
    
    # 测试装饰器
    @log_function_call(logger)
    def test_function():
        print("执行测试函数")
        return "完成"
        
    result = test_function()
    print(f"函数返回值: {result}")
    
    # 测试异步装饰器
    import asyncio
    
    @log_async_function_call(logger)
    async def test_async_function():
        print("执行测试异步函数")
        await asyncio.sleep(1)
        return "异步完成"
        
    async def run_async_test():
        result = await test_async_function()
        print(f"异步函数返回值: {result}")
        
    asyncio.run(run_async_test())