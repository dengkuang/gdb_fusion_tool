#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据转换模块

该模块提供数据类型转换功能，用于处理字段类型转换和空值处理。
"""

import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_field_type(value: Any, source_type: str, target_type: str) -> Any:
    """
    转换字段类型
    
    Args:
        value: 字段值
        source_type: 源类型
        target_type: 目标类型
        
    Returns:
        Any: 转换后的值
    """
    # 处理空值
    if value is None:
        return None
    
    try:
        # 根据目标类型进行转换
        if target_type == 'str' or target_type == 'string':
            return str(value)
        elif target_type == 'int' or target_type == 'int32' or target_type == 'int64':
            return int(float(value))
        elif target_type == 'float' or target_type == 'double':
            return float(value)
        elif target_type == 'bool' or target_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 't', 'y')
            return bool(value)
        elif target_type == 'date' or target_type == 'datetime':
            if isinstance(value, str):
                # 尝试多种日期格式
                for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                # 如果所有格式都失败，返回原值
                return value
            return value
        else:
            # 未知类型，返回原值
            logger.warning(f"未知的目标类型: {target_type}，返回原值")
            return value
    except Exception as e:
        logger.error(f"转换字段类型时出错: {str(e)}")
        return None

def handle_null_values(value: Any, field_name: str, default_value: Any = None) -> Any:
    """
    处理空值
    
    Args:
        value: 字段值
        field_name: 字段名称
        default_value: 默认值
        
    Returns:
        Any: 处理后的值
    """
    if value is None:
        logger.debug(f"字段 {field_name} 的值为空，使用默认值: {default_value}")
        return default_value
    return value

def convert_geometry_type(geometry: Dict, target_type: str) -> Optional[Dict]:
    """
    转换几何类型
    
    Args:
        geometry: 几何对象
        target_type: 目标几何类型
        
    Returns:
        Optional[Dict]: 转换后的几何对象
    """
    if not geometry:
        return None
    
    try:
        source_type = geometry.get('type')
        
        # 如果源类型和目标类型相同，直接返回
        if source_type == target_type:
            return geometry
        
        # 处理不同类型的转换
        if source_type == 'Point' and target_type == 'MultiPoint':
            # 点转多点
            return {
                'type': 'MultiPoint',
                'coordinates': [geometry.get('coordinates')]
            }
        elif source_type == 'LineString' and target_type == 'MultiLineString':
            # 线转多线
            return {
                'type': 'MultiLineString',
                'coordinates': [geometry.get('coordinates')]
            }
        elif source_type == 'Polygon' and target_type == 'MultiPolygon':
            # 面转多面
            return {
                'type': 'MultiPolygon',
                'coordinates': [geometry.get('coordinates')]
            }
        elif source_type == 'MultiPoint' and target_type == 'Point':
            # 多点转点（取第一个点）
            if geometry.get('coordinates') and len(geometry.get('coordinates')) > 0:
                return {
                    'type': 'Point',
                    'coordinates': geometry.get('coordinates')[0]
                }
        elif source_type == 'MultiLineString' and target_type == 'LineString':
            # 多线转线（取第一条线）
            if geometry.get('coordinates') and len(geometry.get('coordinates')) > 0:
                return {
                    'type': 'LineString',
                    'coordinates': geometry.get('coordinates')[0]
                }
        elif source_type == 'MultiPolygon' and target_type == 'Polygon':
            # 多面转面（取第一个面）
            if geometry.get('coordinates') and len(geometry.get('coordinates')) > 0:
                return {
                    'type': 'Polygon',
                    'coordinates': geometry.get('coordinates')[0]
                }
        
        # 其他类型转换暂不支持
        logger.warning(f"不支持的几何类型转换: {source_type} -> {target_type}")
        return None
    except Exception as e:
        logger.error(f"转换几何类型时出错: {str(e)}")
        return None

def convert_crs(crs_from: Dict, crs_to: Dict) -> Dict:
    """
    转换坐标参考系统
    
    Args:
        crs_from: 源坐标参考系统
        crs_to: 目标坐标参考系统
        
    Returns:
        Dict: 转换后的坐标参考系统
    """
    # 这个函数主要是为了接口一致性，实际转换在geopandas中进行
    return crs_to

def create_field_mapping_dict(source_fields: Dict[str, str], target_fields: Dict[str, str]) -> Dict:
    """
    创建字段映射字典
    
    根据源字段和目标字段创建默认的字段映射字典。
    
    Args:
        source_fields: 源字段字典，格式为 {字段名: 字段类型}
        target_fields: 目标字段字典，格式为 {字段名: 字段类型}
        
    Returns:
        Dict: 字段映射字典
    """
    mapping = {}
    
    # 为每个源字段创建映射
    for source_field, source_type in source_fields.items():
        # 检查目标字段中是否有相同名称的字段
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
            # 如果目标字段中没有该字段，创建新字段
            mapping[source_field] = {
                'target_field': source_field,
                'conversion': 'new_field',
                'field_type': source_type,
                'default_value': None
            }
    
    return mapping

def get_field_type_for_value(value: Any) -> str:
    """
    根据值获取字段类型
    
    Args:
        value: 字段值
        
    Returns:
        str: 字段类型
    """
    if value is None:
        return 'str'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, bool):
        return 'bool'
    elif isinstance(value, datetime):
        return 'date'
    else:
        return 'str'

def convert_schema_to_fiona_schema(schema: Dict) -> Dict:
    """
    将自定义模式转换为Fiona模式
    
    Args:
        schema: 自定义模式
        
    Returns:
        Dict: Fiona模式
    """
    # 映射类型
    type_mapping = {
        'str': 'str',
        'string': 'str',
        'int': 'int',
        'int32': 'int',
        'int64': 'int',
        'float': 'float',
        'double': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        'date': 'date',
        'datetime': 'datetime'
    }
    
    fiona_schema = {
        'geometry': schema.get('geometry', 'Unknown'),
        'properties': {}
    }
    
    # 转换属性类型
    for field, field_type in schema.get('properties', {}).items():
        fiona_schema['properties'][field] = type_mapping.get(field_type, 'str')
    
    return fiona_schema

