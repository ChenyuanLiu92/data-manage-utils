#!/bin/bash

# =================================================================
# 机器人数据监控自动化设置脚本（适配 Conda 环境）
# 该脚本用于设置一个定时任务，每周四晚上18点运行 Python 监控脚本。
# 注意：需要自行配置Systemd 或保持 crontab 可用
# =================================================================

PYTHON_SCRIPT="monitor_robot_data.py"

# 设置需要监控的目录
BASE_DIR="Your Data Directory"  
SUB_DIRS=("task_name_1" "task_name_2")

# 设置 Conda 环境名称
CONDA_ENV="data_monitor"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误：找不到 Python 脚本 '$PYTHON_SCRIPT'。"
    echo "请确保脚本位于当前目录下。"
    exit 1
fi

# 检查 crontab 命令是否可用
if ! command -v crontab &> /dev/null; then
    echo "错误：找不到 'crontab' 命令。"
    echo "请确保您的系统已安装 cron。"
    exit 1
fi

# 获取脚本的绝对路径
SCRIPT_PATH="$(pwd)/$PYTHON_SCRIPT"

# 构造子目录参数字符串
SUB_DIRS_STR=""
for dir in "${SUB_DIRS[@]}"; do
    SUB_DIRS_STR+="$dir "
done
SUB_DIRS_STR=$(echo "$SUB_DIRS_STR" | xargs)

# 构造完整的 cron 命令（激活 Conda 环境后运行）
CRON_JOB="0 18 * * 4 /bin/bash -c 'source \"$HOME/miniconda3/etc/profile.d/conda.sh\" && conda activate $CONDA_ENV && python \"$SCRIPT_PATH\" --run-now --base-dir $BASE_DIR --sub-dirs $SUB_DIRS_STR'"

echo "================================================================="
echo "        机器人数据监控脚本设置向导（Conda 版本）"
echo "================================================================="
echo "即将为您的用户设置一个定时任务，它将每周四18:00自动运行。"
echo "任务详情："
echo "-----------------------------------------------------------------"
echo "Python 脚本路径: $SCRIPT_PATH"
echo "Conda 环境: $CONDA_ENV"
echo "监控目录: $BASE_DIR/${SUB_DIRS_STR// / }"
echo "Cron 任务命令：$CRON_JOB"
echo "-----------------------------------------------------------------"
read -p "您确定要继续吗？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消。"
    exit 1
fi

# 将任务添加到 crontab
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH" ; echo "$CRON_JOB") | crontab -
echo "-----------------------------------------------------------------"
echo "✔ 定时任务已成功添加！"
echo "您可以通过运行 'crontab -l' 来验证。"
echo "✔ 请确保您的数据目录 '$BASE_DIR' 位于当前目录。"
echo "-----------------------------------------------------------------"

echo "要立即运行一次扫描进行测试，请运行："
echo "conda activate $CONDA_ENV && python $PYTHON_SCRIPT --run-now"
echo ""
echo "配置完成。"
