#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据生成脚本（使用Shapefile格式）

由于在环境中创建FileGDB格式文件遇到问题，我们改用Shapefile格式生成测试数据。
"""

import os
import sys
import logging
import shutil
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString, Polygon

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_points(count, x_min, y_min, x_max, y_max):
    """生成随机点"""
    x = np.random.uniform(x_min, x_max, count)
    y = np.random.uniform(y_min, y_max, count)
    return [Point(x[i], y[i]) for i in range(count)]

def generate_lines(count, x_min, y_min, x_max, y_max):
    """生成随机线"""
    lines = []
    for _ in range(count):
        num_points = np.random.randint(2, 5)
        x = np.random.uniform(x_min, x_max, num_points)
        y = np.random.uniform(y_min, y_max, num_points)
        points = [(x[i], y[i]) for i in range(num_points)]
        lines.append(LineString(points))
    return lines

def generate_polygons(count, x_min, y_min, x_max, y_max):
    """生成随机多边形"""
    polygons = []
    for _ in range(count):
        num_points = np.random.randint(3, 6)
        # 生成凸多边形
        radius = np.random.uniform(0.1, 0.5)
        center_x = np.random.uniform(x_min + radius, x_max - radius)
        center_y = np.random.uniform(y_min + radius, y_max - radius)
        
        angles = np.sort(np.random.uniform(0, 2 * np.pi, num_points))
        x = center_x + radius * np.cos(angles)
        y = center_y + radius * np.sin(angles)
        
        points = [(x[i], y[i]) for i in range(num_points)]
        # 闭合多边形
        points.append(points[0])
        polygons.append(Polygon(points))
    return polygons

def generate_same_schema_shapefiles(output_dir, count=3):
    """
    生成字段结构一致的多个Shapefile文件
    
    Args:
        output_dir: 输出目录
        count: Shapefile文件组数量
    """
    logger.info(f"生成 {count} 组字段结构一致的Shapefile文件")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义图层和字段结构
    layers = {
        'points': {
            'geometry_type': 'Point',
            'generate_func': generate_points,
            'count': 50,
            'fields': {
                'id': np.arange(50),
                'name': [f'Point_{i}' for i in range(50)],
                'value': np.random.uniform(0, 100, 50),
                'category': np.random.choice(['A', 'B', 'C'], 50)
            }
        },
        'lines': {
            'geometry_type': 'LineString',
            'generate_func': generate_lines,
            'count': 30,
            'fields': {
                'id': np.arange(30),
                'name': [f'Line_{i}' for i in range(30)],
                'length': np.random.uniform(1, 10, 30),
                'type': np.random.choice(['Road', 'River', 'Border'], 30)
            }
        },
        'polygons': {
            'geometry_type': 'Polygon',
            'generate_func': generate_polygons,
            'count': 20,
            'fields': {
                'id': np.arange(20),
                'name': [f'Polygon_{i}' for i in range(20)],
                'area': np.random.uniform(1, 5, 20),
                'type': np.random.choice(['Building', 'Lake', 'Forest'], 20)
            }
        }
    }
    
    # 生成多组Shapefile文件
    for i in range(count):
        group_dir = os.path.join(output_dir, f'same_schema_{i+1}')
        os.makedirs(group_dir, exist_ok=True)
        
        # 为每个图层生成数据
        for layer_name, layer_info in layers.items():
            # 生成几何对象
            geometries = layer_info['generate_func'](
                layer_info['count'],
                i * 10, i * 10,  # x_min, y_min
                i * 10 + 10, i * 10 + 10  # x_max, y_max
            )
            
            # 创建GeoDataFrame
            gdf = gpd.GeoDataFrame(
                layer_info['fields'],
                geometry=geometries,
                crs='EPSG:4326'
            )
            
            # 保存为Shapefile
            output_file = os.path.join(group_dir, f'{layer_name}.shp')
            gdf.to_file(output_file)
            logger.info(f"已生成Shapefile: {output_file}")

def generate_different_schema_shapefiles(output_dir):
    """
    生成字段结构不同的Shapefile文件
    
    Args:
        output_dir: 输出目录
    """
    logger.info("生成字段结构不同的Shapefile文件")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义主Shapefile的图层和字段结构
    main_layers = {
        'points': {
            'geometry_type': 'Point',
            'generate_func': generate_points,
            'count': 50,
            'fields': {
                'id': np.arange(50),
                'name': [f'Point_{i}' for i in range(50)],
                'value': np.random.uniform(0, 100, 50),
                'category': np.random.choice(['A', 'B', 'C'], 50)
            }
        },
        'lines': {
            'geometry_type': 'LineString',
            'generate_func': generate_lines,
            'count': 30,
            'fields': {
                'id': np.arange(30),
                'name': [f'Line_{i}' for i in range(30)],
                'length': np.random.uniform(1, 10, 30),
                'type': np.random.choice(['Road', 'River', 'Border'], 30)
            }
        },
        'polygons': {
            'geometry_type': 'Polygon',
            'generate_func': generate_polygons,
            'count': 20,
            'fields': {
                'id': np.arange(20),
                'name': [f'Polygon_{i}' for i in range(20)],
                'area': np.random.uniform(1, 5, 20),
                'type': np.random.choice(['Building', 'Lake', 'Forest'], 20)
            }
        }
    }
    
    # 定义次要Shapefile的图层和字段结构（与主Shapefile结构不同）
    secondary_layers = {
        'points': {
            'geometry_type': 'Point',
            'generate_func': generate_points,
            'count': 40,
            'fields': {
                'point_id': np.arange(40),  # 字段名不同
                'point_name': [f'SecPoint_{i}' for i in range(40)],  # 字段名不同
                'value': np.random.uniform(0, 100, 40),
                'type': np.random.choice(['X', 'Y', 'Z'], 40)  # 字段名不同，与主Shapefile的category对应
            }
        },
        'lines': {
            'geometry_type': 'LineString',
            'generate_func': generate_lines,
            'count': 25,
            'fields': {
                'line_id': np.arange(25),  # 字段名不同
                'line_name': [f'SecLine_{i}' for i in range(25)],  # 字段名不同
                'line_length': np.random.uniform(1, 10, 25),  # 字段名不同
                'category': np.random.choice(['Road', 'River', 'Border'], 25)  # 字段名不同，与主Shapefile的type对应
            }
        },
        'polygons': {
            'geometry_type': 'Polygon',
            'generate_func': generate_polygons,
            'count': 15,
            'fields': {
                'polygon_id': np.arange(15),  # 字段名不同
                'polygon_name': [f'SecPolygon_{i}' for i in range(15)],  # 字段名不同
                'size': np.random.uniform(1, 5, 15),  # 字段名不同，与主Shapefile的area对应
                'category': np.random.choice(['Building', 'Lake', 'Forest'], 15)  # 字段名不同，与主Shapefile的type对应
            }
        }
    }
    
    # 生成主Shapefile文件
    main_dir = os.path.join(output_dir, 'main')
    os.makedirs(main_dir, exist_ok=True)
    
    # 为每个图层生成数据
    for layer_name, layer_info in main_layers.items():
        # 生成几何对象
        geometries = layer_info['generate_func'](
            layer_info['count'],
            0, 0,  # x_min, y_min
            10, 10  # x_max, y_max
        )
        
        # 创建GeoDataFrame
        gdf = gpd.GeoDataFrame(
            layer_info['fields'],
            geometry=geometries,
            crs='EPSG:4326'
        )
        
        # 保存为Shapefile
        output_file = os.path.join(main_dir, f'{layer_name}.shp')
        gdf.to_file(output_file)
        logger.info(f"已生成主Shapefile: {output_file}")
    
    # 生成次要Shapefile文件
    secondary_dir = os.path.join(output_dir, 'secondary')
    os.makedirs(secondary_dir, exist_ok=True)
    
    # 为每个图层生成数据
    for layer_name, layer_info in secondary_layers.items():
        # 生成几何对象
        geometries = layer_info['generate_func'](
            layer_info['count'],
            5, 5,  # x_min, y_min
            15, 15  # x_max, y_max
        )
        
        # 创建GeoDataFrame
        gdf = gpd.GeoDataFrame(
            layer_info['fields'],
            geometry=geometries,
            crs='EPSG:4326'
        )
        
        # 保存为Shapefile
        output_file = os.path.join(secondary_dir, f'{layer_name}.shp')
        gdf.to_file(output_file)
        logger.info(f"已生成次要Shapefile: {output_file}")
    
    # 生成字段映射文件
    mapping = {
        'points': {
            'point_id': {'target_field': 'id', 'conversion': 'direct', 'default_value': None},
            'point_name': {'target_field': 'name', 'conversion': 'direct', 'default_value': None},
            'value': {'target_field': 'value', 'conversion': 'direct', 'default_value': None},
            'type': {'target_field': 'category', 'conversion': 'direct', 'default_value': None}
        },
        'lines': {
            'line_id': {'target_field': 'id', 'conversion': 'direct', 'default_value': None},
            'line_name': {'target_field': 'name', 'conversion': 'direct', 'default_value': None},
            'line_length': {'target_field': 'length', 'conversion': 'direct', 'default_value': None},
            'category': {'target_field': 'type', 'conversion': 'direct', 'default_value': None}
        },
        'polygons': {
            'polygon_id': {'target_field': 'id', 'conversion': 'direct', 'default_value': None},
            'polygon_name': {'target_field': 'name', 'conversion': 'direct', 'default_value': None},
            'size': {'target_field': 'area', 'conversion': 'direct', 'default_value': None},
            'category': {'target_field': 'type', 'conversion': 'direct', 'default_value': None}
        }
    }
    
    # 保存映射文件
    import json
    for layer_name, layer_mapping in mapping.items():
        mapping_file = os.path.join(output_dir, f'{layer_name}_mapping.json')
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(layer_mapping, f, indent=4, ensure_ascii=False)
        logger.info(f"已生成映射文件: {mapping_file}")

def main():
    """主函数"""
    # 获取测试数据目录
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # 生成测试数据
    generate_same_schema_shapefiles(test_data_dir)
    generate_different_schema_shapefiles(test_data_dir)

if __name__ == '__main__':
    main()

