#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
融合功能测试脚本

该脚本用于测试GDB融合工具的功能，包括：
1. 测试融合字段结构一致的多个GDB
2. 测试融合字段结构不同的GDB
"""

import os
import sys
import logging
import unittest
import shutil
from pathlib import Path

import geopandas as gpd
import fiona

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from src.core.fusion import GDBFusion
from src.core.gdb_reader import GDBReader
from src.core.field_mapper import FieldMapper

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestFusion(unittest.TestCase):
    """融合功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试前的准备工作"""
        # 获取测试数据目录
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # 创建输出目录
        cls.output_dir = os.path.join(cls.test_data_dir, 'output')
        os.makedirs(cls.output_dir, exist_ok=True)
        
        # 初始化融合器
        cls.fusion = GDBFusion()
        cls.reader = GDBReader()
        
        # 注册GDB驱动
        fiona.supported_drivers['FileGDB'] = 'rw'  # 读写模式
    
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
        """测试融合字段结构一致的多个GDB"""
        logger.info("测试融合字段结构一致的多个GDB")
        
        # 获取输入GDB文件
        input_gdbs = [
            os.path.join(self.test_data_dir, 'same_schema_1.gdb'),
            os.path.join(self.test_data_dir, 'same_schema_2.gdb'),
            os.path.join(self.test_data_dir, 'same_schema_3.gdb')
        ]
        
        # 检查输入文件是否存在
        for gdb_path in input_gdbs:
            self.assertTrue(os.path.exists(gdb_path), f"输入GDB不存在: {gdb_path}")
        
        # 设置输出GDB文件
        output_gdb = os.path.join(self.output_dir, 'merged_same.gdb')
        
        # 执行融合
        success = self.fusion.merge_same_schema(input_gdbs, output_gdb)
        
        # 验证融合结果
        self.assertTrue(success, "融合失败")
        self.assertTrue(os.path.exists(output_gdb), f"输出GDB不存在: {output_gdb}")
        
        # 读取融合后的GDB
        self.reader.read_gdb(output_gdb)
        
        # 验证图层
        layers = self.reader.get_layers()
        self.assertIn('points', layers, "缺少points图层")
        self.assertIn('lines', layers, "缺少lines图层")
        self.assertIn('polygons', layers, "缺少polygons图层")
        
        # 验证要素数量
        points_count = self.reader.get_layer_feature_count('points')
        lines_count = self.reader.get_layer_feature_count('lines')
        polygons_count = self.reader.get_layer_feature_count('polygons')
        
        # 预期要素数量：每个输入GDB的要素数量之和
        expected_points_count = 50 * 3  # 每个GDB 50个点
        expected_lines_count = 30 * 3  # 每个GDB 30条线
        expected_polygons_count = 20 * 3  # 每个GDB 20个面
        
        self.assertEqual(points_count, expected_points_count, f"points图层要素数量不符: {points_count} != {expected_points_count}")
        self.assertEqual(lines_count, expected_lines_count, f"lines图层要素数量不符: {lines_count} != {expected_lines_count}")
        self.assertEqual(polygons_count, expected_polygons_count, f"polygons图层要素数量不符: {polygons_count} != {expected_polygons_count}")
        
        logger.info("融合字段结构一致的多个GDB测试通过")
    
    def test_merge_different_schema(self):
        """测试融合字段结构不同的GDB"""
        logger.info("测试融合字段结构不同的GDB")
        
        # 获取输入GDB文件
        main_gdb = os.path.join(self.test_data_dir, 'main.gdb')
        secondary_gdb = os.path.join(self.test_data_dir, 'secondary.gdb')
        
        # 检查输入文件是否存在
        self.assertTrue(os.path.exists(main_gdb), f"主GDB不存在: {main_gdb}")
        self.assertTrue(os.path.exists(secondary_gdb), f"次要GDB不存在: {secondary_gdb}")
        
        # 设置输出GDB文件
        output_gdb = os.path.join(self.output_dir, 'merged_diff.gdb')
        
        # 获取映射文件
        points_mapping = os.path.join(self.test_data_dir, 'points_mapping.json')
        
        # 检查映射文件是否存在
        self.assertTrue(os.path.exists(points_mapping), f"映射文件不存在: {points_mapping}")
        
        # 执行融合（仅融合points图层）
        success = self.fusion.merge_different_schema(
            main_gdb,
            secondary_gdb,
            output_gdb,
            points_mapping,
            ['points']
        )
        
        # 验证融合结果
        self.assertTrue(success, "融合失败")
        self.assertTrue(os.path.exists(output_gdb), f"输出GDB不存在: {output_gdb}")
        
        # 读取融合后的GDB
        self.reader.read_gdb(output_gdb)
        
        # 验证图层
        layers = self.reader.get_layers()
        self.assertIn('points', layers, "缺少points图层")
        
        # 验证要素数量
        points_count = self.reader.get_layer_feature_count('points')
        
        # 预期要素数量：主GDB的要素数量 + 次要GDB的要素数量
        expected_points_count = 50 + 40  # 主GDB 50个点，次要GDB 40个点
        
        self.assertEqual(points_count, expected_points_count, f"points图层要素数量不符: {points_count} != {expected_points_count}")
        
        # 读取融合后的数据
        points_gdf = self.reader.read_layer_data('points')
        
        # 验证字段
        self.assertIn('id', points_gdf.columns, "缺少id字段")
        self.assertIn('name', points_gdf.columns, "缺少name字段")
        self.assertIn('value', points_gdf.columns, "缺少value字段")
        self.assertIn('category', points_gdf.columns, "缺少category字段")
        
        logger.info("融合字段结构不同的GDB测试通过")
    
    def test_generate_mapping_template(self):
        """测试生成字段映射模板"""
        logger.info("测试生成字段映射模板")
        
        # 获取输入GDB文件
        main_gdb = os.path.join(self.test_data_dir, 'main.gdb')
        secondary_gdb = os.path.join(self.test_data_dir, 'secondary.gdb')
        
        # 检查输入文件是否存在
        self.assertTrue(os.path.exists(main_gdb), f"主GDB不存在: {main_gdb}")
        self.assertTrue(os.path.exists(secondary_gdb), f"次要GDB不存在: {secondary_gdb}")
        
        # 设置输出映射文件
        output_mapping = os.path.join(self.output_dir, 'generated_mapping.json')
        
        # 执行生成映射模板
        success = self.fusion.generate_mapping_template(
            main_gdb,
            secondary_gdb,
            'points',
            output_mapping
        )
        
        # 验证生成结果
        self.assertTrue(success, "生成映射模板失败")
        self.assertTrue(os.path.exists(output_mapping), f"输出映射文件不存在: {output_mapping}")
        
        # 读取生成的映射文件
        import json
        with open(output_mapping, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        # 验证映射内容
        self.assertIn('point_id', mapping, "缺少point_id映射")
        self.assertIn('point_name', mapping, "缺少point_name映射")
        self.assertIn('value', mapping, "缺少value映射")
        self.assertIn('type', mapping, "缺少type映射")
        
        logger.info("生成字段映射模板测试通过")

if __name__ == '__main__':
    unittest.main()

