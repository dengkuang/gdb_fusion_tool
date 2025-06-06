# GDB融合工具用户手册

**版本：** 0.1.0  
**作者：** Manus AI  
**日期：** 2025-06-06

## 目录

1. [简介](#1-简介)
2. [安装](#2-安装)
3. [基本概念](#3-基本概念)
4. [命令行界面](#4-命令行界面)
5. [图形用户界面](#5-图形用户界面)
6. [字段映射配置](#6-字段映射配置)
7. [最佳实践](#7-最佳实践)
8. [常见问题](#8-常见问题)
9. [故障排除](#9-故障排除)
10. [参考资料](#10-参考资料)

## 1. 简介

GDB融合工具是一个基于Python的地理数据库(GDB)融合工具，专为GIS专业人员和开发人员设计，用于合并和整合多个GDB文件的数据。该工具提供两种主要功能：

1. **融合字段结构一致的多个GDB**：将多个具有相同字段结构的GDB文件合并为一个GDB文件。
2. **融合字段结构不同的GDB**：将两个字段结构不同的GDB文件融合，通过字段映射关系将一个GDB的属性融合到另一个GDB中。

本工具支持命令行界面和图形用户界面，适用于各种工作流程和自动化需求。

### 1.1 主要特点

- 支持融合多个字段结构一致的GDB文件
- 支持融合字段结构不同的GDB文件，通过字段映射关系进行属性融合
- 自动处理坐标系差异
- 支持选择要融合的图层
- 支持字段映射配置
- 自动创建新字段
- 处理数据类型转换
- 提供命令行界面和图形用户界面
- 详细的日志记录和错误处理

### 1.2 系统要求

- Python 3.6+
- 依赖库：
  - fiona
  - geopandas
  - shapely
  - tqdm
  - pandas
  - numpy

## 2. 安装

### 2.1 从源代码安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/gdb_fusion_tool.git
cd gdb_fusion_tool
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 安装工具：

```bash
pip install -e .
```

### 2.2 使用pip安装

```bash
pip install gdb-fusion-tool
```

### 2.3 验证安装

安装完成后，可以通过以下命令验证安装是否成功：

```bash
gdb-fusion --help
```

如果安装成功，将显示命令行帮助信息。

## 3. 基本概念

在使用GDB融合工具之前，了解一些基本概念将有助于更好地理解和使用该工具。

### 3.1 GDB文件

GDB（地理数据库）是ESRI开发的一种地理空间数据存储格式，用于存储、查询和管理地理空间数据。GDB文件可以包含多个图层，每个图层包含几何对象和属性数据。

### 3.2 图层

图层是GDB文件中的基本组织单元，用于存储特定类型的地理要素（如点、线、面）及其属性。每个图层具有特定的几何类型和属性字段结构。

### 3.3 字段结构

字段结构定义了图层中的属性字段，包括字段名称、数据类型和其他属性。字段结构一致意味着两个图层具有相同的字段名称和数据类型。

### 3.4 字段映射

字段映射定义了如何将一个图层的字段映射到另一个图层的字段。字段映射包括源字段、目标字段、转换类型和默认值等信息。

## 4. 命令行界面

GDB融合工具提供了命令行界面，方便在脚本中使用或进行批处理操作。

### 4.1 基本用法

```bash
gdb-fusion <command> [options]
```

### 4.2 可用命令

- `merge-same`：融合字段结构一致的多个GDB
- `merge-diff`：融合字段结构不同的GDB
- `gen-mapping`：生成字段映射模板

### 4.3 融合字段结构一致的多个GDB

```bash
gdb-fusion merge-same --input input1.gdb input2.gdb input3.gdb --output output.gdb [--layers layer1 layer2] [--verbose]
```

参数说明：
- `--input`, `-i`：输入GDB文件路径列表（必需）
- `--output`, `-o`：输出GDB文件路径（必需）
- `--layers`, `-l`：要处理的图层列表（可选）
- `--verbose`, `-v`：显示详细日志（可选）

示例：

```bash
gdb-fusion merge-same --input data/city1.gdb data/city2.gdb data/city3.gdb --output data/merged_cities.gdb --layers buildings roads
```

### 4.4 融合字段结构不同的GDB

```bash
gdb-fusion merge-diff --main main.gdb --secondary secondary.gdb --output output.gdb [--mapping mapping.json] [--layers layer1 layer2] [--verbose]
```

参数说明：
- `--main`, `-m`：主GDB文件路径（必需）
- `--secondary`, `-s`：次要GDB文件路径（必需）
- `--output`, `-o`：输出GDB文件路径（必需）
- `--mapping`, `-p`：字段映射配置文件路径（可选）
- `--layers`, `-l`：要处理的图层列表（可选）
- `--verbose`, `-v`：显示详细日志（可选）

示例：

```bash
gdb-fusion merge-diff --main data/main_city.gdb --secondary data/secondary_city.gdb --output data/merged_city.gdb --mapping data/field_mapping.json
```

### 4.5 生成字段映射模板

```bash
gdb-fusion gen-mapping --main main.gdb --secondary secondary.gdb --layer layer_name --output mapping.json [--verbose]
```

参数说明：
- `--main`, `-m`：主GDB文件路径（必需）
- `--secondary`, `-s`：次要GDB文件路径（必需）
- `--layer`, `-l`：图层名称（必需）
- `--output`, `-o`：输出映射文件路径（必需）
- `--verbose`, `-v`：显示详细日志（可选）

示例：

```bash
gdb-fusion gen-mapping --main data/main_city.gdb --secondary data/secondary_city.gdb --layer buildings --output data/buildings_mapping.json
```

## 5. 图形用户界面

GDB融合工具还提供了图形用户界面，方便不熟悉命令行的用户使用。

### 5.1 启动图形用户界面

```bash
gdb-fusion --gui
```

### 5.2 界面概述

图形用户界面包含三个选项卡：
1. **融合相同结构GDB**：用于融合字段结构一致的多个GDB
2. **融合不同结构GDB**：用于融合字段结构不同的GDB
3. **生成字段映射**：用于生成字段映射模板

每个选项卡底部都有一个日志区域，显示操作过程中的日志信息。

### 5.3 融合相同结构GDB

1. 在"融合相同结构GDB"选项卡中：
   - 点击"浏览..."按钮选择输入GDB文件
   - 点击"浏览..."按钮选择输出GDB文件
   - 点击"选择..."按钮选择要处理的图层
   - 点击"执行融合"按钮开始融合

### 5.4 融合不同结构GDB

1. 在"融合不同结构GDB"选项卡中：
   - 点击"浏览..."按钮选择主GDB文件
   - 点击"浏览..."按钮选择次要GDB文件
   - 点击"浏览..."按钮选择输出GDB文件
   - 点击"浏览..."按钮选择映射文件（可选）
   - 点击"选择..."按钮选择要处理的图层
   - 点击"执行融合"按钮开始融合

### 5.5 生成字段映射

1. 在"生成字段映射"选项卡中：
   - 点击"浏览..."按钮选择主GDB文件
   - 点击"浏览..."按钮选择次要GDB文件
   - 点击"刷新"按钮加载图层列表
   - 从下拉菜单中选择图层
   - 点击"浏览..."按钮选择输出映射文件
   - 点击"生成映射"按钮生成映射模板

## 6. 字段映射配置

字段映射配置是一个JSON文件，用于定义如何将一个GDB的字段映射到另一个GDB的字段。

### 6.1 映射文件格式

映射文件是一个JSON对象，其中键是源字段名称，值是映射信息对象。映射信息对象包含以下属性：

- `target_field`：目标字段名称
- `conversion`：转换类型
- `default_value`：默认值（当源值为空时使用）
- 其他属性（根据转换类型而定）

示例：

```json
{
    "source_field1": {
        "target_field": "target_field1",
        "conversion": "direct",
        "default_value": null
    },
    "source_field2": {
        "target_field": "target_field2",
        "conversion": "type_convert",
        "source_type": "str",
        "target_type": "int",
        "default_value": 0
    },
    "source_field3": {
        "target_field": "new_field",
        "conversion": "new_field",
        "field_type": "float",
        "default_value": 0.0
    }
}
```

### 6.2 转换类型

GDB融合工具支持以下转换类型：

1. **direct**：直接映射，不进行类型转换
   - 属性：
     - `target_field`：目标字段名称
     - `default_value`：默认值

2. **type_convert**：类型转换，将源字段值转换为目标字段类型
   - 属性：
     - `target_field`：目标字段名称
     - `source_type`：源字段类型
     - `target_type`：目标字段类型
     - `default_value`：默认值

3. **new_field**：创建新字段，如果目标GDB中不存在该字段
   - 属性：
     - `target_field`：目标字段名称
     - `field_type`：字段类型
     - `default_value`：默认值

4. **custom**：自定义转换，使用自定义函数进行转换
   - 属性：
     - `target_field`：目标字段名称
     - `custom_function`：自定义转换函数
     - `default_value`：默认值

### 6.3 生成映射模板

可以使用`gen-mapping`命令或图形用户界面中的"生成字段映射"功能生成映射模板。生成的模板可以根据需要进行修改。

## 7. 最佳实践

### 7.1 数据准备

- 在融合前检查GDB文件的有效性
- 确保输入GDB文件的坐标系统正确
- 备份重要数据

### 7.2 字段映射

- 为每个图层创建单独的映射文件
- 仔细检查字段类型是否兼容
- 为可能为空的字段设置合适的默认值

### 7.3 性能优化

- 对于大型GDB文件，考虑按图层分批处理
- 使用`--layers`参数只处理需要的图层
- 关闭不必要的日志输出

## 8. 常见问题

### 8.1 如何处理坐标系不同的GDB文件？

GDB融合工具会自动检测坐标系差异，并在必要时进行转换。默认情况下，次要GDB的坐标系会被转换为主GDB的坐标系。

### 8.2 如何处理字段名称冲突？

在字段映射配置中，可以将源字段映射到不同名称的目标字段，避免名称冲突。

### 8.3 如何处理大型GDB文件？

对于大型GDB文件，建议：
- 按图层分批处理
- 使用命令行界面而不是图形用户界面
- 增加系统内存

## 9. 故障排除

### 9.1 常见错误

1. **GDB文件无效**
   - 检查GDB文件路径是否正确
   - 确保GDB文件未损坏
   - 尝试使用ArcGIS或其他GIS软件打开GDB文件

2. **字段映射错误**
   - 检查映射文件格式是否正确
   - 确保源字段和目标字段存在
   - 检查字段类型是否兼容

3. **内存不足**
   - 减少同时处理的数据量
   - 按图层分批处理
   - 增加系统内存

### 9.2 日志分析

GDB融合工具会生成详细的日志，可以通过以下方式查看：
- 命令行界面中使用`--verbose`参数
- 图形用户界面中的日志区域
- 日志文件（如果配置了日志文件输出）

## 10. 参考资料

- [ESRI GDB格式规范](https://desktop.arcgis.com/en/arcmap/latest/manage-data/geodatabases/types-of-geodatabases.htm)
- [Fiona文档](https://fiona.readthedocs.io/)
- [GeoPandas文档](https://geopandas.org/)
- [Shapely文档](https://shapely.readthedocs.io/)

