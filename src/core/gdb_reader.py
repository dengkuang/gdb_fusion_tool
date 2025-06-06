#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GDB读取模块

该模块负责读取GDB文件，提取图层和属性信息。
由于环境限制，我们使用fiona和geopandas库代替arcpy来处理GDB文件。
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any

import fiona
import geopandas as gpd
from shapely.geometry import shape

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GDBReader:
    """
    GDB文件读取器类
    
    用于读取GDB文件，提取图层和属性信息。
    """
    
    def __init__(self):
        """初始化GDB读取器"""
        self.gdb_path = None
        self.layers = {}
        self.current_gdb = None
    
    def read_gdb(self, gdb_path: str) -> bool:
        """
        读取GDB文件
        
        Args:
            gdb_path: GDB文件路径
            
        Returns:
            bool: 是否成功读取
        """
        if not os.path.exists(gdb_path):
            logger.error(f"GDB文件不存在: {gdb_path}")
            return False
        
        try:
            # 注册GDB驱动
            fiona.supported_drivers['FileGDB'] = 'rw'  # 读写模式
            
            # 打开GDB文件
            self.gdb_path = gdb_path
            self.layers = {}
            
            # 获取所有图层
            layer_list = fiona.listlayers(gdb_path)
            logger.info(f"在GDB中发现 {len(layer_list)} 个图层: {', '.join(layer_list)}")
            
            # 读取每个图层的基本信息
            for layer_name in layer_list:
                try:
                    with fiona.open(gdb_path, layer=layer_name, driver='FileGDB') as layer:
                        self.layers[layer_name] = {
                            'schema': layer.schema,
                            'crs': layer.crs,
                            'count': len(layer)
                        }
                except Exception as e:
                    logger.warning(f"无法读取图层 {layer_name}: {str(e)}")
            
            return True
        except Exception as e:
            logger.error(f"读取GDB文件时出错: {str(e)}")
            return False
    
    def get_layers(self) -> List[str]:
        """
        获取GDB中的图层列表
        
        Returns:
            List[str]: 图层名称列表
        """
        return list(self.layers.keys())
    
    def get_layer_schema(self, layer_name: str) -> Optional[Dict]:
        """
        获取图层的字段结构
        
        Args:
            layer_name: 图层名称
            
        Returns:
            Optional[Dict]: 图层结构，如果图层不存在则返回None
        """
        if layer_name not in self.layers:
            logger.warning(f"图层不存在: {layer_name}")
            return None
        
        return self.layers[layer_name]['schema']
    
    def read_layer_data(self, layer_name: str) -> Optional[gpd.GeoDataFrame]:
        """
        读取图层数据
        
        Args:
            layer_name: 图层名称
            
        Returns:
            Optional[gpd.GeoDataFrame]: 图层数据，如果图层不存在则返回None
        """
        if layer_name not in self.layers:
            logger.warning(f"图层不存在: {layer_name}")
            return None
        
        try:
            # 使用geopandas读取图层数据
            gdf = gpd.read_file(self.gdb_path, layer=layer_name, driver='FileGDB')
            logger.info(f"成功读取图层 {layer_name}，共 {len(gdf)} 条记录")
            return gdf
        except Exception as e:
            logger.error(f"读取图层 {layer_name} 数据时出错: {str(e)}")
            return None
    
    def get_layer_feature_count(self, layer_name: str) -> int:
        """
        获取图层要素数量
        
        Args:
            layer_name: 图层名称
            
        Returns:
            int: 要素数量，如果图层不存在则返回0
        """
        if layer_name not in self.layers:
            logger.warning(f"图层不存在: {layer_name}")
            return 0
        
        return self.layers[layer_name]['count']
    
    def get_layer_crs(self, layer_name: str) -> Optional[Dict]:
        """
        获取图层坐标参考系统
        
        Args:
            layer_name: 图层名称
            
        Returns:
            Optional[Dict]: 坐标参考系统，如果图层不存在则返回None
        """
        if layer_name not in self.layers:
            logger.warning(f"图层不存在: {layer_name}")
            return None
        
        return self.layers[layer_name]['crs']
    
    def compare_layer_schemas(self, layer_name1: str, layer_name2: str) -> Tuple[bool, List[str]]:
        """
        比较两个图层的字段结构是否一致
        
        Args:
            layer_name1: 第一个图层名称
            layer_name2: 第二个图层名称
            
        Returns:
            Tuple[bool, List[str]]: 
                - 是否一致
                - 不一致的字段列表
        """
        schema1 = self.get_layer_schema(layer_name1)
        schema2 = self.get_layer_schema(layer_name2)
        
        if not schema1 or not schema2:
            return False, ["图层不存在"]
        
        # 比较字段结构
        fields1 = schema1['properties']
        fields2 = schema2['properties']
        
        # 检查字段名称和类型是否一致
        diff_fields = []
        for field_name, field_type in fields1.items():
            if field_name not in fields2:
                diff_fields.append(f"字段 {field_name} 在第二个图层中不存在")
            elif fields2[field_name] != field_type:
                diff_fields.append(f"字段 {field_name} 类型不一致: {field_type} vs {fields2[field_name]}")
        
        for field_name in fields2:
            if field_name not in fields1:
                diff_fields.append(f"字段 {field_name} 在第一个图层中不存在")
        
        return len(diff_fields) == 0, diff_fields
    
    def close(self):
        """关闭GDB文件"""
        self.gdb_path = None
        self.layers = {}

