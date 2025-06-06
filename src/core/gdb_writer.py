#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GDB写入模块

该模块负责创建和写入GDB文件。
由于环境限制，我们使用fiona和geopandas库代替arcpy来处理GDB文件。
"""

import os
import logging
import shutil
from typing import Dict, List, Optional, Any

import fiona
import geopandas as gpd
from shapely.geometry import mapping

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GDBWriter:
    """
    GDB文件写入器类
    
    用于创建和写入GDB文件。
    """
    
    def __init__(self):
        """初始化GDB写入器"""
        self.gdb_path = None
        self.layers = {}
        self.is_open = False
    
    def create_gdb(self, gdb_path: str) -> bool:
        """
        创建新的GDB文件
        
        Args:
            gdb_path: GDB文件路径
            
        Returns:
            bool: 是否成功创建
        """
        # 检查路径是否已存在
        if os.path.exists(gdb_path):
            logger.warning(f"GDB文件已存在，将被覆盖: {gdb_path}")
            try:
                # 如果是目录，尝试删除
                if os.path.isdir(gdb_path):
                    shutil.rmtree(gdb_path)
                else:
                    os.remove(gdb_path)
            except Exception as e:
                logger.error(f"无法删除现有文件: {str(e)}")
                return False
        
        try:
            # 注册GDB驱动
            fiona.supported_drivers['FileGDB'] = 'rw'  # 读写模式
            
            # 创建GDB目录结构
            # 注意：由于fiona不直接支持创建空的FileGDB，我们需要在第一次写入图层时创建
            self.gdb_path = gdb_path
            self.layers = {}
            self.is_open = True
            
            logger.info(f"已准备创建GDB文件: {gdb_path}")
            return True
        except Exception as e:
            logger.error(f"创建GDB文件时出错: {str(e)}")
            return False
    
    def create_layer(self, layer_name: str, schema: Dict, crs: Optional[Dict] = None) -> bool:
        """
        创建图层
        
        Args:
            layer_name: 图层名称
            schema: 图层结构
            crs: 坐标参考系统
            
        Returns:
            bool: 是否成功创建
        """
        if not self.is_open:
            logger.error("GDB文件未打开")
            return False
        
        if layer_name in self.layers:
            logger.warning(f"图层已存在: {layer_name}")
            return False
        
        try:
            # 创建图层
            self.layers[layer_name] = {
                'schema': schema,
                'crs': crs,
                'features': []
            }
            
            logger.info(f"已创建图层: {layer_name}")
            return True
        except Exception as e:
            logger.error(f"创建图层时出错: {str(e)}")
            return False
    
    def write_features(self, layer_name: str, features: List[Dict]) -> bool:
        """
        写入要素
        
        Args:
            layer_name: 图层名称
            features: 要素列表
            
        Returns:
            bool: 是否成功写入
        """
        if not self.is_open:
            logger.error("GDB文件未打开")
            return False
        
        if layer_name not in self.layers:
            logger.error(f"图层不存在: {layer_name}")
            return False
        
        try:
            # 添加要素到缓存
            self.layers[layer_name]['features'].extend(features)
            
            logger.info(f"已添加 {len(features)} 个要素到图层 {layer_name}")
            return True
        except Exception as e:
            logger.error(f"写入要素时出错: {str(e)}")
            return False
    
    def write_geodataframe(self, layer_name: str, gdf: gpd.GeoDataFrame) -> bool:
        """
        写入GeoDataFrame
        
        Args:
            layer_name: 图层名称
            gdf: GeoDataFrame对象
            
        Returns:
            bool: 是否成功写入
        """
        if not self.is_open:
            logger.error("GDB文件未打开")
            return False
        
        try:
            # 如果图层不存在，创建图层
            if layer_name not in self.layers:
                # 从GeoDataFrame创建schema
                schema = {
                    'geometry': gdf.geometry.iloc[0].geom_type if len(gdf) > 0 else 'Unknown',
                    'properties': {col: type(gdf[col].iloc[0]).__name__ if len(gdf) > 0 else 'str' 
                                  for col in gdf.columns if col != 'geometry'}
                }
                
                # 创建图层
                self.create_layer(layer_name, schema, gdf.crs)
            
            # 转换GeoDataFrame为要素列表
            features = []
            for _, row in gdf.iterrows():
                feature = {
                    'geometry': mapping(row.geometry),
                    'properties': {col: row[col] for col in gdf.columns if col != 'geometry'}
                }
                features.append(feature)
            
            # 写入要素
            return self.write_features(layer_name, features)
        except Exception as e:
            logger.error(f"写入GeoDataFrame时出错: {str(e)}")
            return False
    
    def finalize(self) -> bool:
        """
        完成写入并关闭文件
        
        Returns:
            bool: 是否成功完成
        """
        if not self.is_open:
            logger.error("GDB文件未打开")
            return False
        
        try:
            # 注册GDB驱动
            fiona.supported_drivers['FileGDB'] = 'rw'  # 读写模式
            
            # 写入所有图层
            for layer_name, layer_info in self.layers.items():
                schema = layer_info['schema']
                crs = layer_info['crs']
                features = layer_info['features']
                
                # 创建图层并写入要素
                with fiona.open(
                    self.gdb_path,
                    'w',
                    driver='FileGDB',
                    layer=layer_name,
                    schema=schema,
                    crs=crs
                ) as layer:
                    for feature in features:
                        layer.write(feature)
                
                logger.info(f"已写入 {len(features)} 个要素到图层 {layer_name}")
            
            self.is_open = False
            logger.info(f"已完成GDB文件写入: {self.gdb_path}")
            return True
        except Exception as e:
            logger.error(f"完成GDB文件写入时出错: {str(e)}")
            return False
    
    def close(self):
        """关闭GDB文件"""
        if self.is_open:
            self.finalize()
        
        self.gdb_path = None
        self.layers = {}
        self.is_open = False

