#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GDB融合工具主程序入口

该模块是GDB融合工具的主程序入口，用于启动命令行界面或图形用户界面。
"""

import sys
import argparse
import logging

from .ui.cli import CLI
from .ui.gui import GUI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主程序入口函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='GDB融合工具 - 用于融合多个GDB文件',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加参数
    parser.add_argument('--gui', action='store_true', help='启动图形用户界面')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
    
    # 解析参数
    args, remaining_args = parser.parse_known_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 根据参数启动相应界面
    if args.gui:
        # 启动图形用户界面
        logger.info("启动图形用户界面")
        gui = GUI()
        gui.run()
    else:
        # 启动命令行界面
        logger.info("启动命令行界面")
        cli = CLI()
        sys.exit(cli.run(remaining_args))

if __name__ == '__main__':
    main()

