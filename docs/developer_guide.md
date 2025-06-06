# GDB融合工具开发者指南

**版本：** 0.1.0  
**作者：** Manus AI  
**日期：** 2025-06-06

## 目录

1. [简介](#1-简介)
2. [系统架构](#2-系统架构)
3. [核心模块](#3-核心模块)
4. [工具函数模块](#4-工具函数模块)
5. [用户界面模块](#5-用户界面模块)
6. [配置管理模块](#6-配置管理模块)
7. [数据流](#7-数据流)
8. [扩展指南](#8-扩展指南)
9. [测试](#9-测试)
10. [构建与部署](#10-构建与部署)
11. [参考资料](#11-参考资料)

## 1. 简介

本文档面向GDB融合工具的开发者，详细说明工具的架构、实现细节和扩展方法。GDB融合工具是一个基于Python的地理数据库(GDB)融合工具，用于合并和整合多个GDB文件的数据。

### 1.1 技术栈

GDB融合工具使用以下技术栈：

- **编程语言**：Python 3.6+
- **地理空间库**：
  - Fiona：用于读写地理空间数据
  - GeoPandas：用于处理地理空间数据
  - Shapely：用于处理几何对象
- **用户界面**：
  - 命令行界面：使用argparse库
  - 图形用户界面：使用tkinter库
- **其他库**：
  - tqdm：用于显示进度条
  - pandas：用于数据处理
  - numpy：用于数值计算
  - logging：用于日志记录

### 1.2 开发环境设置

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/gdb_fusion_tool.git
cd gdb_fusion_tool
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 安装开发依赖：

```bash
pip install -e ".[dev]"
```

4. 安装pre-commit钩子：

```bash
pre-commit install
```

## 2. 系统架构

GDB融合工具采用模块化设计，主要包含以下组件：

```
gdb_fusion_tool/
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── core/               # 核心功能模块
│   │   ├── __init__.py
│   │   ├── gdb_reader.py   # GDB读取模块
│   │   ├── gdb_writer.py   # GDB写入模块
│   │   ├── field_mapper.py # 字段映射模块
│   │   └── fusion.py       # 融合逻辑模块
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── validation.py   # 数据验证
│   │   └── conversion.py   # 数据转换
│   ├── ui/                 # 用户界面
│   │   ├── __init__.py
│   │   ├── cli.py          # 命令行界面
│   │   └── gui.py          # 图形用户界面
│   ├── config/             # 配置管理
│   │   ├── __init__.py
│   │   └── config_manager.py # 配置管理器
│   └── __main__.py         # 主程序入口
├── tests/                  # 测试目录
├── docs/                   # 文档目录
└── examples/               # 示例目录
```

### 2.1 设计原则

GDB融合工具的设计遵循以下原则：

1. **模块化**：将功能分解为独立的模块，便于维护和扩展
2. **单一职责**：每个模块只负责一个功能
3. **接口分离**：通过定义清晰的接口分离不同模块
4. **依赖注入**：通过参数传递依赖，而不是在模块内部创建
5. **错误处理**：使用异常处理机制捕获和处理错误

### 2.2 依赖关系

模块之间的依赖关系如下：

- `fusion.py` 依赖 `gdb_reader.py`、`gdb_writer.py` 和 `field_mapper.py`
- `gdb_reader.py` 和 `gdb_writer.py` 依赖 `fiona` 和 `geopandas`
- `field_mapper.py` 依赖 `conversion.py`
- `cli.py` 和 `gui.py` 依赖 `fusion.py`
- `__main__.py` 依赖 `cli.py` 和 `gui.py`

## 3. 核心模块

### 3.1 GDB读取模块 (gdb_reader.py)

GDB读取模块负责读取GDB文件，提取图层和属性信息。

#### 3.1.1 主要类和函数

- `GDBReader`: 读取GDB文件的主类
  - `read_gdb(gdb_path)`: 读取GDB文件
  - `get_layers()`: 获取GDB中的图层列表
  - `get_layer_schema(layer_name)`: 获取图层的字段结构
  - `read_layer_data(layer_name)`: 读取图层数据
  - `get_layer_feature_count(layer_name)`: 获取图层要素数量
  - `get_layer_crs(layer_name)`: 获取图层坐标参考系统
  - `compare_layer_schemas(layer_name1, layer_name2)`: 比较两个图层的字段结构是否一致
  - `close()`: 关闭GDB文件

#### 3.1.2 实现细节

GDB读取模块使用Fiona库读取GDB文件，并使用GeoPandas处理地理空间数据。主要实现步骤：

1. 注册GDB驱动
2. 打开GDB文件
3. 获取图层列表
4. 读取图层结构和数据
5. 关闭GDB文件

#### 3.1.3 示例代码

```python
from src.core.gdb_reader import GDBReader

# 创建GDB读取器
reader = GDBReader()

# 读取GDB文件
reader.read_gdb("path/to/file.gdb")

# 获取图层列表
layers = reader.get_layers()
print(f"图层列表: {layers}")

# 读取图层数据
for layer_name in layers:
    gdf = reader.read_layer_data(layer_name)
    print(f"图层 {layer_name} 有 {len(gdf)} 个要素")

# 关闭GDB文件
reader.close()
```

### 3.2 GDB写入模块 (gdb_writer.py)

GDB写入模块负责创建和写入GDB文件。

#### 3.2.1 主要类和函数

- `GDBWriter`: 写入GDB文件的主类
  - `create_gdb(gdb_path)`: 创建新的GDB文件
  - `create_layer(layer_name, schema, crs)`: 创建图层
  - `write_features(layer_name, features)`: 写入要素
  - `write_geodataframe(layer_name, gdf)`: 写入GeoDataFrame
  - `finalize()`: 完成写入并关闭文件
  - `close()`: 关闭GDB文件

#### 3.2.2 实现细节

GDB写入模块使用Fiona库写入GDB文件，并使用GeoPandas处理地理空间数据。主要实现步骤：

1. 注册GDB驱动
2. 创建GDB文件
3. 创建图层
4. 写入要素
5. 完成写入并关闭文件

#### 3.2.3 示例代码

```python
from src.core.gdb_writer import GDBWriter
import geopandas as gpd
from shapely.geometry import Point

# 创建GDB写入器
writer = GDBWriter()

# 创建GDB文件
writer.create_gdb("path/to/output.gdb")

# 创建GeoDataFrame
geometry = [Point(0, 0), Point(1, 1), Point(2, 2)]
data = {'id': [1, 2, 3], 'name': ['A', 'B', 'C']}
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs='EPSG:4326')

# 写入GeoDataFrame
writer.write_geodataframe("points", gdf)

# 完成写入
writer.finalize()
```

### 3.3 字段映射模块 (field_mapper.py)

字段映射模块负责处理字段映射关系。

#### 3.3.1 主要类和函数

- `FieldMapper`: 字段映射主类
  - `create_mapping(source_schema, target_schema)`: 创建默认映射
  - `load_mapping(mapping_file)`: 加载映射配置
  - `save_mapping(mapping_file)`: 保存映射配置
  - `apply_mapping(source_feature, mapping)`: 应用映射到要素
  - `get_target_schema(source_schema)`: 获取目标模式
  - `update_mapping(source_field, target_field, conversion, **kwargs)`: 更新映射
  - `remove_mapping(source_field)`: 删除映射
  - `get_mapping()`: 获取当前映射
  - `clear_mapping()`: 清空映射

#### 3.3.2 实现细节

字段映射模块使用JSON格式存储映射配置，并提供映射应用功能。主要实现步骤：

1. 创建或加载映射配置
2. 应用映射到要素
3. 保存映射配置

#### 3.3.3 示例代码

```python
from src.core.field_mapper import FieldMapper

# 创建字段映射器
mapper = FieldMapper()

# 创建默认映射
source_schema = {'properties': {'id': 'int', 'name': 'str', 'value': 'float'}}
target_schema = {'properties': {'id': 'int', 'name': 'str', 'amount': 'float'}}
mapping = mapper.create_mapping(source_schema, target_schema)

# 更新映射
mapper.update_mapping('value', 'amount', 'direct')

# 保存映射
mapper.save_mapping("path/to/mapping.json")

# 应用映射
source_feature = {
    'geometry': {'type': 'Point', 'coordinates': [0, 0]},
    'properties': {'id': 1, 'name': 'A', 'value': 10.5}
}
target_feature = mapper.apply_mapping(source_feature)
```

### 3.4 融合逻辑模块 (fusion.py)

融合逻辑模块实现两种融合功能的核心逻辑。

#### 3.4.1 主要类和函数

- `GDBFusion`: 融合功能的主类
  - `merge_same_schema(gdb_list, output_gdb, layer_filter)`: 融合相同结构的GDB
  - `merge_different_schema(main_gdb, secondary_gdb, output_gdb, mapping_file, layer_filter)`: 融合不同结构的GDB
  - `generate_mapping_template(main_gdb, secondary_gdb, layer_name, output_file)`: 生成字段映射模板

#### 3.4.2 实现细节

融合逻辑模块使用GDB读取模块、GDB写入模块和字段映射模块实现融合功能。主要实现步骤：

1. 读取输入GDB文件
2. 验证图层和字段结构
3. 创建输出GDB文件
4. 应用字段映射（如果需要）
5. 写入融合后的数据

#### 3.4.3 示例代码

```python
from src.core.fusion import GDBFusion

# 创建融合器
fusion = GDBFusion()

# 融合相同结构的GDB
input_gdbs = ["path/to/input1.gdb", "path/to/input2.gdb", "path/to/input3.gdb"]
output_gdb = "path/to/output.gdb"
fusion.merge_same_schema(input_gdbs, output_gdb)

# 融合不同结构的GDB
main_gdb = "path/to/main.gdb"
secondary_gdb = "path/to/secondary.gdb"
output_gdb = "path/to/output.gdb"
mapping_file = "path/to/mapping.json"
fusion.merge_different_schema(main_gdb, secondary_gdb, output_gdb, mapping_file)

# 生成字段映射模板
main_gdb = "path/to/main.gdb"
secondary_gdb = "path/to/secondary.gdb"
layer_name = "points"
output_file = "path/to/mapping.json"
fusion.generate_mapping_template(main_gdb, secondary_gdb, layer_name, output_file)
```

## 4. 工具函数模块

### 4.1 数据验证模块 (validation.py)

数据验证模块提供数据验证功能，用于验证GDB文件、模式兼容性和字段映射。

#### 4.1.1 主要函数

- `validate_gdb(gdb_path)`: 验证GDB文件是否有效
- `validate_schema_compatibility(schema1, schema2)`: 验证两个模式是否兼容
- `validate_field_mapping(mapping, source_schema, target_schema)`: 验证字段映射是否有效
- `validate_output_path(output_path)`: 验证输出路径是否有效

#### 4.1.2 实现细节

数据验证模块使用Fiona库验证GDB文件，并提供模式兼容性和字段映射验证功能。主要实现步骤：

1. 验证GDB文件是否存在和有效
2. 验证模式是否兼容
3. 验证字段映射是否有效
4. 验证输出路径是否有效

#### 4.1.3 示例代码

```python
from src.utils.validation import validate_gdb, validate_schema_compatibility

# 验证GDB文件
is_valid, error = validate_gdb("path/to/file.gdb")
if not is_valid:
    print(f"GDB文件无效: {error}")

# 验证模式兼容性
schema1 = {'properties': {'id': 'int', 'name': 'str'}}
schema2 = {'properties': {'id': 'int', 'name': 'str'}}
is_compatible, diff_fields = validate_schema_compatibility(schema1, schema2)
if not is_compatible:
    print(f"模式不兼容: {diff_fields}")
```

### 4.2 数据转换模块 (conversion.py)

数据转换模块提供数据类型转换功能，用于处理字段类型转换和空值处理。

#### 4.2.1 主要函数

- `convert_field_type(value, source_type, target_type)`: 转换字段类型
- `handle_null_values(value, field_name, default_value)`: 处理空值
- `convert_geometry_type(geometry, target_type)`: 转换几何类型
- `convert_crs(crs_from, crs_to)`: 转换坐标参考系统
- `create_field_mapping_dict(source_fields, target_fields)`: 创建字段映射字典
- `get_field_type_for_value(value)`: 根据值获取字段类型
- `convert_schema_to_fiona_schema(schema)`: 将自定义模式转换为Fiona模式

#### 4.2.2 实现细节

数据转换模块提供各种数据类型转换功能，用于处理字段类型转换和空值处理。主要实现步骤：

1. 转换字段类型
2. 处理空值
3. 转换几何类型
4. 转换坐标参考系统

#### 4.2.3 示例代码

```python
from src.utils.conversion import convert_field_type, handle_null_values

# 转换字段类型
value = "123"
converted_value = convert_field_type(value, "str", "int")
print(f"转换后的值: {converted_value}")  # 输出: 123

# 处理空值
value = None
default_value = 0
handled_value = handle_null_values(value, "id", default_value)
print(f"处理后的值: {handled_value}")  # 输出: 0
```

## 5. 用户界面模块

### 5.1 命令行界面 (cli.py)

命令行界面模块提供命令行操作接口，用于在命令行中使用GDB融合工具。

#### 5.1.1 主要类和函数

- `CLI`: 命令行界面主类
  - `_create_parser()`: 创建命令行参数解析器
  - `parse_args(args)`: 解析命令行参数
  - `run(args)`: 运行命令行工具
  - `_run_merge_same(args)`: 运行融合相同结构的GDB命令
  - `_run_merge_diff(args)`: 运行融合不同结构的GDB命令
  - `_run_gen_mapping(args)`: 运行生成字段映射模板命令
- `main()`: 命令行入口函数

#### 5.1.2 实现细节

命令行界面模块使用argparse库解析命令行参数，并调用融合逻辑模块实现功能。主要实现步骤：

1. 创建命令行参数解析器
2. 解析命令行参数
3. 根据命令执行相应操作

#### 5.1.3 示例代码

```python
from src.ui.cli import CLI

# 创建命令行界面
cli = CLI()

# 解析命令行参数
args = cli.parse_args(["merge-same", "--input", "input1.gdb", "input2.gdb", "--output", "output.gdb"])

# 运行命令行工具
exit_code = cli.run(args)
```

### 5.2 图形用户界面 (gui.py)

图形用户界面模块提供简单的图形用户界面，使用tkinter库实现。

#### 5.2.1 主要类和函数

- `RedirectText`: 重定向文本类，用于将日志重定向到Text控件
- `GUI`: 图形界面主类
  - `create_widgets()`: 创建界面控件
  - `create_same_tab()`: 创建融合相同结构GDB选项卡
  - `create_diff_tab()`: 创建融合不同结构GDB选项卡
  - `create_mapping_tab()`: 创建生成字段映射选项卡
  - `create_log_area()`: 创建日志区域
  - `run()`: 运行图形界面
- `main()`: 图形界面入口函数

#### 5.2.2 实现细节

图形用户界面模块使用tkinter库创建界面，并调用融合逻辑模块实现功能。主要实现步骤：

1. 创建主窗口
2. 创建选项卡和控件
3. 绑定事件处理函数
4. 运行主循环

#### 5.2.3 示例代码

```python
from src.ui.gui import GUI

# 创建图形用户界面
gui = GUI()

# 运行图形界面
gui.run()
```

## 6. 配置管理模块

### 6.1 配置管理器 (config_manager.py)

配置管理模块负责管理工具配置，包括加载、保存和获取配置项。

#### 6.1.1 主要类和函数

- `ConfigManager`: 配置管理主类
  - `load_config(config_file)`: 加载配置
  - `save_config(config_file)`: 保存配置
  - `get_setting(key, default)`: 获取配置项
  - `set_setting(key, value)`: 设置配置项
  - `get_all_settings()`: 获取所有配置项
  - `update_settings(settings)`: 更新多个配置项
  - `clear_settings()`: 清空所有配置项
  - `remove_setting(key)`: 删除配置项
  - `get_config_file()`: 获取当前配置文件路径

#### 6.1.2 实现细节

配置管理模块使用JSON格式存储配置，并提供配置项管理功能。主要实现步骤：

1. 加载配置文件
2. 获取和设置配置项
3. 保存配置文件

#### 6.1.3 示例代码

```python
from src.config.config_manager import ConfigManager

# 创建配置管理器
config_manager = ConfigManager()

# 加载配置
config_manager.load_config("path/to/config.json")

# 获取配置项
value = config_manager.get_setting("key", "default_value")

# 设置配置项
config_manager.set_setting("key", "value")

# 保存配置
config_manager.save_config()
```

## 7. 数据流

### 7.1 融合字段结构一致的多个GDB

1. 用户通过UI选择多个GDB文件和输出路径
2. 系统验证所有GDB文件的有效性
3. 系统检查所有GDB的字段结构是否一致
4. 系统创建新的输出GDB
5. 系统逐个读取输入GDB的图层和要素
6. 系统将所有要素写入输出GDB
7. 系统完成融合并返回结果

### 7.2 融合字段结构不同的GDB

1. 用户通过UI选择主GDB、次要GDB和输出路径
2. 用户配置字段映射关系
3. 系统验证GDB文件的有效性
4. 系统创建新的输出GDB，结构基于主GDB
5. 系统读取主GDB的图层和要素，写入输出GDB
6. 系统读取次要GDB的图层和要素
7. 系统根据字段映射关系转换次要GDB的要素
8. 系统将转换后的要素写入输出GDB
9. 系统完成融合并返回结果

## 8. 扩展指南

### 8.1 添加新的转换类型

要添加新的转换类型，需要修改以下文件：

1. `src/core/field_mapper.py`：添加新的转换类型处理逻辑
2. `src/utils/conversion.py`：添加新的转换函数
3. `src/utils/validation.py`：添加新的验证逻辑

示例：添加一个新的转换类型`format_string`，用于格式化字符串

```python
# 在field_mapper.py中添加处理逻辑
elif conversion == 'format_string':
    # 格式化字符串
    format_string = map_info.get('format_string', '{0}')
    try:
        target_properties[target_field] = format_string.format(source_value)
    except Exception as e:
        logger.error(f"格式化字符串出错: {str(e)}")
        target_properties[target_field] = default_value

# 在conversion.py中添加转换函数
def format_string(value, format_string):
    """
    格式化字符串
    
    Args:
        value: 字段值
        format_string: 格式化字符串
        
    Returns:
        str: 格式化后的字符串
    """
    try:
        return format_string.format(value)
    except Exception as e:
        logger.error(f"格式化字符串出错: {str(e)}")
        return value

# 在validation.py中添加验证逻辑
elif conversion == 'format_string':
    # 格式化字符串，检查是否指定了格式化字符串
    if 'format_string' not in map_info:
        errors.append(f"未指定格式化字符串: {source_field} -> {target_field}")
```

### 8.2 添加新的命令

要添加新的命令，需要修改以下文件：

1. `src/ui/cli.py`：添加新的命令和参数
2. `src/core/fusion.py`：添加新的功能实现

示例：添加一个新的命令`validate`，用于验证GDB文件

```python
# 在cli.py中添加新的命令
# 验证GDB文件
validate = subparsers.add_parser('validate', help='验证GDB文件')
validate.add_argument('--input', '-i', required=True, help='输入GDB文件路径')
validate.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')

# 添加新的命令处理函数
def _run_validate(self, args):
    """
    运行验证GDB文件命令
    
    Args:
        args: 解析后的参数
        
    Returns:
        int: 退出码，0表示成功，非0表示失败
    """
    # 验证输入GDB
    is_valid, error = validate_gdb(args.input)
    if not is_valid:
        logger.error(f"输入GDB无效: {args.input} - {error}")
        return 1
    
    # 读取GDB文件
    reader = GDBReader()
    if not reader.read_gdb(args.input):
        logger.error(f"无法读取GDB文件: {args.input}")
        return 1
    
    # 获取图层列表
    layers = reader.get_layers()
    logger.info(f"GDB文件包含 {len(layers)} 个图层: {', '.join(layers)}")
    
    # 验证每个图层
    for layer_name in layers:
        feature_count = reader.get_layer_feature_count(layer_name)
        logger.info(f"图层 {layer_name} 包含 {feature_count} 个要素")
    
    logger.info(f"GDB文件验证成功: {args.input}")
    return 0

# 在run方法中添加新的命令处理
elif args.command == 'validate':
    return self._run_validate(args)

# 在fusion.py中添加新的功能实现
def validate_gdb_file(self, gdb_path):
    """
    验证GDB文件
    
    Args:
        gdb_path: GDB文件路径
        
    Returns:
        tuple: (是否有效, 图层列表, 图层信息)
    """
    try:
        # 读取GDB文件
        if not self.reader.read_gdb(gdb_path):
            return False, [], {}
        
        # 获取图层列表
        layers = self.reader.get_layers()
        
        # 获取图层信息
        layer_info = {}
        for layer_name in layers:
            feature_count = self.reader.get_layer_feature_count(layer_name)
            schema = self.reader.get_layer_schema(layer_name)
            crs = self.reader.get_layer_crs(layer_name)
            
            layer_info[layer_name] = {
                'feature_count': feature_count,
                'schema': schema,
                'crs': crs
            }
        
        return True, layers, layer_info
    except Exception as e:
        logger.error(f"验证GDB文件时出错: {str(e)}")
        return False, [], {}
```

### 8.3 添加新的用户界面

要添加新的用户界面，需要创建新的UI模块，并修改`src/__main__.py`文件。

示例：添加一个基于PyQt的用户界面

1. 创建新的UI模块`src/ui/qt_gui.py`
2. 在`src/__main__.py`中添加新的UI选项

```python
# 在__main__.py中添加新的UI选项
parser.add_argument('--qt-gui', action='store_true', help='启动PyQt图形用户界面')

# 根据参数启动相应界面
if args.qt_gui:
    # 启动PyQt图形用户界面
    logger.info("启动PyQt图形用户界面")
    from .ui.qt_gui import QtGUI
    qt_gui = QtGUI()
    qt_gui.run()
elif args.gui:
    # 启动Tkinter图形用户界面
    logger.info("启动Tkinter图形用户界面")
    gui = GUI()
    gui.run()
else:
    # 启动命令行界面
    logger.info("启动命令行界面")
    cli = CLI()
    sys.exit(cli.run(remaining_args))
```

## 9. 测试

### 9.1 测试框架

GDB融合工具使用Python的unittest框架进行测试。测试文件位于`tests`目录下。

### 9.2 测试数据

测试数据由`tests/generate_test_data.py`脚本生成，包括：

1. 字段结构一致的多个GDB文件
2. 字段结构不同的GDB文件
3. 字段映射配置文件

### 9.3 运行测试

运行所有测试：

```bash
python -m unittest discover tests
```

运行特定测试：

```bash
python -m unittest tests.test_fusion
```

### 9.4 添加新的测试

要添加新的测试，需要创建新的测试文件，并继承`unittest.TestCase`类。

示例：添加一个新的测试文件`tests/test_validation.py`

```python
import os
import sys
import unittest
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.validation import validate_gdb, validate_schema_compatibility

class TestValidation(unittest.TestCase):
    """验证功能测试类"""
    
    def test_validate_gdb(self):
        """测试验证GDB文件"""
        # 测试有效的GDB文件
        is_valid, error = validate_gdb("tests/data/same_schema_1.gdb")
        self.assertTrue(is_valid, f"有效的GDB文件应该通过验证: {error}")
        
        # 测试不存在的GDB文件
        is_valid, error = validate_gdb("tests/data/not_exist.gdb")
        self.assertFalse(is_valid, "不存在的GDB文件应该验证失败")
    
    def test_validate_schema_compatibility(self):
        """测试验证模式兼容性"""
        # 测试兼容的模式
        schema1 = {'properties': {'id': 'int', 'name': 'str'}}
        schema2 = {'properties': {'id': 'int', 'name': 'str'}}
        is_compatible, diff_fields = validate_schema_compatibility(schema1, schema2)
        self.assertTrue(is_compatible, "兼容的模式应该验证通过")
        
        # 测试不兼容的模式
        schema1 = {'properties': {'id': 'int', 'name': 'str'}}
        schema2 = {'properties': {'id': 'int', 'title': 'str'}}
        is_compatible, diff_fields = validate_schema_compatibility(schema1, schema2)
        self.assertFalse(is_compatible, "不兼容的模式应该验证失败")

if __name__ == '__main__':
    unittest.main()
```

## 10. 构建与部署

### 10.1 构建包

使用setuptools构建包：

```bash
python setup.py sdist bdist_wheel
```

### 10.2 安装包

安装开发版本：

```bash
pip install -e .
```

安装发布版本：

```bash
pip install dist/gdb_fusion_tool-0.1.0-py3-none-any.whl
```

### 10.3 发布到PyPI

1. 安装twine：

```bash
pip install twine
```

2. 上传到PyPI：

```bash
twine upload dist/*
```

## 11. 参考资料

- [Python官方文档](https://docs.python.org/)
- [Fiona文档](https://fiona.readthedocs.io/)
- [GeoPandas文档](https://geopandas.org/)
- [Shapely文档](https://shapely.readthedocs.io/)
- [ESRI GDB格式规范](https://desktop.arcgis.com/en/arcmap/latest/manage-data/geodatabases/types-of-geodatabases.htm)

