# Robot Data Monitor in RHOS Lab

## 概述
`monitor_data.py` 是用于监控机器人实验数据目录下 `.hdf5` 文件数量和帧数的脚本。  
脚本可以统计每个子任务目录的：

- Episode 数量（`.hdf5` 文件数）
- 总帧数（所有 episode 的帧数累加）
- 总时长（根据帧数和机器人 FPS 换算为小时）

并生成对应的柱状图，显示本周新增量。图表存储在 `data_stats_log/img_count` 下。

---

## 功能

1. **统计每个子目录的 episode 数量和总帧数**
2. **计算新增 episode 数量和新增帧数**
3. **生成柱状图**
   - Episode 数量柱状图
   - 总小时数柱状图（根据帧数 / FPS / 3600）
   - 柱子顶部显示具体数量或小时数
   - 本周新增量以绿色显示
   - y 轴自动比最高柱子高 10%
   - 柱宽随任务数量动态调整
4. **日志记录**
   - 记录每次扫描结果
   - 日志文件：`data_stats_log/data_monitor.log`
5. **配置存储**
   - 上一次扫描的 episode 数量和帧数保存于 `data_stats_log/data_monitor_config.json`
6. **支持定时模式**
   - 可每周四 18:00 自动扫描并生成图表
   - 使用 `schedule` 库进行定时任务

---

## 依赖

- Python 3.8+
- `matplotlib`
- `h5py`
- `schedule`

安装依赖示例：

```bash
pip install matplotlib h5py schedule
