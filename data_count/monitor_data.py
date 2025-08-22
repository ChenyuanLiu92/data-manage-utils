import os
import json
import schedule
import time
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import h5py

# 配置文件和日志文件
CONFIG_FILE = 'data_stats_log/data_monitor_config.json'
LOG_FILE = 'data_stats_log/data_monitor.log'
FPS = 25  # 机器人 FPS

# 确保目录存在
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)


def _get_file_counts_and_frames(base_dir, sub_dirs):
    """
    统计每个子目录：
    - episode 数量（.hdf5 文件数）
    - 总 frame 数量（累加每个 episode 的帧数）
    """
    counts = {}
    frames_counts = {}
    for sub_dir in sub_dirs:
        full_path = os.path.join(base_dir, sub_dir)
        episode_count = 0
        total_frames = 0
        if os.path.isdir(full_path):
            for root, dirs, files in os.walk(full_path):
                for f in files:
                    if f.endswith('.hdf5'):
                        episode_count += 1
                        hdf5_path = os.path.join(root, f)
                        try:
                            with h5py.File(hdf5_path, 'r') as hf:
                                # 找到第一个 dataset，取第 0 维长度作为帧数
                                def find_any_dataset(hf_obj):
                                    for key, item in hf_obj.items():
                                        if isinstance(item, h5py.Dataset):
                                            return item
                                        elif isinstance(item, h5py.Group):
                                            ds = find_any_dataset(item)
                                            if ds is not None:
                                                return ds
                                    return None

                                ds = find_any_dataset(hf)
                                if ds is not None:
                                    total_frames += ds.shape[0]
                        except Exception as e:
                            print(f"[WARN] 读取文件 {hdf5_path} 失败: {e}")

            counts[sub_dir] = episode_count
            frames_counts[sub_dir] = total_frames
        else:
            print(f"警告：目录 {full_path} 不存在，已跳过。")
            counts[sub_dir] = 0
            frames_counts[sub_dir] = 0
    return counts, frames_counts


def _load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'last_counts': {}, 'last_frames': {}}


def _save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def _write_log(message):
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')


def plot_bar_chart(current_counts: dict, last_counts: dict):
    dirs = list(current_counts.keys())
    n = len(dirs)
    width = min(0.8 / n, 0.1)  # 动态宽度，最大 0.1

    current_values = [current_counts[d] for d in dirs]
    last_values = [last_counts.get(d, 0) for d in dirs]

    increases = [max(c - l, 0) for c, l in zip(current_values, last_values)]
    base_values = [c - inc for c, inc in zip(current_values, increases)]

    plt.figure(figsize=(max(8, n*0.8), 5))  # 图宽随任务数量增加
    bars_base = plt.bar(dirs, base_values, color='skyblue', width=width, label='original data')
    bars_incr = plt.bar(dirs, increases, bottom=base_values, color='green', width=width, label='this week')

    max_height = max([base + inc for base, inc in zip(base_values, increases)])
    plt.ylim(0, max_height * 1.1)

    # 柱子上显示数量
    for b, i, base, inc in zip(bars_base, bars_incr, base_values, increases):
        plt.text(b.get_x() + b.get_width()/2, base + inc + 0.5, str(int(base + inc)),
                 ha='center', va='bottom', fontsize=10)

    plt.xlabel("Task")
    plt.ylabel("Number of Episodes")
    plt.title("Episode Counts by Task Name")
    plt.legend()
    plt.tight_layout()

    date_str = datetime.now().strftime("%Y%m%d")
    img_dir = os.path.join('data_stats_log', 'img_count')
    os.makedirs(img_dir, exist_ok=True)
    output_path = os.path.join(img_dir, f"episode_chart_{date_str}.png")
    plt.savefig(output_path)
    plt.close()
    print(f"[INFO] Episode 柱状图已保存到 {output_path}")


def plot_hours_bar_chart(current_frames: dict, last_frames: dict):
    dirs = list(current_frames.keys())
    n = len(dirs)
    width = min(0.8 / n, 0.1)

    current_hours = [current_frames[d] / (FPS * 3600) for d in dirs]
    last_hours = [last_frames.get(d, 0) / (FPS * 3600) for d in dirs]

    increases = [max(c - l, 0) for c, l in zip(current_hours, last_hours)]
    base_values = [c - inc for c, inc in zip(current_hours, increases)]

    plt.figure(figsize=(max(8, n*0.8), 5))
    bars_base = plt.bar(dirs, base_values, color='skyblue', width=width, label='original data')
    bars_incr = plt.bar(dirs, increases, bottom=base_values, color='green', width=width, label='this week')

    max_height = max([base + inc for base, inc in zip(base_values, increases)])
    plt.ylim(0, max_height * 1.1)

    # 柱子上显示小时数
    for b, i, base, inc in zip(bars_base, bars_incr, base_values, increases):
        plt.text(b.get_x() + b.get_width()/2, base + inc + 0.05, f"{base + inc:.2f}",
                 ha='center', va='bottom', fontsize=10)

    plt.xlabel("Task")
    plt.ylabel("Hours")
    plt.title(f"Total Hours by Task Name")
    plt.legend()
    plt.tight_layout()

    date_str = datetime.now().strftime("%Y%m%d")
    img_dir = os.path.join('data_stats_log', 'img_count')
    os.makedirs(img_dir, exist_ok=True)
    output_path = os.path.join(img_dir, f"hour_chart_{date_str}.png")
    plt.savefig(output_path)
    plt.close()
    print(f"[INFO] Hours 柱状图已保存到 {output_path}")





def monitor_data_changes(base_dir, sub_dirs):
    print("开始扫描文件...")
    config = _load_config()
    last_counts = config.get('last_counts', {})
    last_frames = config.get('last_frames', {})

    current_counts, current_frames = _get_file_counts_and_frames(base_dir, sub_dirs)
    total_current_episodes = sum(current_counts.values())
    total_current_frames = sum(current_frames.values())

    log_message = datetime.now().strftime('%Y年 %m月 %d日 ')

    if not last_counts:  # 首次初始化
        log_message += "首次初始化，记录当前基准数据量："
        for sub_dir in current_counts:
            log_message += f"{sub_dir} {current_counts[sub_dir]}条 episode, {current_frames[sub_dir]} frames; "
        log_message += f"总 episode: {total_current_episodes}, 总 frames: {total_current_frames}"

        print("首次执行，建立基准：", log_message)
        _write_log(log_message)
        _save_config({'last_counts': current_counts, 'last_frames': current_frames})

        plot_bar_chart(current_counts, {d: 0 for d in current_counts})
        plot_hours_bar_chart(current_frames, {d: 0 for d in current_frames})
        return

    # 正常逻辑：对比上次数量
    for sub_dir in sub_dirs:
        current_ep = current_counts.get(sub_dir, 0)
        last_ep = last_counts.get(sub_dir, 0)
        change_ep = current_ep - last_ep
        change_text_ep = "增加" if change_ep >= 0 else "减少"

        current_fr = current_frames.get(sub_dir, 0)
        last_fr = last_frames.get(sub_dir, 0)
        change_fr = current_fr - last_fr
        change_text_fr = "增加" if change_fr >= 0 else "减少"

        log_message += (f"{sub_dir} episode {change_text_ep}{abs(change_ep)}条, "
                        f"frames {change_text_fr}{abs(change_fr)}; ")

    log_message += f"总 episode: {total_current_episodes}, 总 frames: {total_current_frames}"
    print("扫描完成。记录日志：", log_message)
    _write_log(log_message)

    # 更新配置
    _save_config({'last_counts': current_counts, 'last_frames': current_frames})

    # 绘制柱状图
    plot_bar_chart(current_counts, last_counts)
    plot_hours_bar_chart(current_frames, last_frames)


def main():
    parser = argparse.ArgumentParser(description="监控指定目录下的 .hdf5 文件数量和总 frames")
    parser.add_argument("--base-dir", type=str, default="OCL4Rob", help="数据根目录")
    parser.add_argument("--sub-dirs", nargs="+", default=["pp_two_cube", "pour"], help="需要监控的子目录")
    parser.add_argument("--run-now", action="store_true", help="立即运行一次扫描")
    parser.add_argument("--watch", action="store_true", help="进入定时模式（每周四18:00运行）")
    args = parser.parse_args()

    if args.run_now:
        monitor_data_changes(base_dir=args.base_dir, sub_dirs=args.sub_dirs)

    if args.watch:
        schedule.every().thursday.at("18:00").do(monitor_data_changes,
                                                base_dir=args.base_dir,
                                                sub_dirs=args.sub_dirs)
        print("进入定时模式：每周四18:00自动运行扫描，按 Ctrl+C 退出。")
        while True:
            schedule.run_pending()
            time.sleep(1)

    if not args.run_now and not args.watch:
        parser.print_help()


if __name__ == "__main__":
    main()
