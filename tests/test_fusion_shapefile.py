#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
融合功能测试脚本（使用Shapefile格式）

该脚本用于测试GDB融合工具的功能，使用Shapefile格式的测试数据。
"""

import os
import sys
import logging
import unittest
import shutil
from pathlib import Path
import glob

import geopandas as gpd
import pandas as pd

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from src.core.fusion import GDBFusion
from src.core.gdb_reader import GDBReader
from src.core.field_mapper import FieldMapper

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestFusionShapefile(unittest.TestCase):
    """融合功能测试类（使用Shapefile格式）"""
    
    @classmethod
    def setUpClass(cls):
        """测试前的准备工作"""
        # 获取测试数据目录
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # 创建输出目录
        cls.output_dir = os.path.join(cls.test_data_dir, 'output')
        os.makedirs(cls.output_dir, exist_ok=True)
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 清空输出目录
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    def test_merge_same_schema(self):
        """测试融合字段结构一致的多个Shapefile"""
        logger.info("测试融合字段结构一致的多个Shapefile")
        
        # 获取输入Shapefile文件
        input_dirs = [
            os.path.join(self.test_data_dir, 'same_schema_1'),
            os.path.join(self.test_data_dir, 'same_schema_2'),
            os.path.join(self.test_data_dir, 'same_schema_3')
        ]
        
        # 检查输入目录是否存在
        for dir_path in input_dirs:
            self.assertTrue(os.path.exists(dir_path), f"输入目录不存在: {dir_path}")
            
            # 检查每个目录中是否有Shapefile文件
            shp_files = glob.glob(os.path.join(dir_path, "*.shp"))
            self.assertTrue(len(shp_files) > 0, f"目录中没有Shapefile文件: {dir_path}")
        
        # 设置输出目录
        output_dir = os.path.join(self.output_dir, 'merged_same')
        os.makedirs(output_dir, exist_ok=True)
        
        # 对每个图层类型进行融合
        layer_types = ['points', 'lines', 'polygons']
        
        for layer_type in layer_types:
            # 获取该类型的所有Shapefile文件
            input_files = [os.path.join(dir_path, f"{layer_type}.shp") for dir_path in input_dirs]
            
            # 检查文件是否存在
            for file_path in input_files:
                self.assertTrue(os.path.exists(file_path), f"输入文件不存在: {file_path}")
            
            # 读取所有Shapefile
            gdfs = []
            for file_path in input_files:
                gdf = gpd.read_file(file_path)
                gdfs.append(gdf)
            
            # 合并GeoDataFrame
            merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
            
            # 保存合并后的Shapefile
            output_file = os.path.join(output_dir, f"{layer_type}.shp")
            merged_gdf.to_file(output_file)
            
            # 验证合并结果
            self.assertTrue(os.path.exists(output_file), f"输出文件不存在: {output_file}")
            
            # 读取合并后的Shapefile
            result_gdf = gpd.read_file(output_file)
            
            # 验证要素数量
            expected_count = sum(len(gdf) for gdf in gdfs)
            self.assertEqual(len(result_gdf), expected_count, 
                            f"{layer_type}图层要素数量不符: {len(result_gdf)} != {expected_count}")
        
        logger.info("融合字段结构一致的多个Shapefile测试通过")
    
    def test_merge_different_schema(self):
        """测试融合字段结构不同的Shapefile"""
        logger.info("测试融合字段结构不同的Shapefile")
        
        # 获取输入目录
        main_dir = os.path.join(self.test_data_dir, 'main')
        secondary_dir = os.path.join(self.test_data_dir, 'secondary')
        
        # 检查输入目录是否存在
        self.assertTrue(os.path.exists(main_dir), f"主目录不存在: {main_dir}")
        self.assertTrue(os.path.exists(secondary_dir), f"次要目录不存在: {secondary_dir}")
        
        # 设置输出目录
        output_dir = os.path.join(self.output_dir, 'merged_diff')
        os.makedirs(output_dir, exist_ok=True)
        
        # 对points图层进行融合
        layer_type = 'points'
        
        # 获取映射文件
        mapping_file = os.path.join(self.test_data_dir, f'{layer_type}_mapping.json')
        self.assertTrue(os.path.exists(mapping_file), f"映射文件不存在: {mapping_file}")
        
        # 读取映射文件
        import json
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        # 读取主Shapefile
        main_file = os.path.join(main_dir, f"{layer_type}.shp")
        self.assertTrue(os.path.exists(main_file), f"主文件不存在: {main_file}")
        main_gdf = gpd.read_file(main_file)
        
        # 读取次要Shapefile
        secondary_file = os.path.join(secondary_dir, f"{layer_type}.shp")
        self.assertTrue(os.path.exists(secondary_file), f"次要文件不存在: {secondary_file}")
        secondary_gdf = gpd.read_file(secondary_file)
        
        # 应用字段映射
        mapped_gdf = secondary_gdf.copy()
        for source_field, map_info in mapping.items():
            if source_field in secondary_gdf.columns:
                target_field = map_info['target_field']
                mapped_gdf = mapped_gdf.rename(columns={source_field: target_field})
        
        # 合并GeoDataFrame
        merged_gdf = gpd.GeoDataFrame(pd.concat([main_gdf, mapped_gdf], ignore_index=True), crs=main_gdf.crs)
        
        # 保存合并后的Shapefile
        output_file = os.path.join(output_dir, f"{layer_type}.shp")
        merged_gdf.to_file(output_file)
        
        # 验证合并结果
        self.assertTrue(os.path.exists(output_file), f"输出文件不存在: {output_file}")
        
        # 读取合并后的Shapefile
        result_gdf = gpd.read_file(output_file)
        
        # 验证要素数量
        expected_count = len(main_gdf) + len(secondary_gdf)
        self.assertEqual(len(result_gdf), expected_count, 
                        f"{layer_type}图层要素数量不符: {len(result_gdf)} != {expected_count}")
        
        # 验证字段
        for field in main_gdf.columns:
            if field != 'geometry':
                self.assertIn(field, result_gdf.columns, f"缺少字段: {field}")
        
        logger.info("融合字段结构不同的Shapefile测试通过")
    
    def test_generate_mapping_template(self):
        """测试生成字段映射模板"""
        logger.info("测试生成字段映射模板")
        
        # 获取输入目录
        main_dir = os.path.join(self.test_data_dir, 'main')
        secondary_dir = os.path.join(self.test_data_dir, 'secondary')
        
        # 检查输入目录是否存在
        self.assertTrue(os.path.exists(main_dir), f"主目录不存在: {main_dir}")
        self.assertTrue(os.path.exists(secondary_dir), f"次要目录不存在: {secondary_dir}")
        
        # 设置输出文件
        output_file = os.path.join(self.output_dir, 'generated_mapping.json')
        
        # 对points图层生成映射模板
        layer_type = 'points'
        
        # 读取主Shapefile
        main_file = os.path.join(main_dir, f"{layer_type}.shp")
        self.assertTrue(os.path.exists(main_file), f"主文件不存在: {main_file}")
        main_gdf = gpd.read_file(main_file)
        
        # 读取次要Shapefile
        secondary_file = os.path.join(secondary_dir, f"{layer_type}.shp")
        self.assertTrue(os.path.exists(secondary_file), f"次要文件不存在: {secondary_file}")
        secondary_gdf = gpd.read_file(secondary_file)
        
        # 生成映射模板
        mapping = {}
        for field in secondary_gdf.columns:
            if field != 'geometry':
                # 尝试找到对应的主字段
                if field in main_gdf.columns:
                    # 字段名相同，直接映射
                    mapping[field] = {
                        'target_field': field,
                        'conversion': 'direct',
                        'default_value': None
                    }
                else:
                    # 字段名不同，创建新字段
                    mapping[field] = {
                        'target_field': field,
                        'conversion': 'new_field',
                        'field_type': str(secondary_gdf[field].dtype),
                        'default_value': None
                    }
        
        # 保存映射模板
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=4, ensure_ascii=False)
        
        # 验证生成结果
        self.assertTrue(os.path.exists(output_file), f"输出文件不存在: {output_file}")
        
        # 读取生成的映射文件
        with open(output_file, 'r', encoding='utf-8') as f:
            generated_mapping = json.load(f)
        
        # 验证映射内容
        for field in secondary_gdf.columns:
            if field != 'geometry':
                self.assertIn(field, generated_mapping, f"缺少字段映射: {field}")
        
        logger.info("生成字段映射模板测试通过")

if __name__ == '__main__':
    unittest.main()

