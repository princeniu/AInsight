#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram通知模块

该模块提供通过Telegram机器人发送通知消息的功能。
"""

import requests
import logging
from typing import Optional, Dict, Any, List
import os
import json
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram通知类，用于发送Telegram消息通知"""
    
    def __init__(self, token: str, chat_id: str):
        """
        初始化Telegram通知器
        
        Args:
            token: Telegram机器人的API令牌
            chat_id: 接收消息的聊天ID
        """
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.include_preview = True
        self.send_full_article = False
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        发送Telegram消息
        
        Args:
            message: 要发送的消息内容
            parse_mode: 消息解析模式，可选HTML或Markdown
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(self.api_url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram通知发送成功")
                return True
            else:
                logger.error(f"Telegram通知发送失败: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"发送Telegram通知时出错: {str(e)}")
            return False
    
    def send_article_notification(self, 
                                 title: str, 
                                 source: str, 
                                 file_path: str,
                                 word_count: int,
                                 model_used: str,
                                 content: str = None) -> bool:
        """
        发送文章生成完成的通知
        
        Args:
            title: 文章标题
            source: 新闻来源
            file_path: 文件保存路径
            word_count: 文章字数
            model_used: 使用的模型名称
            content: 文章内容，默认为None
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        # 获取文件名
        file_name = os.path.basename(file_path)
        
        # 构建美观的HTML消息
        message = (
            f"<b>🎉 文章生成完成</b>\n\n"
            f"<b>📝 标题:</b> {title}\n"
            f"<b>🔍 来源:</b> {source}\n"
            f"<b>📊 字数:</b> {word_count}\n"
            f"<b>🤖 模型:</b> {model_used}\n"
            f"<b>💾 文件名:</b> {file_name}\n"
        )
        
        # 如果提供了文章内容，添加内容预览
        if content and self.include_preview:
            # 截取前300个字符作为预览，避免消息过长
            preview = content[:300] + ("..." if len(content) > 300 else "")
            message += f"\n<b>📄 内容预览:</b>\n<i>{preview}</i>\n"
        
        message += "\n<i>文章已保存到本地和数据库</i>"
        
        return self.send_message(message)

    def send_full_article(self, title: str, content: str) -> bool:
        """
        发送完整文章内容
        
        Args:
            title: 文章标题
            content: 文章完整内容
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        # Telegram消息有长度限制，通常为4096个字符
        # 如果内容太长，需要分段发送
        max_length = 4000  # 留一些余量给标题和格式
        
        try:
            # 发送标题
            message = f"<b>📝 {title}</b>\n\n"
            self.send_message(message)
            
            # 分段发送内容
            for i in range(0, len(content), max_length):
                chunk = content[i:i+max_length]
                self.send_message(chunk)
                
            return True
        except Exception as e:
            logger.error(f"发送完整文章时出错: {str(e)}")
            return False
    
    def send_batch_notification(self, 
                               total_fetched: int, 
                               total_filtered: int,
                               total_generated: int,
                               models_used: List[str],
                               execution_time: float) -> bool:
        """
        发送批量处理完成的通知
        
        Args:
            total_fetched: 获取的新闻总数
            total_filtered: 过滤后的新闻数量
            total_generated: 生成的文章数量
            models_used: 使用的模型列表
            execution_time: 执行时间(秒)
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        # 构建美观的HTML消息
        message = (
            f"<b>✅ AI新闻自动化任务完成</b>\n\n"
            f"<b>📰 获取新闻:</b> {total_fetched}条\n"
            f"<b>🔍 过滤后:</b> {total_filtered}条\n"
            f"<b>📝 生成文章:</b> {total_generated}篇\n"
            f"<b>🤖 使用模型:</b> {', '.join(models_used)}\n"
            f"<b>⏱️ 执行时间:</b> {execution_time:.2f}秒\n\n"
            f"<i>所有文章已保存到本地和数据库</i>"
        )
        
        return self.send_message(message)
    
    @staticmethod
    def from_config(config_path: Optional[str] = None) -> Optional['TelegramNotifier']:
        """
        从配置文件创建TelegramNotifier实例
        
        Args:
            config_path: 配置文件路径，默认为None，将使用默认路径
            
        Returns:
            TelegramNotifier: 如果配置有效则返回实例，否则返回None
        """
        if config_path is None:
            # 尝试从项目根目录的config文件夹读取
            config_path = Path(__file__).parent.parent.parent / "config" / "telegram_config.json"
        
        try:
            if not os.path.exists(config_path):
                logger.warning(f"Telegram配置文件不存在: {config_path}")
                return None
                
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            token = config.get('token')
            chat_id = config.get('chat_id')
            
            if not token or not chat_id:
                logger.warning("Telegram配置不完整，缺少token或chat_id")
                return None
                
            notifier = TelegramNotifier(token, chat_id)
            
            # 设置可选配置
            notifier.include_preview = config.get('include_preview', True)
            notifier.send_full_article = config.get('send_full_article', False)
            
            return notifier
            
        except Exception as e:
            logger.error(f"从配置加载Telegram通知器时出错: {str(e)}")
            return None 