import logging
import asyncio
from typing import Callable, Any
from functools import wraps


class ErrorHandler:
    def __init__(self):
        """
        初始化错误处理器
        """
        self.retry_count = 3
        self.retry_delay = 2  # 秒
        
    def handle_error(self, func: Callable) -> Callable:
        """
        装饰器：处理函数执行中的错误
        
        Args:
            func: 被装饰的函数
            
        Returns:
            包装后的函数
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.retry_count):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    logging.error(f"函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{self.retry_count}): {str(e)}")
                    
                    if attempt < self.retry_count - 1:
                        logging.info(f"等待 {self.retry_delay} 秒后重试...")
                        await asyncio.sleep(self.retry_delay)
                        
            logging.error(f"函数 {func.__name__} 在 {self.retry_count} 次尝试后仍然失败: {str(last_exception)}")
            raise last_exception
            
        return wrapper
        
    async def handle_network_error(self, error_msg: str = "网络错误"):
        """
        处理网络相关错误
        
        Args:
            error_msg: 错误消息
        """
        logging.error(f"网络错误: {error_msg}")
        # 可以在这里添加重连逻辑或其他网络错误处理
        
    async def handle_timeout_error(self, timeout_duration: int):
        """
        处理超时错误
        
        Args:
            timeout_duration: 超时持续时间
        """
        logging.error(f"操作超时 ({timeout_duration} ms)")
        # 可以在这里添加超时处理逻辑
        
    async def handle_captcha_error(self):
        """
        处理验证码错误
        """
        logging.warning("检测到验证码，需要人工处理")
        # 可以在这里添加验证码处理逻辑
        
    async def handle_security_check(self):
        """
        处理安全检查
        """
        logging.warning("触发安全检查，可能需要调整请求频率")
        # 可以在这里添加应对反爬虫机制的逻辑
        
    def log_error_context(self, context: str, error: Exception):
        """
        记录错误上下文
        
        Args:
            context: 错误发生的上下文
            error: 发生的错误
        """
        logging.error(f"在 {context} 中发生错误: {str(error)}")
        
    async def recover_from_error(self, recovery_func: Callable) -> bool:
        """
        尝试从错误中恢复
        
        Args:
            recovery_func: 恢复函数
            
        Returns:
            恢复是否成功
        """
        try:
            await recovery_func()
            logging.info("错误恢复成功")
            return True
        except Exception as e:
            logging.error(f"错误恢复失败: {str(e)}")
            return False


# 示例用法
async def example_function_that_might_fail():
    import random
    if random.random() < 0.7:  # 70% 的概率抛出异常
        raise Exception("随机错误")
    return "成功"


async def main():
    error_handler = ErrorHandler()
    
    # 使用装饰器处理错误
    decorated_func = error_handler.handle_error(example_function_that_might_fail)
    
    try:
        result = await decorated_func()
        print(result)
    except Exception as e:
        print(f"最终失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())