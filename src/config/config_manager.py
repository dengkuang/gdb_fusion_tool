#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块

该模块负责管理工具配置，包括加载、保存和获取配置项。
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    配置管理类
    
    用于管理工具配置。
    """
    
    def __init__(self):
        """初始化配置管理器"""
        self.config = {}
        self.config_file = None
    
    def load_config(self, config_file: str) -> bool:
        """
        加载配置
        
        从JSON文件加载配置。
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(config_file):
            logger.warning(f"配置文件不存在: {config_file}")
            self.config = {}
            self.config_file = config_file
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.config_file = config_file
            logger.info(f"已加载配置: {config_file}")
            return True
        except Exception as e:
            logger.error(f"加载配置时出错: {str(e)}")
            self.config = {}
            self.config_file = config_file
            return False
    
    def save_config(self, config_file: Optional[str] = None) -> bool:
        """
        保存配置
        
        将配置保存到JSON文件。
        
        Args:
            config_file: 配置文件路径，如果为None则使用当前配置文件
            
        Returns:
            bool: 是否成功保存
        """
        if config_file is None:
            config_file = self.config_file
        
        if config_file is None:
            logger.error("未指定配置文件路径")
            return False
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.config_file = config_file
            logger.info(f"已保存配置: {config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置时出错: {str(e)}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键
            default: 默认值
            
        Returns:
            Any: 配置项值
        """
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键
            value: 配置项值
        """
        self.config[key] = value
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        获取所有配置项
        
        Returns:
            Dict[str, Any]: 所有配置项
        """
        return self.config.copy()
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        更新多个配置项
        
        Args:
            settings: 配置项字典
        """
        self.config.update(settings)
    
    def clear_settings(self) -> None:
        """清空所有配置项"""
        self.config = {}
    
    def remove_setting(self, key: str) -> bool:
        """
        删除配置项
        
        Args:
            key: 配置项键
            
        Returns:
            bool: 是否成功删除
        """
        if key in self.config:
            del self.config[key]
            return True
        return False
    
    def get_config_file(self) -> Optional[str]:
        """
        获取当前配置文件路径
        
        Returns:
            Optional[str]: 配置文件路径
        """
        return self.config_file

