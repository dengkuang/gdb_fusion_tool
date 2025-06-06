#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令行界面模块

该模块提供命令行操作接口，用于在命令行中使用GDB融合工具。
"""

import os
import sys
import argparse
import logging
from typing import List, Optional, Dict, Any

from ..core.fusion import GDBFusion
from ..core.field_mapper import FieldMapper
from ..utils.validation import validate_gdb, validate_output_path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CLI:
    """
    命令行界面类
    
    提供命令行操作接口。
    """
    
    def __init__(self):
        """初始化命令行界面"""
        self.parser = self._create_parser()
        self.fusion = GDBFusion()
        self.field_mapper = FieldMapper()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        创建命令行参数解析器
        
        Returns:
            argparse.ArgumentParser: 参数解析器
        """
        # 创建主解析器
        parser = argparse.ArgumentParser(
            description='GDB融合工具 - 用于融合多个GDB文件',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 添加子命令
        subparsers = parser.add_subparsers(dest='command', help='子命令')
        
        # 融合相同结构的GDB
        merge_same = subparsers.add_parser('merge-same', help='融合字段结构一致的多个GDB')
        merge_same.add_argument('--input', '-i', required=True, nargs='+', help='输入GDB文件路径列表')
        merge_same.add_argument('--output', '-o', required=True, help='输出GDB文件路径')
        merge_same.add_argument('--layers', '-l', nargs='+', help='要处理的图层列表，如果不指定则处理所有图层')
        merge_same.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
        
        # 融合不同结构的GDB
        merge_diff = subparsers.add_parser('merge-diff', help='融合字段结构不同的GDB')
        merge_diff.add_argument('--main', '-m', required=True, help='主GDB文件路径')
        merge_diff.add_argument('--secondary', '-s', required=True, help='次要GDB文件路径')
        merge_diff.add_argument('--output', '-o', required=True, help='输出GDB文件路径')
        merge_diff.add_argument('--mapping', '-p', help='字段映射配置文件路径')
        merge_diff.add_argument('--layers', '-l', nargs='+', help='要处理的图层列表，如果不指定则处理所有图层')
        merge_diff.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
        
        # 生成字段映射模板
        gen_mapping = subparsers.add_parser('gen-mapping', help='生成字段映射模板')
        gen_mapping.add_argument('--main', '-m', required=True, help='主GDB文件路径')
        gen_mapping.add_argument('--secondary', '-s', required=True, help='次要GDB文件路径')
        gen_mapping.add_argument('--layer', '-l', required=True, help='图层名称')
        gen_mapping.add_argument('--output', '-o', required=True, help='输出映射文件路径')
        gen_mapping.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        解析命令行参数
        
        Args:
            args: 命令行参数列表，如果为None则使用sys.argv
            
        Returns:
            argparse.Namespace: 解析后的参数
        """
        return self.parser.parse_args(args)
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        运行命令行工具
        
        Args:
            args: 命令行参数列表，如果为None则使用sys.argv
            
        Returns:
            int: 退出码，0表示成功，非0表示失败
        """
        # 解析参数
        args = self.parse_args(args)
        
        # 设置日志级别
        if hasattr(args, 'verbose') and args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 根据子命令执行相应操作
        if args.command == 'merge-same':
            return self._run_merge_same(args)
        elif args.command == 'merge-diff':
            return self._run_merge_diff(args)
        elif args.command == 'gen-mapping':
            return self._run_gen_mapping(args)
        else:
            self.parser.print_help()
            return 1
    
    def _run_merge_same(self, args: argparse.Namespace) -> int:
        """
        运行融合相同结构的GDB命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码，0表示成功，非0表示失败
        """
        # 验证输入GDB
        for gdb_path in args.input:
            is_valid, error = validate_gdb(gdb_path)
            if not is_valid:
                logger.error(f"输入GDB无效: {gdb_path} - {error}")
                return 1
        
        # 验证输出路径
        is_valid, error = validate_output_path(args.output)
        if not is_valid:
            logger.error(f"输出路径无效: {args.output} - {error}")
            return 1
        
        # 执行融合
        success = self.fusion.merge_same_schema(
            args.input,
            args.output,
            args.layers
        )
        
        if success:
            logger.info(f"成功融合GDB文件到: {args.output}")
            return 0
        else:
            logger.error("融合GDB文件失败")
            return 1
    
    def _run_merge_diff(self, args: argparse.Namespace) -> int:
        """
        运行融合不同结构的GDB命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码，0表示成功，非0表示失败
        """
        # 验证主GDB
        is_valid, error = validate_gdb(args.main)
        if not is_valid:
            logger.error(f"主GDB无效: {args.main} - {error}")
            return 1
        
        # 验证次要GDB
        is_valid, error = validate_gdb(args.secondary)
        if not is_valid:
            logger.error(f"次要GDB无效: {args.secondary} - {error}")
            return 1
        
        # 验证输出路径
        is_valid, error = validate_output_path(args.output)
        if not is_valid:
            logger.error(f"输出路径无效: {args.output} - {error}")
            return 1
        
        # 验证映射文件
        if args.mapping and not os.path.exists(args.mapping):
            logger.error(f"映射文件不存在: {args.mapping}")
            return 1
        
        # 执行融合
        success = self.fusion.merge_different_schema(
            args.main,
            args.secondary,
            args.output,
            args.mapping,
            args.layers
        )
        
        if success:
            logger.info(f"成功融合GDB文件到: {args.output}")
            return 0
        else:
            logger.error("融合GDB文件失败")
            return 1
    
    def _run_gen_mapping(self, args: argparse.Namespace) -> int:
        """
        运行生成字段映射模板命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码，0表示成功，非0表示失败
        """
        # 验证主GDB
        is_valid, error = validate_gdb(args.main)
        if not is_valid:
            logger.error(f"主GDB无效: {args.main} - {error}")
            return 1
        
        # 验证次要GDB
        is_valid, error = validate_gdb(args.secondary)
        if not is_valid:
            logger.error(f"次要GDB无效: {args.secondary} - {error}")
            return 1
        
        # 验证输出路径
        is_valid, error = validate_output_path(args.output)
        if not is_valid:
            logger.error(f"输出路径无效: {args.output} - {error}")
            return 1
        
        # 执行生成映射模板
        success = self.fusion.generate_mapping_template(
            args.main,
            args.secondary,
            args.layer,
            args.output
        )
        
        if success:
            logger.info(f"成功生成字段映射模板: {args.output}")
            return 0
        else:
            logger.error("生成字段映射模板失败")
            return 1

def main():
    """命令行入口函数"""
    cli = CLI()
    sys.exit(cli.run())

if __name__ == '__main__':
    main()

