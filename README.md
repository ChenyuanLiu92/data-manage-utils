
# 机器人数据管理系统

这是一个用于管理机器人数据（`.hdf5` 文件）的 项目。
目前实现了数据统计功能，可以扫描指定目录下的文件数量和总帧数，计算每周的增量，并将结果记录到日志文件和可视化的柱状图中。

## 功能特点

- **多维度统计**: 统计每个任务（子目录）下的 `episode` 数量（`.hdf5` 文件数）和总 `frame` 数量。
- **增量计算**: 自动计算每周新增的 `episode` 和 `frame` 数量。
- **日志记录**: 将每次统计结果追加记录到 **`data_stats_log/data_monitor.log`** 文件中。
- **数据可视化**: 生成并保存两个柱状图：
  - **`episode` 柱状图**: 展示每个任务的总 `episode` 数量。
  - **`hours` 柱状图**: 将总帧数转换为小时，展示每个任务的总数据时长。
- **灵活运行**: 支持命令行参数，可以立即运行一次扫描，也可以设置为每周定时自动运行。
- **配置管理**: 使用 **`data_stats_log/data_monitor_config.json`** 文件来保存上次的统计数据，以实现增量计算。

---

## 安装与准备

**安装依赖**: 您需要安装以下 Python 库。在终端中运行：
   
   ```
   conda create -n data_monitor python=3.12 -y

   conda activate data_monitor

   conda install -c conda-forge matplotlib h5py schedule -y
   ```
## 目录结构:
请确保您的数据目录结构如下所示，或者根据需要修改脚本中的 --base-dir 和 --sub-dirs 参数。
```
├── data_dir/
│   ├── OCL4Rob/              # <-- 根目录 (--base-dir)
│   │   ├── pp_two_cube/      # <-- 子目录 (--sub-dirs)
│   │   │   └── data_001.hdf5
│   │   └── pour/             # <-- 子目录 (--sub-dirs)
│   │       └── data_002.hdf5
├── data_stats_log/           # <-- 脚本自动创建
│   ├── data_monitor.log
│   ├── data_monitor_config.json
│   └── img_count/
│       ├── episode_chart_20250822.png
│       └── hour_chart_20250822.png
└── data_count/
    └── monitor_robot_data.py  # <-- 主脚本
    └── monitor_data.sh  # <-- 可选的 Systemd 启动脚本

```
## 如何使用

```data_count``` 脚本提供了两种主要的运行模式：立即运行和定时模式。

### 模式一：立即运行一次扫描
使用 --run-now 参数可以立即执行一次完整的数据扫描和统计。这对于首次运行或手动检查非常有用。

```
python monitor_robot_data.py --run-now
```
可选参数：

--base-dir \<path\> : 指定数据根目录。默认为 OCL4Rob。

--sub-dirs \<dir1\> \<dir2\> ... : 指定需要监控的子目录。默认为 pp_two_cube 和 pour。


### 模式二：进入定时模式
使用 --watch 参数，脚本将进入一个循环，并根据 schedule 库的设置在每周四晚上 18:00 自动执行扫描。


## 结果输出
脚本执行后，您将在 data_stats_log/ 目录中找到以下文件：

data_stats_log/data_monitor.log: 日志文件，记录每次统计的文本信息。

data_stats_log/data_monitor_config.json: 配置文件，保存上次的统计数据。

data_stats_log/img_count/: 包含生成的柱状图图片。

每次运行，脚本都会生成最新的柱状图，清晰展示数据增长情况。

## 备注

可以每周按时人工执行脚本统计，也可以设置为Systemd开机自动启动(参考 `monitor_data.sh` 脚本)。
