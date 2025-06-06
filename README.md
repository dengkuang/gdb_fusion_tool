# GDB融合工具

基于Python ArcGIS的GDB融合工具，用于合并多个GDB文件的数据。

## 功能特点

1. **融合字段结构一致的多个GDB**
   - 将多个字段结构一致的GDB文件合并为一个GDB文件
   - 支持选择要融合的图层
   - 自动处理坐标系差异

2. **融合字段结构不同的GDB**
   - 以一个GDB为主结构，将另一个GDB的属性融合到主GDB中
   - 支持字段映射配置
   - 自动创建新字段
   - 处理数据类型转换

## 系统要求

- Python 3.6+
- 依赖库：
  - fiona
  - geopandas
  - shapely
  - tqdm

## 安装方法

### 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/dengkuang/gdb_fusion_tool.git
cd gdb_fusion_tool

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

### 使用pip安装

```bash
pip install gdb-fusion-tool
```

## 使用方法

### 命令行界面

#### 融合字段结构一致的多个GDB

```bash
gdb-fusion merge-same --input input1.gdb input2.gdb input3.gdb --output output.gdb
```

可选参数：
- `--layers`：要处理的图层列表
- `--verbose`：显示详细日志

#### 融合字段结构不同的GDB

```bash
gdb-fusion merge-diff --main main.gdb --secondary secondary.gdb --output output.gdb
```

可选参数：
- `--mapping`：字段映射配置文件路径
- `--layers`：要处理的图层列表
- `--verbose`：显示详细日志

#### 生成字段映射模板

```bash
gdb-fusion gen-mapping --main main.gdb --secondary secondary.gdb --layer layer_name --output mapping.json
```

可选参数：
- `--verbose`：显示详细日志

### 图形用户界面

启动图形用户界面：

```bash
gdb-fusion --gui
```

## 字段映射配置

字段映射配置是一个JSON文件，用于定义字段之间的映射关系。示例：

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

转换类型：
- `direct`：直接映射，不进行类型转换
- `type_convert`：类型转换，将源字段值转换为目标字段类型
- `new_field`：创建新字段，如果目标GDB中不存在该字段

## 许可证

MIT License

