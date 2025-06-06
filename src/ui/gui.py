#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图形用户界面模块

该模块提供简单的图形用户界面，使用tkinter库实现。
"""

import os
import sys
import logging
import threading
import json
from typing import List, Dict, Any, Optional, Callable
from tkinter import Tk, Frame, Label, Button, Entry, Text, Scrollbar, StringVar, OptionMenu
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font

from ..core.fusion import GDBFusion
from ..core.gdb_reader import GDBReader
from ..core.field_mapper import FieldMapper
from ..utils.validation import validate_gdb, validate_output_path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedirectText:
    """
    重定向文本类
    
    用于将日志重定向到Text控件。
    """
    
    def __init__(self, text_widget):
        """
        初始化重定向文本
        
        Args:
            text_widget: Text控件
        """
        self.text_widget = text_widget
        self.buffer = ""
    
    def write(self, string):
        """
        写入文本
        
        Args:
            string: 要写入的文本
        """
        self.buffer += string
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
    
    def flush(self):
        """刷新缓冲区"""
        self.text_widget.update_idletasks()

class GUI:
    """
    图形用户界面类
    
    提供简单的图形用户界面。
    """
    
    def __init__(self, root=None):
        """
        初始化图形用户界面
        
        Args:
            root: Tkinter根窗口，如果为None则创建新窗口
        """
        self.root = root or Tk()
        self.root.title("GDB融合工具")
        self.root.geometry("800x600")
        
        self.fusion = GDBFusion()
        self.reader = GDBReader()
        self.field_mapper = FieldMapper()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面控件"""
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建选项卡页面
        self.tab_same = Frame(self.notebook)
        self.tab_diff = Frame(self.notebook)
        self.tab_mapping = Frame(self.notebook)
        
        self.notebook.add(self.tab_same, text="融合相同结构GDB")
        self.notebook.add(self.tab_diff, text="融合不同结构GDB")
        self.notebook.add(self.tab_mapping, text="生成字段映射")
        
        # 创建各选项卡的控件
        self.create_same_tab()
        self.create_diff_tab()
        self.create_mapping_tab()
        
        # 创建日志区域
        self.create_log_area()
    
    def create_same_tab(self):
        """创建融合相同结构GDB选项卡"""
        # 输入GDB
        Label(self.tab_same, text="输入GDB文件:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.same_input_text = Text(self.tab_same, height=5, width=50)
        self.same_input_text.grid(row=0, column=1, padx=5, pady=5)
        Button(self.tab_same, text="浏览...", command=self.browse_same_input).grid(row=0, column=2, padx=5, pady=5)
        
        # 输出GDB
        Label(self.tab_same, text="输出GDB文件:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.same_output_var = StringVar()
        Entry(self.tab_same, textvariable=self.same_output_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        Button(self.tab_same, text="浏览...", command=self.browse_same_output).grid(row=1, column=2, padx=5, pady=5)
        
        # 图层过滤
        Label(self.tab_same, text="图层过滤:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.same_layers_text = Text(self.tab_same, height=3, width=50)
        self.same_layers_text.grid(row=2, column=1, padx=5, pady=5)
        Button(self.tab_same, text="选择...", command=self.select_same_layers).grid(row=2, column=2, padx=5, pady=5)
        
        # 执行按钮
        Button(self.tab_same, text="执行融合", command=self.run_merge_same).grid(row=3, column=1, padx=5, pady=20)
    
    def create_diff_tab(self):
        """创建融合不同结构GDB选项卡"""
        # 主GDB
        Label(self.tab_diff, text="主GDB文件:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.diff_main_var = StringVar()
        Entry(self.tab_diff, textvariable=self.diff_main_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        Button(self.tab_diff, text="浏览...", command=self.browse_diff_main).grid(row=0, column=2, padx=5, pady=5)
        
        # 次要GDB
        Label(self.tab_diff, text="次要GDB文件:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.diff_secondary_var = StringVar()
        Entry(self.tab_diff, textvariable=self.diff_secondary_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        Button(self.tab_diff, text="浏览...", command=self.browse_diff_secondary).grid(row=1, column=2, padx=5, pady=5)
        
        # 输出GDB
        Label(self.tab_diff, text="输出GDB文件:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.diff_output_var = StringVar()
        Entry(self.tab_diff, textvariable=self.diff_output_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        Button(self.tab_diff, text="浏览...", command=self.browse_diff_output).grid(row=2, column=2, padx=5, pady=5)
        
        # 映射文件
        Label(self.tab_diff, text="映射文件:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.diff_mapping_var = StringVar()
        Entry(self.tab_diff, textvariable=self.diff_mapping_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        Button(self.tab_diff, text="浏览...", command=self.browse_diff_mapping).grid(row=3, column=2, padx=5, pady=5)
        
        # 图层过滤
        Label(self.tab_diff, text="图层过滤:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.diff_layers_text = Text(self.tab_diff, height=3, width=50)
        self.diff_layers_text.grid(row=4, column=1, padx=5, pady=5)
        Button(self.tab_diff, text="选择...", command=self.select_diff_layers).grid(row=4, column=2, padx=5, pady=5)
        
        # 执行按钮
        Button(self.tab_diff, text="执行融合", command=self.run_merge_diff).grid(row=5, column=1, padx=5, pady=20)
    
    def create_mapping_tab(self):
        """创建生成字段映射选项卡"""
        # 主GDB
        Label(self.tab_mapping, text="主GDB文件:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mapping_main_var = StringVar()
        Entry(self.tab_mapping, textvariable=self.mapping_main_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        Button(self.tab_mapping, text="浏览...", command=self.browse_mapping_main).grid(row=0, column=2, padx=5, pady=5)
        
        # 次要GDB
        Label(self.tab_mapping, text="次要GDB文件:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mapping_secondary_var = StringVar()
        Entry(self.tab_mapping, textvariable=self.mapping_secondary_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        Button(self.tab_mapping, text="浏览...", command=self.browse_mapping_secondary).grid(row=1, column=2, padx=5, pady=5)
        
        # 图层选择
        Label(self.tab_mapping, text="图层:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.mapping_layer_var = StringVar()
        self.mapping_layer_menu = OptionMenu(self.tab_mapping, self.mapping_layer_var, "")
        self.mapping_layer_menu.config(width=45)
        self.mapping_layer_menu.grid(row=2, column=1, padx=5, pady=5)
        Button(self.tab_mapping, text="刷新", command=self.refresh_mapping_layers).grid(row=2, column=2, padx=5, pady=5)
        
        # 输出文件
        Label(self.tab_mapping, text="输出文件:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.mapping_output_var = StringVar()
        Entry(self.tab_mapping, textvariable=self.mapping_output_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        Button(self.tab_mapping, text="浏览...", command=self.browse_mapping_output).grid(row=3, column=2, padx=5, pady=5)
        
        # 执行按钮
        Button(self.tab_mapping, text="生成映射", command=self.run_gen_mapping).grid(row=4, column=1, padx=5, pady=20)
    
    def create_log_area(self):
        """创建日志区域"""
        log_frame = Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        Label(log_frame, text="日志:").pack(anchor="w")
        
        # 创建日志文本框和滚动条
        self.log_text = Text(log_frame, height=10, width=80)
        scrollbar = Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 重定向标准输出和标准错误到日志文本框
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect
        sys.stderr = self.redirect
    
    def browse_same_input(self):
        """浏览融合相同结构GDB的输入文件"""
        filepaths = filedialog.askopenfilenames(
            title="选择输入GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepaths:
            self.same_input_text.delete("1.0", "end")
            self.same_input_text.insert("1.0", "\n".join(filepaths))
    
    def browse_same_output(self):
        """浏览融合相同结构GDB的输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="选择输出GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.same_output_var.set(filepath)
    
    def select_same_layers(self):
        """选择融合相同结构GDB的图层"""
        # 获取输入GDB
        input_text = self.same_input_text.get("1.0", "end").strip()
        if not input_text:
            messagebox.showerror("错误", "请先选择输入GDB文件")
            return
        
        input_gdbs = input_text.split("\n")
        if not input_gdbs:
            messagebox.showerror("错误", "请先选择输入GDB文件")
            return
        
        # 读取第一个GDB的图层
        if not self.reader.read_gdb(input_gdbs[0]):
            messagebox.showerror("错误", f"无法读取GDB文件: {input_gdbs[0]}")
            return
        
        layers = self.reader.get_layers()
        if not layers:
            messagebox.showerror("错误", f"GDB文件中没有图层: {input_gdbs[0]}")
            return
        
        # 创建图层选择对话框
        layer_dialog = Tk()
        layer_dialog.title("选择图层")
        layer_dialog.geometry("300x400")
        
        # 创建图层列表
        frame = Frame(layer_dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        Label(frame, text="选择要处理的图层:").pack(anchor="w")
        
        # 创建复选框
        layer_vars = {}
        for layer in layers:
            var = StringVar(value="1")  # 默认选中
            layer_vars[layer] = var
            ttk.Checkbutton(frame, text=layer, variable=var, onvalue="1", offvalue="0").pack(anchor="w")
        
        # 确定按钮
        def on_confirm():
            selected_layers = [layer for layer, var in layer_vars.items() if var.get() == "1"]
            self.same_layers_text.delete("1.0", "end")
            self.same_layers_text.insert("1.0", "\n".join(selected_layers))
            layer_dialog.destroy()
        
        Button(frame, text="确定", command=on_confirm).pack(pady=10)
        
        layer_dialog.mainloop()
    
    def browse_diff_main(self):
        """浏览融合不同结构GDB的主GDB文件"""
        filepath = filedialog.askopenfilename(
            title="选择主GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.diff_main_var.set(filepath)
    
    def browse_diff_secondary(self):
        """浏览融合不同结构GDB的次要GDB文件"""
        filepath = filedialog.askopenfilename(
            title="选择次要GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.diff_secondary_var.set(filepath)
    
    def browse_diff_output(self):
        """浏览融合不同结构GDB的输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="选择输出GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.diff_output_var.set(filepath)
    
    def browse_diff_mapping(self):
        """浏览融合不同结构GDB的映射文件"""
        filepath = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            self.diff_mapping_var.set(filepath)
    
    def select_diff_layers(self):
        """选择融合不同结构GDB的图层"""
        # 获取主GDB
        main_gdb = self.diff_main_var.get()
        if not main_gdb:
            messagebox.showerror("错误", "请先选择主GDB文件")
            return
        
        # 读取主GDB的图层
        if not self.reader.read_gdb(main_gdb):
            messagebox.showerror("错误", f"无法读取GDB文件: {main_gdb}")
            return
        
        layers = self.reader.get_layers()
        if not layers:
            messagebox.showerror("错误", f"GDB文件中没有图层: {main_gdb}")
            return
        
        # 创建图层选择对话框
        layer_dialog = Tk()
        layer_dialog.title("选择图层")
        layer_dialog.geometry("300x400")
        
        # 创建图层列表
        frame = Frame(layer_dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        Label(frame, text="选择要处理的图层:").pack(anchor="w")
        
        # 创建复选框
        layer_vars = {}
        for layer in layers:
            var = StringVar(value="1")  # 默认选中
            layer_vars[layer] = var
            ttk.Checkbutton(frame, text=layer, variable=var, onvalue="1", offvalue="0").pack(anchor="w")
        
        # 确定按钮
        def on_confirm():
            selected_layers = [layer for layer, var in layer_vars.items() if var.get() == "1"]
            self.diff_layers_text.delete("1.0", "end")
            self.diff_layers_text.insert("1.0", "\n".join(selected_layers))
            layer_dialog.destroy()
        
        Button(frame, text="确定", command=on_confirm).pack(pady=10)
        
        layer_dialog.mainloop()
    
    def browse_mapping_main(self):
        """浏览生成字段映射的主GDB文件"""
        filepath = filedialog.askopenfilename(
            title="选择主GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.mapping_main_var.set(filepath)
    
    def browse_mapping_secondary(self):
        """浏览生成字段映射的次要GDB文件"""
        filepath = filedialog.askopenfilename(
            title="选择次要GDB文件",
            filetypes=[("GDB文件", "*.gdb"), ("所有文件", "*.*")]
        )
        if filepath:
            self.mapping_secondary_var.set(filepath)
    
    def browse_mapping_output(self):
        """浏览生成字段映射的输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="选择输出文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            self.mapping_output_var.set(filepath)
    
    def refresh_mapping_layers(self):
        """刷新生成字段映射的图层列表"""
        # 获取主GDB和次要GDB
        main_gdb = self.mapping_main_var.get()
        secondary_gdb = self.mapping_secondary_var.get()
        
        if not main_gdb or not secondary_gdb:
            messagebox.showerror("错误", "请先选择主GDB和次要GDB文件")
            return
        
        # 读取主GDB的图层
        if not self.reader.read_gdb(main_gdb):
            messagebox.showerror("错误", f"无法读取GDB文件: {main_gdb}")
            return
        
        main_layers = set(self.reader.get_layers())
        
        # 读取次要GDB的图层
        secondary_reader = GDBReader()
        if not secondary_reader.read_gdb(secondary_gdb):
            messagebox.showerror("错误", f"无法读取GDB文件: {secondary_gdb}")
            return
        
        secondary_layers = set(secondary_reader.get_layers())
        
        # 获取共有图层
        common_layers = main_layers.intersection(secondary_layers)
        
        if not common_layers:
            messagebox.showerror("错误", "主GDB和次要GDB没有共同的图层")
            return
        
        # 更新图层下拉菜单
        menu = self.mapping_layer_menu["menu"]
        menu.delete(0, "end")
        
        for layer in sorted(common_layers):
            menu.add_command(label=layer, command=lambda l=layer: self.mapping_layer_var.set(l))
        
        # 设置默认选择第一个图层
        self.mapping_layer_var.set(next(iter(sorted(common_layers))))
    
    def run_merge_same(self):
        """运行融合相同结构的GDB"""
        # 获取参数
        input_text = self.same_input_text.get("1.0", "end").strip()
        if not input_text:
            messagebox.showerror("错误", "请选择输入GDB文件")
            return
        
        input_gdbs = input_text.split("\n")
        if len(input_gdbs) < 2:
            messagebox.showerror("错误", "至少需要两个GDB文件进行融合")
            return
        
        output_gdb = self.same_output_var.get()
        if not output_gdb:
            messagebox.showerror("错误", "请选择输出GDB文件")
            return
        
        layers_text = self.same_layers_text.get("1.0", "end").strip()
        layers = layers_text.split("\n") if layers_text else None
        
        # 验证输入GDB
        for gdb_path in input_gdbs:
            is_valid, error = validate_gdb(gdb_path)
            if not is_valid:
                messagebox.showerror("错误", f"输入GDB无效: {gdb_path} - {error}")
                return
        
        # 验证输出路径
        is_valid, error = validate_output_path(output_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"输出路径无效: {output_gdb} - {error}")
            return
        
        # 在新线程中执行融合
        def run_task():
            try:
                success = self.fusion.merge_same_schema(
                    input_gdbs,
                    output_gdb,
                    layers
                )
                
                if success:
                    messagebox.showinfo("成功", f"成功融合GDB文件到: {output_gdb}")
                else:
                    messagebox.showerror("错误", "融合GDB文件失败")
            except Exception as e:
                messagebox.showerror("错误", f"融合GDB文件时出错: {str(e)}")
        
        threading.Thread(target=run_task).start()
    
    def run_merge_diff(self):
        """运行融合不同结构的GDB"""
        # 获取参数
        main_gdb = self.diff_main_var.get()
        if not main_gdb:
            messagebox.showerror("错误", "请选择主GDB文件")
            return
        
        secondary_gdb = self.diff_secondary_var.get()
        if not secondary_gdb:
            messagebox.showerror("错误", "请选择次要GDB文件")
            return
        
        output_gdb = self.diff_output_var.get()
        if not output_gdb:
            messagebox.showerror("错误", "请选择输出GDB文件")
            return
        
        mapping_file = self.diff_mapping_var.get()
        
        layers_text = self.diff_layers_text.get("1.0", "end").strip()
        layers = layers_text.split("\n") if layers_text else None
        
        # 验证主GDB
        is_valid, error = validate_gdb(main_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"主GDB无效: {main_gdb} - {error}")
            return
        
        # 验证次要GDB
        is_valid, error = validate_gdb(secondary_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"次要GDB无效: {secondary_gdb} - {error}")
            return
        
        # 验证输出路径
        is_valid, error = validate_output_path(output_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"输出路径无效: {output_gdb} - {error}")
            return
        
        # 验证映射文件
        if mapping_file and not os.path.exists(mapping_file):
            messagebox.showerror("错误", f"映射文件不存在: {mapping_file}")
            return
        
        # 在新线程中执行融合
        def run_task():
            try:
                success = self.fusion.merge_different_schema(
                    main_gdb,
                    secondary_gdb,
                    output_gdb,
                    mapping_file,
                    layers
                )
                
                if success:
                    messagebox.showinfo("成功", f"成功融合GDB文件到: {output_gdb}")
                else:
                    messagebox.showerror("错误", "融合GDB文件失败")
            except Exception as e:
                messagebox.showerror("错误", f"融合GDB文件时出错: {str(e)}")
        
        threading.Thread(target=run_task).start()
    
    def run_gen_mapping(self):
        """运行生成字段映射模板"""
        # 获取参数
        main_gdb = self.mapping_main_var.get()
        if not main_gdb:
            messagebox.showerror("错误", "请选择主GDB文件")
            return
        
        secondary_gdb = self.mapping_secondary_var.get()
        if not secondary_gdb:
            messagebox.showerror("错误", "请选择次要GDB文件")
            return
        
        layer = self.mapping_layer_var.get()
        if not layer:
            messagebox.showerror("错误", "请选择图层")
            return
        
        output_file = self.mapping_output_var.get()
        if not output_file:
            messagebox.showerror("错误", "请选择输出文件")
            return
        
        # 验证主GDB
        is_valid, error = validate_gdb(main_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"主GDB无效: {main_gdb} - {error}")
            return
        
        # 验证次要GDB
        is_valid, error = validate_gdb(secondary_gdb)
        if not is_valid:
            messagebox.showerror("错误", f"次要GDB无效: {secondary_gdb} - {error}")
            return
        
        # 验证输出路径
        is_valid, error = validate_output_path(output_file)
        if not is_valid:
            messagebox.showerror("错误", f"输出路径无效: {output_file} - {error}")
            return
        
        # 在新线程中执行生成映射模板
        def run_task():
            try:
                success = self.fusion.generate_mapping_template(
                    main_gdb,
                    secondary_gdb,
                    layer,
                    output_file
                )
                
                if success:
                    messagebox.showinfo("成功", f"成功生成字段映射模板: {output_file}")
                else:
                    messagebox.showerror("错误", "生成字段映射模板失败")
            except Exception as e:
                messagebox.showerror("错误", f"生成字段映射模板时出错: {str(e)}")
        
        threading.Thread(target=run_task).start()
    
    def run(self):
        """运行图形界面"""
        self.root.mainloop()

def main():
    """图形界面入口函数"""
    gui = GUI()
    gui.run()

if __name__ == '__main__':
    main()

