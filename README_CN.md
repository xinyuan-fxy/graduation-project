# 智能传感器吉他环境保护监测系统

**作者：** 冯心源（Xinyuan Feng）  
**学位：** 机器人工程学士（BEng Robotics）— 赫瑞瓦特大学  
**指导教师：** Dr. Theodoros Georgiou

---

## 项目简介

实木吉他对温度、湿度和光照的变化极为敏感，环境不当极易造成开裂、变形等不可逆损伤。本项目使用 **BBC Micro:bit V2** 与 **Kitronik 空气质量板**搭建低成本离线环境监测系统，在室内六个不同位置持续采集温度、湿度与光照数据，并通过统计分析确定最适合存放吉他的位置。

**厂商推荐的安全存放范围：**
- 湿度：**40 – 60% RH**
- 温度：**低于 30 °C**
- 光照：避免阳光直射

---

## 目录结构

```
graduation-project/
│
├── code/
│   ├── microbit-main.hex       # 烧录到 Micro:bit 的固件程序
│   └── generate_charts.py      # 数据可视化与统计分析 Python 脚本
│
├── data5/                      # 每 5 秒采样一次的传感器数据（约 9.8 小时）
│   ├── Hallway End/
│   ├── Hallway Middle/
│   ├── bedroom  far away from door/
│   ├── bedroom middle/
│   ├── kitchen  far away from door/
│   └── kitchen middle/
│
├── data30/                     # 每 30 秒采样一次的传感器数据（约 24 小时）
│   ├── Hallway End/
│   ├── Hallway Middle/
│   ├── bedroom far/
│   ├── bedroom middle/
│   ├── kitchen  far away from door/
│   └── kitchen middle/
│
├── image/                      # 参考图片与论文插图
├── image5/                     # 由 data5 生成的图表（输出目录）
├── image30/                    # 由 data30 生成的图表（输出目录）
├── comparison_chart.png        # 跨阶段对比图（输出文件）
└── Xinyuan Feng Final Dissertation Document .docx
```

每个位置子文件夹内包含一份 CSV 文件，列格式如下：

| 列名 | 说明 |
|------|------|
| `Time (seconds)` | 自开始记录后的累计时间（秒） |
| `Temp` | 温度（°C） |
| `Humid` | 相对湿度（%） |
| `Light` | 光照强度（0 – 255，由 Micro:bit LED 矩阵反向读取） |

---

## 第一部分 — 硬件：烧录 Micro:bit

### 所需设备

| 设备 | 说明 |
|------|------|
| BBC Micro:bit V2 | 主控制器 |
| Kitronik 空气质量板 | 提供温湿度传感器，Micro:bit 插入其上方插槽 |
| USB-A 转 Micro-USB 数据线 | 用于烧录固件和提取数据 |
| 小型移动电源（可选） | 野外部署时为设备供电 |

### 烧录步骤

1. 用 USB 线将 Micro:bit 连接到电脑。
2. 电脑上会出现一个名为 **MICROBIT** 的可移动磁盘。
3. 将 `code/microbit-main.hex` 文件复制到该磁盘中。
4. Micro:bit 会自动重启，固件烧录完成，设备开始运行。
5. LED 矩阵显示**笑脸**表示当前环境在安全范围内；显示**哭脸**表示湿度超出 40–60% 或温度超过 30 °C。

### 数据采集说明

固件每隔一个采样间隔将一条读数写入 Micro:bit 内部闪存。

| 数据集 | 采样间隔 | 典型采集时长 | 约采集数据点 |
|--------|---------|------------|-------------|
| `data5`  | 每 **5 秒** 一次 | 约 9.8 小时 | 每个位置约 5 800 条 |
| `data30` | 每 **30 秒** 一次 | 约 24 小时 | 每个位置约 2 800 条 |

> **注意：** 本项目只有一块 Micro:bit，因此六个位置按顺序在不同日期分别采集。

### 提取数据

1. 采集完成后，将 Micro:bit 通过 USB 重新连接到电脑。
2. 在 MICROBIT 磁盘中找到 **MY_DATA.HTM** 文件，用浏览器打开。
3. 点击页面中的下载按钮，将数据导出为 CSV 文件。
4. 将 CSV 文件放入对应的 `data5/` 或 `data30/` 子目录中，并按位置名称命名（例如 `bedroom far/bedroom far.csv`）。

---

## 第二部分 — 软件：生成图表与统计分析

### 环境要求

- Python 3.8 及以上版本
- 所需第三方库：

```bash
pip install pandas matplotlib numpy scipy
```

### 运行脚本

```bash
cd graduation-project
python code/generate_charts.py
```

脚本会自动扫描 `data5/` 和 `data30/` 下的所有 CSV 文件，生成全部图表和统计结果，并保存到对应输出目录。

### 输出文件说明

#### 每个数据集各自生成（分别保存在 `image5/` 和 `image30/`）

| 文件 | 说明 |
|------|------|
| `linechart.png` | 折线图：六个位置叠加显示（3 个子图：温度、湿度、光照随时间变化）。温度子图含 30 °C 红色警戒线，湿度子图含 40–60% 绿色安全区。 |
| `barchart.png` | 柱状图：六个位置的均值 ± 标准差。最优位置（卧室远端）加粗边框并标注"Optimal Location"箭头。 |
| `stats_results.csv` | 统计检验结果（机器可读 CSV 格式）。 |
| `stats_table.png` | 统计结果渲染为图片，可直接插入报告。显著结果（p < 0.05）以橙色高亮。 |

#### 项目根目录生成

| 文件 | 说明 |
|------|------|
| `comparison_chart.png` | 跨阶段对比图：每个位置并排显示第一阶段（5 秒采样）与第二阶段（30 秒采样）的均值和误差棒。 |

### 统计分析内容

| 检验方法 | 用途 |
|---------|------|
| **单因素方差分析（One-Way ANOVA）** | 检验六个位置之间温度、湿度、光照是否存在显著差异。 |
| **Levene 检验** | 检验各位置温度和湿度的方差（波动性）是否存在显著差异。 |
| **Welch t 检验** | 将"卧室远端"与其他每个位置逐一进行两样本比较（温度和湿度）。 |
| **Cohen's d 效应量** | 衡量"卧室远端"优势在实际意义上有多显著，不依赖样本量。 |

---

## 主要结论

- **卧室远端（Bedroom Far from Door）** 在两个采集阶段中均被确认为最稳定、最安全的存放位置：
  - 湿度波动最小（第一阶段标准差约 0.9%，第二阶段约 1.6%）
  - 温度稳定（约 22–23 °C）
  - 光照强度始终为零
- **厨房**环境波动最大，不适合存放吉他。
- **走廊**位置过于干燥（平均湿度最低仅 18%），存在严重开裂风险。
- 所有测试位置的湿度均**低于** 40% 的安全下限 — 仅靠被动监测不够，还需搭配加湿器主动调节。

---

## 完整复现步骤

1. 将 `code/microbit-main.hex` 烧录到 Micro:bit。
2. 将 Micro:bit（插上 Kitronik 空气质量板）放置于目标位置。
3. 保持运行指定时长（5 秒采样约需 10 小时，30 秒采样约需 24 小时）。
4. 通过 USB 提取 CSV 数据文件，放入对应子目录。
5. 执行 `python code/generate_charts.py`，重新生成所有图表和统计结果。
