#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
融合逻辑模块

该模块实现两种融合功能的核心逻辑：
1. 融合字段结构一致的多个GDB
2. 融合字段结构不同的GDB，通过字段映射关系进行属性融合
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple

import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from .gdb_reader import GDBReader
from .gdb_writer import GDBWriter
from .field_mapper import FieldMapper

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GDBFusion:
    """
    GDB融合类
    
    实现GDB融合的核心逻辑。
    """
    
    def __init__(self):
        """初始化GDB融合器"""
        self.reader = GDBReader()
        self.writer = GDBWriter()
        self.field_mapper = FieldMapper()
    
    def merge_same_schema(self, gdb_list: List[str], output_gdb: str, 
                          layer_filter: Optional[List[str]] = None) -> bool:
        """
        融合相同结构的GDB
        
        将多个字段结构一致的GDB文件融合为一个GDB文件。
        
        Args:
            gdb_list: GDB文件路径列表
            output_gdb: 输出GDB文件路径
            layer_filter: 要处理的图层列表，如果为None则处理所有图层
            
        Returns:
            bool: 是否成功融合
        """
        if len(gdb_list) < 2:
            logger.error("至少需要两个GDB文件进行融合")
            return False
        
        try:
            # 创建输出GDB
            if not self.writer.create_gdb(output_gdb):
                return False
            
            # 读取第一个GDB作为基准
            base_gdb = gdb_list[0]
            if not self.reader.read_gdb(base_gdb):
                return False
            
            # 获取基准GDB的图层列表
            base_layers = self.reader.get_layers()
            if not base_layers:
                logger.error(f"基准GDB中没有图层: {base_gdb}")
                return False
            
            # 如果指定了图层过滤器，则只处理指定的图层
            if layer_filter:
                base_layers = [layer for layer in base_layers if layer in layer_filter]
                if not base_layers:
                    logger.error("指定的图层在基准GDB中不存在")
                    return False
            
            # 处理每个图层
            for layer_name in base_layers:
                logger.info(f"处理图层: {layer_name}")
                
                # 获取基准图层的结构和数据
                base_schema = self.reader.get_layer_schema(layer_name)
                base_crs = self.reader.get_layer_crs(layer_name)
                
                # 创建输出图层
                if not self.writer.create_layer(layer_name, base_schema, base_crs):
                    continue
                
                # 读取基准图层数据
                base_gdf = self.reader.read_layer_data(layer_name)
                if base_gdf is None:
                    logger.warning(f"无法读取基准图层数据: {layer_name}")
                    continue
                
                # 写入基准图层数据
                if not self.writer.write_geodataframe(layer_name, base_gdf):
                    logger.warning(f"无法写入基准图层数据: {layer_name}")
                    continue
                
                # 处理其他GDB
                for gdb_path in tqdm(gdb_list[1:], desc=f"融合图层 {layer_name}"):
                    # 读取GDB
                    if not self.reader.read_gdb(gdb_path):
                        logger.warning(f"无法读取GDB: {gdb_path}")
                        continue
                    
                    # 检查图层是否存在
                    if layer_name not in self.reader.get_layers():
                        logger.warning(f"图层 {layer_name} 在GDB {gdb_path} 中不存在")
                        continue
                    
                    # 检查图层结构是否一致
                    is_compatible, diff_fields = self.reader.compare_layer_schemas(
                        layer_name, layer_name)
                    
                    if not is_compatible:
                        logger.warning(f"图层 {layer_name} 在GDB {gdb_path} 中结构不一致: {diff_fields}")
                        continue
                    
                    # 读取图层数据
                    gdf = self.reader.read_layer_data(layer_name)
                    if gdf is None:
                        logger.warning(f"无法读取图层数据: {layer_name} 从 {gdb_path}")
                        continue
                    
                    # 检查坐标系是否一致，如果不一致则转换
                    if base_crs != self.reader.get_layer_crs(layer_name):
                        logger.info(f"转换坐标系: {layer_name} 从 {gdb_path}")
                        gdf = gdf.to_crs(base_crs)
                    
                    # 写入图层数据
                    if not self.writer.write_geodataframe(layer_name, gdf):
                        logger.warning(f"无法写入图层数据: {layer_name} 从 {gdb_path}")
                        continue
            
            # 完成写入
            if not self.writer.finalize():
                return False
            
            logger.info(f"成功融合 {len(gdb_list)} 个GDB文件到 {output_gdb}")
            return True
        except Exception as e:
            logger.error(f"融合相同结构的GDB时出错: {str(e)}")
            return False
        finally:
            # 关闭资源
            self.reader.close()
            self.writer.close()
    
    def merge_different_schema(self, main_gdb: str, secondary_gdb: str, output_gdb: str,
                              mapping_file: Optional[str] = None,
                              layer_filter: Optional[List[str]] = None) -> bool:
        """
        融合不同结构的GDB
        
        将两个字段结构不同的GDB文件融合为一个GDB文件，以一个GDB为主结构，
        通过字段映射关系，将另一个GDB的属性融合到主GDB中。
        
        Args:
            main_gdb: 主GDB文件路径
            secondary_gdb: 次要GDB文件路径
            output_gdb: 输出GDB文件路径
            mapping_file: 字段映射配置文件路径，如果为None则自动创建映射
            layer_filter: 要处理的图层列表，如果为None则处理所有图层
            
        Returns:
            bool: 是否成功融合
        """
        try:
            # 创建输出GDB
            if not self.writer.create_gdb(output_gdb):
                return False
            
            # 读取主GDB
            if not self.reader.read_gdb(main_gdb):
                return False
            
            # 获取主GDB的图层列表
            main_layers = self.reader.get_layers()
            if not main_layers:
                logger.error(f"主GDB中没有图层: {main_gdb}")
                return False
            
            # 如果指定了图层过滤器，则只处理指定的图层
            if layer_filter:
                main_layers = [layer for layer in main_layers if layer in layer_filter]
                if not main_layers:
                    logger.error("指定的图层在主GDB中不存在")
                    return False
            
            # 读取次要GDB
            secondary_reader = GDBReader()
            if not secondary_reader.read_gdb(secondary_gdb):
                return False
            
            # 获取次要GDB的图层列表
            secondary_layers = secondary_reader.get_layers()
            if not secondary_layers:
                logger.error(f"次要GDB中没有图层: {secondary_gdb}")
                return False
            
            # 处理每个主图层
            for layer_name in main_layers:
                logger.info(f"处理主图层: {layer_name}")
                
                # 检查次要GDB中是否存在对应图层
                if layer_name not in secondary_layers:
                    logger.warning(f"次要GDB中不存在图层: {layer_name}")
                    
                    # 直接复制主图层
                    main_schema = self.reader.get_layer_schema(layer_name)
                    main_crs = self.reader.get_layer_crs(layer_name)
                    main_gdf = self.reader.read_layer_data(layer_name)
                    
                    if main_gdf is not None:
                        self.writer.create_layer(layer_name, main_schema, main_crs)
                        self.writer.write_geodataframe(layer_name, main_gdf)
                    
                    continue
                
                # 获取主图层和次要图层的结构
                main_schema = self.reader.get_layer_schema(layer_name)
                secondary_schema = secondary_reader.get_layer_schema(layer_name)
                
                # 创建字段映射
                if mapping_file and os.path.exists(mapping_file):
                    # 加载映射配置
                    self.field_mapper.load_mapping(mapping_file)
                else:
                    # 自动创建映射
                    self.field_mapper.create_mapping(secondary_schema, main_schema)
                
                # 获取主图层和次要图层的数据
                main_gdf = self.reader.read_layer_data(layer_name)
                secondary_gdf = secondary_reader.read_layer_data(layer_name)
                
                if main_gdf is None or secondary_gdf is None:
                    logger.warning(f"无法读取图层数据: {layer_name}")
                    continue
                
                # 检查坐标系是否一致，如果不一致则转换
                main_crs = self.reader.get_layer_crs(layer_name)
                secondary_crs = secondary_reader.get_layer_crs(layer_name)
                
                if main_crs != secondary_crs:
                    logger.info(f"转换坐标系: {layer_name} 从次要GDB")
                    secondary_gdf = secondary_gdf.to_crs(main_crs)
                
                # 创建输出图层
                target_schema = self.field_mapper.get_target_schema(main_schema)
                if not self.writer.create_layer(layer_name, target_schema, main_crs):
                    continue
                
                # 写入主图层数据
                if not self.writer.write_geodataframe(layer_name, main_gdf):
                    logger.warning(f"无法写入主图层数据: {layer_name}")
                    continue
                
                # 处理次要图层数据
                # 将次要图层的每个要素转换为主图层结构
                converted_features = []
                for _, row in tqdm(secondary_gdf.iterrows(), desc=f"转换图层 {layer_name}", total=len(secondary_gdf)):
                    # 构造要素
                    feature = {
                        'geometry': row.geometry.__geo_interface__,
                        'properties': {col: row[col] for col in secondary_gdf.columns if col != 'geometry'}
                    }
                    
                    # 应用字段映射
                    converted_feature = self.field_mapper.apply_mapping(feature)
                    converted_features.append(converted_feature)
                
                # 写入转换后的要素
                if not self.writer.write_features(layer_name, converted_features):
                    logger.warning(f"无法写入转换后的要素: {layer_name}")
                    continue
            
            # 完成写入
            if not self.writer.finalize():
                return False
            
            logger.info(f"成功融合GDB文件 {main_gdb} 和 {secondary_gdb} 到 {output_gdb}")
            return True
        except Exception as e:
            logger.error(f"融合不同结构的GDB时出错: {str(e)}")
            return False
        finally:
            # 关闭资源
            self.reader.close()
            self.writer.close()
            if 'secondary_reader' in locals():
                secondary_reader.close()
    
    def generate_mapping_template(self, main_gdb: str, secondary_gdb: str, 
                                 layer_name: str, output_file: str) -> bool:
        """
        生成字段映射模板
        
        根据主GDB和次要GDB的结构，生成字段映射模板。
        
        Args:
            main_gdb: 主GDB文件路径
            secondary_gdb: 次要GDB文件路径
            layer_name: 图层名称
            output_file: 输出文件路径
            
        Returns:
            bool: 是否成功生成
        """
        try:
            # 读取主GDB
            if not self.reader.read_gdb(main_gdb):
                return False
            
            # 检查图层是否存在
            if layer_name not in self.reader.get_layers():
                logger.error(f"主GDB中不存在图层: {layer_name}")
                return False
            
            # 获取主图层结构
            main_schema = self.reader.get_layer_schema(layer_name)
            
            # 读取次要GDB
            secondary_reader = GDBReader()
            if not secondary_reader.read_gdb(secondary_gdb):
                return False
            
            # 检查图层是否存在
            if layer_name not in secondary_reader.get_layers():
                logger.error(f"次要GDB中不存在图层: {layer_name}")
                return False
            
            # 获取次要图层结构
            secondary_schema = secondary_reader.get_layer_schema(layer_name)
            
            # 创建字段映射
            self.field_mapper.create_mapping(secondary_schema, main_schema)
            
            # 保存映射模板
            if not self.field_mapper.save_mapping(output_file):
                return False
            
            logger.info(f"成功生成字段映射模板: {output_file}")
            return True
        except Exception as e:
            logger.error(f"生成字段映射模板时出错: {str(e)}")
            return False
        finally:
            # 关闭资源
            self.reader.close()
            if 'secondary_reader' in locals():
                secondary_reader.close()

