#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字段映射模块

该模块负责处理字段映射关系，用于融合不同结构的GDB文件。
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FieldMapper:
    """
    字段映射类
    
    用于创建、加载、保存和应用字段映射关系。
    """
    
    def __init__(self):
        """初始化字段映射器"""
        self.mapping = {}
    
    def create_mapping(self, source_schema: Dict, target_schema: Dict) -> Dict:
        """
        创建默认映射
        
        根据源模式和目标模式创建默认的字段映射关系。
        尝试匹配相同名称的字段，对于不匹配的字段，将创建新字段。
        
        Args:
            source_schema: 源模式
            target_schema: 目标模式
            
        Returns:
            Dict: 字段映射关系
        """
        mapping = {}
        
        # 获取字段列表
        source_fields = source_schema.get('properties', {})
        target_fields = target_schema.get('properties', {})
        
        # 为每个源字段创建映射
        for source_field, source_type in source_fields.items():
            # 检查目标模式中是否有相同名称的字段
            if source_field in target_fields:
                # 如果字段类型相同，直接映射
                if source_type == target_fields[source_field]:
                    mapping[source_field] = {
                        'target_field': source_field,
                        'conversion': 'direct',
                        'default_value': None
                    }
                else:
                    # 如果字段类型不同，设置类型转换
                    mapping[source_field] = {
                        'target_field': source_field,
                        'conversion': 'type_convert',
                        'source_type': source_type,
                        'target_type': target_fields[source_field],
                        'default_value': None
                    }
            else:
                # 如果目标模式中没有该字段，创建新字段
                mapping[source_field] = {
                    'target_field': source_field,
                    'conversion': 'new_field',
                    'field_type': source_type,
                    'default_value': None
                }
        
        self.mapping = mapping
        logger.info(f"已创建默认映射，共 {len(mapping)} 个字段")
        return mapping
    
    def load_mapping(self, mapping_file: str) -> bool:
        """
        加载映射配置
        
        从JSON文件加载字段映射配置。
        
        Args:
            mapping_file: 映射配置文件路径
            
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(mapping_file):
            logger.error(f"映射配置文件不存在: {mapping_file}")
            return False
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            
            self.mapping = mapping
            logger.info(f"已加载映射配置，共 {len(mapping)} 个字段")
            return True
        except Exception as e:
            logger.error(f"加载映射配置时出错: {str(e)}")
            return False
    
    def save_mapping(self, mapping_file: str) -> bool:
        """
        保存映射配置
        
        将字段映射配置保存到JSON文件。
        
        Args:
            mapping_file: 映射配置文件路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f, indent=4, ensure_ascii=False)
            
            logger.info(f"已保存映射配置到文件: {mapping_file}")
            return True
        except Exception as e:
            logger.error(f"保存映射配置时出错: {str(e)}")
            return False
    
    def apply_mapping(self, source_feature: Dict, mapping: Optional[Dict] = None) -> Dict:
        """
        应用映射到要素
        
        根据字段映射关系，将源要素转换为目标要素。
        
        Args:
            source_feature: 源要素
            mapping: 字段映射关系，如果为None则使用当前映射
            
        Returns:
            Dict: 转换后的要素
        """
        if mapping is None:
            mapping = self.mapping
        
        if not mapping:
            logger.warning("映射为空，无法应用")
            return source_feature
        
        target_feature = {
            'geometry': source_feature.get('geometry', None)
        }
        target_properties = {}
        
        # 应用字段映射
        source_properties = source_feature.get('properties', {})
        for source_field, map_info in mapping.items():
            if source_field not in source_properties:
                logger.warning(f"源要素中不存在字段: {source_field}")
                continue
            
            source_value = source_properties[source_field]
            target_field = map_info.get('target_field', source_field)
            conversion = map_info.get('conversion', 'direct')
            default_value = map_info.get('default_value', None)
            
            # 根据转换类型处理值
            if conversion == 'direct':
                # 直接映射
                target_properties[target_field] = source_value
            elif conversion == 'type_convert':
                # 类型转换
                target_type = map_info.get('target_type', 'str')
                try:
                    # 尝试转换类型
                    if target_type == 'str':
                        target_properties[target_field] = str(source_value) if source_value is not None else default_value
                    elif target_type == 'int':
                        target_properties[target_field] = int(source_value) if source_value is not None else default_value
                    elif target_type == 'float':
                        target_properties[target_field] = float(source_value) if source_value is not None else default_value
                    elif target_type == 'bool':
                        target_properties[target_field] = bool(source_value) if source_value is not None else default_value
                    else:
                        # 未知类型，使用默认值
                        target_properties[target_field] = default_value
                except (ValueError, TypeError):
                    # 转换失败，使用默认值
                    target_properties[target_field] = default_value
            elif conversion == 'new_field':
                # 新字段，直接使用源值
                target_properties[target_field] = source_value
            elif conversion == 'custom':
                # 自定义转换
                custom_function = map_info.get('custom_function', None)
                if custom_function and callable(custom_function):
                    try:
                        target_properties[target_field] = custom_function(source_value)
                    except Exception as e:
                        logger.error(f"自定义转换函数出错: {str(e)}")
                        target_properties[target_field] = default_value
                else:
                    target_properties[target_field] = default_value
            else:
                # 未知转换类型，使用默认值
                target_properties[target_field] = default_value
        
        target_feature['properties'] = target_properties
        return target_feature
    
    def get_target_schema(self, source_schema: Dict) -> Dict:
        """
        获取目标模式
        
        根据源模式和字段映射关系，生成目标模式。
        
        Args:
            source_schema: 源模式
            
        Returns:
            Dict: 目标模式
        """
        target_schema = {
            'geometry': source_schema.get('geometry', 'Unknown'),
            'properties': {}
        }
        
        # 获取源字段
        source_fields = source_schema.get('properties', {})
        
        # 根据映射生成目标字段
        for source_field, map_info in self.mapping.items():
            if source_field not in source_fields:
                logger.warning(f"源模式中不存在字段: {source_field}")
                continue
            
            target_field = map_info.get('target_field', source_field)
            conversion = map_info.get('conversion', 'direct')
            
            if conversion == 'direct':
                # 直接映射，使用源字段类型
                target_schema['properties'][target_field] = source_fields[source_field]
            elif conversion == 'type_convert':
                # 类型转换，使用目标字段类型
                target_schema['properties'][target_field] = map_info.get('target_type', 'str')
            elif conversion == 'new_field':
                # 新字段，使用指定的字段类型
                target_schema['properties'][target_field] = map_info.get('field_type', 'str')
            elif conversion == 'custom':
                # 自定义转换，使用指定的字段类型
                target_schema['properties'][target_field] = map_info.get('field_type', 'str')
        
        return target_schema
    
    def update_mapping(self, source_field: str, target_field: str, conversion: str, **kwargs) -> bool:
        """
        更新映射
        
        更新字段映射关系。
        
        Args:
            source_field: 源字段名称
            target_field: 目标字段名称
            conversion: 转换类型
            **kwargs: 其他参数
            
        Returns:
            bool: 是否成功更新
        """
        try:
            # 创建映射信息
            map_info = {
                'target_field': target_field,
                'conversion': conversion,
                **kwargs
            }
            
            # 更新映射
            self.mapping[source_field] = map_info
            logger.info(f"已更新字段映射: {source_field} -> {target_field}")
            return True
        except Exception as e:
            logger.error(f"更新字段映射时出错: {str(e)}")
            return False
    
    def remove_mapping(self, source_field: str) -> bool:
        """
        删除映射
        
        删除字段映射关系。
        
        Args:
            source_field: 源字段名称
            
        Returns:
            bool: 是否成功删除
        """
        if source_field not in self.mapping:
            logger.warning(f"映射中不存在字段: {source_field}")
            return False
        
        try:
            # 删除映射
            del self.mapping[source_field]
            logger.info(f"已删除字段映射: {source_field}")
            return True
        except Exception as e:
            logger.error(f"删除字段映射时出错: {str(e)}")
            return False
    
    def get_mapping(self) -> Dict:
        """
        获取当前映射
        
        Returns:
            Dict: 当前字段映射关系
        """
        return self.mapping
    
    def clear_mapping(self):
        """清空映射"""
        self.mapping = {}

