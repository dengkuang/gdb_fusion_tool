#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据验证模块

该模块提供数据验证功能，用于验证GDB文件、模式兼容性和字段映射。
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple

import fiona

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_gdb(gdb_path: str) -> Tuple[bool, str]:
    """
    验证GDB文件是否有效
    
    Args:
        gdb_path: GDB文件路径
        
    Returns:
        Tuple[bool, str]: 
            - 是否有效
            - 错误信息
    """
    if not os.path.exists(gdb_path):
        return False, f"GDB文件不存在: {gdb_path}"
    
    try:
        # 注册GDB驱动
        fiona.supported_drivers['FileGDB'] = 'r'  # 只读模式
        
        # 尝试列出图层
        layers = fiona.listlayers(gdb_path)
        
        if not layers:
            return False, f"GDB文件中没有图层: {gdb_path}"
        
        return True, ""
    except Exception as e:
        return False, f"GDB文件无效: {str(e)}"

def validate_schema_compatibility(schema1: Dict, schema2: Dict) -> Tuple[bool, List[str]]:
    """
    验证两个模式是否兼容
    
    Args:
        schema1: 第一个模式
        schema2: 第二个模式
        
    Returns:
        Tuple[bool, List[str]]: 
            - 是否兼容
            - 不兼容的字段列表
    """
    if not schema1 or not schema2:
        return False, ["模式为空"]
    
    # 检查几何类型是否兼容
    if schema1.get('geometry') != schema2.get('geometry'):
        return False, [f"几何类型不兼容: {schema1.get('geometry')} vs {schema2.get('geometry')}"]
    
    # 获取字段列表
    fields1 = schema1.get('properties', {})
    fields2 = schema2.get('properties', {})
    
    # 检查字段名称和类型是否一致
    diff_fields = []
    for field_name, field_type in fields1.items():
        if field_name not in fields2:
            diff_fields.append(f"字段 {field_name} 在第二个模式中不存在")
        elif fields2[field_name] != field_type:
            diff_fields.append(f"字段 {field_name} 类型不一致: {field_type} vs {fields2[field_name]}")
    
    for field_name in fields2:
        if field_name not in fields1:
            diff_fields.append(f"字段 {field_name} 在第一个模式中不存在")
    
    return len(diff_fields) == 0, diff_fields

def validate_field_mapping(mapping: Dict, source_schema: Dict, target_schema: Dict) -> Tuple[bool, List[str]]:
    """
    验证字段映射是否有效
    
    Args:
        mapping: 字段映射
        source_schema: 源模式
        target_schema: 目标模式
        
    Returns:
        Tuple[bool, List[str]]: 
            - 是否有效
            - 错误信息列表
    """
    if not mapping:
        return False, ["映射为空"]
    
    if not source_schema or not source_schema.get('properties'):
        return False, ["源模式为空"]
    
    if not target_schema or not target_schema.get('properties'):
        return False, ["目标模式为空"]
    
    # 获取字段列表
    source_fields = source_schema.get('properties', {})
    target_fields = target_schema.get('properties', {})
    
    # 检查映射是否有效
    errors = []
    for source_field, map_info in mapping.items():
        # 检查源字段是否存在
        if source_field not in source_fields:
            errors.append(f"源字段不存在: {source_field}")
            continue
        
        # 获取映射信息
        target_field = map_info.get('target_field')
        conversion = map_info.get('conversion')
        
        # 检查目标字段
        if not target_field:
            errors.append(f"源字段 {source_field} 的目标字段未指定")
            continue
        
        # 检查转换类型
        if not conversion:
            errors.append(f"源字段 {source_field} 的转换类型未指定")
            continue
        
        # 根据转换类型进行验证
        if conversion == 'direct':
            # 直接映射，检查目标字段是否存在
            if target_field not in target_fields:
                errors.append(f"目标字段不存在: {target_field}")
            # 检查字段类型是否一致
            elif source_fields[source_field] != target_fields[target_field]:
                errors.append(f"字段类型不一致: {source_field}({source_fields[source_field]}) -> {target_field}({target_fields[target_field]})")
        
        elif conversion == 'type_convert':
            # 类型转换，检查目标字段是否存在
            if target_field not in target_fields:
                errors.append(f"目标字段不存在: {target_field}")
            # 检查是否指定了目标类型
            elif 'target_type' not in map_info:
                errors.append(f"未指定目标类型: {source_field} -> {target_field}")
            # 检查目标类型是否与目标字段类型一致
            elif map_info['target_type'] != target_fields[target_field]:
                errors.append(f"目标类型不一致: {map_info['target_type']} vs {target_fields[target_field]}")
        
        elif conversion == 'new_field':
            # 新字段，检查是否指定了字段类型
            if 'field_type' not in map_info:
                errors.append(f"未指定字段类型: {source_field} -> {target_field}")
        
        elif conversion == 'custom':
            # 自定义转换，检查是否指定了自定义函数
            if 'custom_function' not in map_info or not callable(map_info['custom_function']):
                errors.append(f"未指定有效的自定义函数: {source_field} -> {target_field}")
        
        else:
            # 未知转换类型
            errors.append(f"未知的转换类型: {conversion}")
    
    return len(errors) == 0, errors

def validate_output_path(output_path: str) -> Tuple[bool, str]:
    """
    验证输出路径是否有效
    
    Args:
        output_path: 输出路径
        
    Returns:
        Tuple[bool, str]: 
            - 是否有效
            - 错误信息
    """
    # 检查路径是否为空
    if not output_path:
        return False, "输出路径为空"
    
    # 检查目录是否存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            return False, f"无法创建输出目录: {str(e)}"
    
    # 检查是否有写入权限
    if output_dir:
        if not os.access(output_dir, os.W_OK):
            return False, f"没有写入权限: {output_dir}"
    
    return True, ""

