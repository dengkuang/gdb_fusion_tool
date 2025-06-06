#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行测试脚本（使用Shapefile格式）

该脚本用于运行使用Shapefile格式的测试，包括：
1. 生成Shapefile格式的测试数据
2. 运行测试用例
"""

import os
import sys
import logging
import unittest
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    # 生成测试数据
    logger.info("生成Shapefile格式的测试数据...")
    from generate_test_data_shapefile import main as generate_data
    generate_data()
    
    # 运行测试用例
    logger.info("运行测试用例...")
    
    # 加载测试模块
    from test_fusion_shapefile import TestFusionShapefile
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestFusionShapefile))
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # 输出测试结果
    logger.info(f"测试完成，共运行 {test_result.testsRun} 个测试")
    logger.info(f"成功: {test_result.testsRun - len(test_result.errors) - len(test_result.failures)}")
    logger.info(f"失败: {len(test_result.failures)}")
    logger.info(f"错误: {len(test_result.errors)}")
    
    # 返回退出码
    return 0 if test_result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())

