# 20期技术复现操作册

先读SOURCES.md。以下是待执行实验与安全关卡，不是已经完成的成绩单。每日两步节奏：第1天实现/排错，第2天复测/记录/整理发布。进度落后时发故障分析，不为赶发布日期跳过安全关卡。

## 共用目录与软件边界

```bash
# 在本仓库根目录执行；不会安装训练栈或控制硬件
python3 tools/build.py
# Mac可直接打开publisher.html；也可启动仅本机可访问的预览
python3 -m http.server 8000 --bind 127.0.0.1
```

ZERO 3W只承担本期板端采集/后续推理实验。GPU工作站运行训练/仿真，不在ZERO 3W安装整套CUDA训练栈。现有工作目录不要直接切换版本：先记录`git status --short`、`git rev-parse HEAD`，保存未提交修改。以下在全新旁路目录拉取已核对的参考版本，不覆盖个人工作区：

```bash
git clone https://github.com/pollen-robotics/microduck_rl.git microduck_rl-reference
cd microduck_rl-reference
git checkout --detach 1e79c29c97d8b38aee9eefde77a545860ba7658e
uv sync --frozen
uv run list-envs
```

第一次安装依赖需要网络；不得把下载失败解释成机器人模型失败。这里固定的是本系列参考，不声称是最新或与手头ONNX自动匹配。相机overlay仅按匹配Radxa OS的文档配置。`tools/lab.py`的模型/ONNX命令应在已安装对应包的环境执行，例如在上游目录`uv run /绝对路径/microduck-xhs/tools/lab.py model ...`。

## L01｜设备身份证

在ZERO 3W本机执行：
```bash
bash tools/camera_probe.sh
```

输出进入`evidence/raw/`。填写`docs/hardware_inventory.md`，拍相机丝印、板卡版次、排线两端触点。只凭选型讨论无法确认实物型号。不要发布包含网络标识的原始日志。

## L02｜驱动与overlay

匹配的Radxa OS：断电检查排线；登录后先备份配置，再执行`sudo rsetup`，只选择真实传感器对应overlay。重启由操作人员确认执行。重新运行probe，对比传感器探测与节点。非Radxa OS应查对应镜像维护者的设备树流程，不移植未经验证的dtbo。不要同时替换内核、镜像、排线和overlay。

## L03｜首帧

```bash
# 软件包名适用于Debian系；先确认当前镜像与APT源
sudo apt update
sudo apt install v4l-utils gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good
v4l2-ctl --list-devices
# DEV必须替换为本机确认的捕获节点，不能直接猜video0
export DEV=/dev/video0
v4l2-ctl -d "$DEV" --all
v4l2-ctl -d "$DEV" --list-formats-ext
mkdir -p evidence/raw/03
# 仅适用于节点支持可协商的video/x-raw输出
# 不硬编码未经枚举验证的分辨率/格式；保留GStreamer协商日志
GST_DEBUG=2 gst-launch-1.0 -e v4l2src device="$DEV" num-buffers=1 ! videoconvert ! jpegenc ! filesink location=evidence/raw/03/first.jpg
# 仅在节点支持image/jpeg时改用此管线（另一个文件，避免覆盖）
# gst-launch-1.0 -e v4l2src device="$DEV" num-buffers=1 ! image/jpeg ! jpegdec ! videoconvert ! pngenc ! filesink location=evidence/raw/03/first.png
```

若输出为Bayer/ISP未配置，不套用以上两条管线；返回检查当前驱动的ISP/media graph。拍到图片后手工打开验证。记录退出码，别只验证文件存在。失败时保留错误原文和协商格式。

## L04｜稳定性

原生apt的OpenCV可用于系统Python；不要与上游uv环境混为一谈。安装依赖后在本仓库运行：
```bash
sudo apt install python3-opencv
# DEV为确认可被OpenCV读取的图像节点；保留实际返回分辨率
# timeout是Linux外层保险：某些后端的read可能阻塞
# 640x480为拟测试配置，不是此相机已支持的声明
timeout 630s python3 tools/lab.py capture --device "$DEV" --width 640 --height 480 --seconds 600 --out evidence/raw/04
```

CSV记录每次读取耗时与成功到达间隔；summary里的p50/p95/p99不是曝光到显示延迟，也不检测冻结画面。读到重复帧需要独立画面变化实验。长时间阻塞会由timeout终止，已有CSV仍保留；缺失summary须标记中断。温度单位按thermal zone驱动确认，不以未知值判断通过。

## L05｜DISPLAY故障

在SSH与远程桌面终端分别记录：
```bash
printf 'DISPLAY=%s\nWAYLAND_DISPLAY=%s\nXDG_SESSION_TYPE=%s\n' "$DISPLAY" "$WAYLAND_DISPLAY" "$XDG_SESSION_TYPE"
nvidia-smi
```

GPU命令成功不证明窗口可用。先在合法图形会话打开上游viewer，再运行原命令：
```bash
uv run python -m mujoco.viewer --mjcf src/mjlab_microduck/robot/microduck/scene.xml
uv run scripts/infer_policy.py --help
uv run scripts/infer_policy.py --walking alpha_walking.onnx --new-cmd-obs
```

必须确认ONNX路径、版本与接口适合`--new-cmd-obs`。不使用`xhost +`、不盲设`:0`。交互viewer依赖显示会话；无显示时可另建离屏渲染或纯计算程序，但不要声称EGL自动修好GLFW窗口。Mac上的passive viewer可能需要`mjpython`，本操作路径面向Ubuntu GPU工作站。

## L06｜MJCF审计

```bash
# 在上游uv环境；替换本仓库的绝对路径
uv run /绝对路径/microduck-xhs/tools/lab.py model src/mjlab_microduck/robot/microduck/scene.xml
```

输出包含nq/nv/njnt/nu与执行器连接。14维指特定步态策略，不是XML所有关节总数。填写joint_map：action_index、joint_name、actuator_name、servo_id、direction、zero、limits、evidence。实机未验证的字段保持unknown。BAM/被动关节/嘴部不能用数组补齐来“兼容”。

## L07｜ONNX合同

```bash
uv run /绝对路径/microduck-xhs/tools/lab.py onnx alpha_walking.onnx
```

只检查输入输出/元数据和SHA256，不用随机输入测试真机。参考统一合同为61维/14维；不同策略文件必须以实际shape与语义核对。逐项检查关节顺序、姿态/四元数约定、单位、commands布局、默认姿态、动作尺度和归一化。上游导出包含normalizer，不能重复应用。维度通过只是第一关。

## L08｜参考策略基线

L05和L07通过后再执行原推理。记录文件哈希、模型、场景、参数、实际命令序列、失败情况。固定参考输入进行对照；键盘交互来源按核对版本为终端TTY，不是随便点击viewer。保存未剪辑录屏，本期只标“参考策略推理”，不标“自主训练成功”。

## L09｜奖励审计

```bash
# 在上游仓库，定位配置与函数后阅读上下文
grep -nE 'reward|weight|ENABLE_' src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py
uv run train Mjlab-Velocity-Flat-MicroDuck --help
```

任务文件若不同先用`find src/mjlab_microduck/tasks -maxdepth 1 -type f`确认，不凭教程猜路径。为每项写目标、符号、可能退化行为；只修改一项，保存diff。安全判据和奖励不是同一概念，不能把回报阈值当硬件急停。

## L10｜并行训练

先确认当前help支持参数；以下为参考README确认的任务与环境数选项：
```bash
CUDA_VISIBLE_DEVICES=0 uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 128
# 128通过后另开实验再测512、1024；不要同时执行三条争抢显存
# CUDA_VISIBLE_DEVICES=0 uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 512
# CUDA_VISIBLE_DEVICES=0 uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024
```

训练为交互前台命令；从本机help选择实际支持的最大迭代选项，或观察冒烟后人工终止，不杜撰统一停止flag。记录是否正常保存checkpoint。先1卡、小规模；不保证指定档位收敛，不搬用上游训练时间作为本机成绩。多卡需另立分布式实验与实际日志。GUI观测规模与训练环境规模分开记录。

## L11｜轨迹数据

`docs/trajectory_schema.json`描述统一合同下的记录。最小真实记录在环境step后生成；同时保存对应输入观测、动作、奖励和下一状态，而不是只存一张截图。频繁写盘可能影响训练：先小样本同步记录验证，再讨论缓冲/分块异步写入。

```python
# 接入示意，不是可直接粘贴的上游变量名；需在真实step边界完成张量到CPU转换
record = {
  'provenance': 'measured', 'run_id': run_id, 'episode_id': episode_id,
  'env_id': env_id, 'step': step, 't_sim_s': simulation_time,
  'seed': seed, 'policy_sha256': policy_sha, 'config_sha256': config_sha,
  'observation': obs_before, 'action': action_applied, 'reward': reward,
  'next_observation': obs_after, 'terminated': terminated, 'truncated': truncated
}
```

向量环境可能自动reset；`next_observation`应保存该转移实际末状态，不能误存reset后的新状态。用环境的final/terminal observation信息处理。PPO在线rollout与归档数据集不同，旧轨迹不自动可用于当前PPO更新。

```bash
python3 tools/lab.py trajectory evidence/raw/11/rollout.jsonl
```

## L12｜评测计划

先保存`eval_plan.json`，字段包括策略SHA、独立训练seed（若有）、eval_seed、命令序列、参数扰动范围、时长和失败定义。计划3个评测seed×10回合只作初步对照。当前infer脚本的交互视频不自动提供这套批量评测；需在环境reset/step层接入固定命令与终止计数，不伪装已有完整评测器。所有实际完成回合逐条记录，再统计成功率；没跑完标partial。

## L13｜软件冻结与准入

以SHA256归档候选模型、uv.lock、配置和接口表；Git记录commit与dirty状态。拒绝把随机变更后的目录称为同一版本。50Hz对应20ms总周期预算；板端实际采样/通信/推理/发送/调度需要分别测量。急停、看门狗、传感器失效处理未验证前，禁止策略接管真实舵机。

## L14｜板件职责与替代

建立功能矩阵：计算/电源/舵机半双工通信/姿态。对每个候选列准确版本、输入电压、逻辑电平、协议、频率、帧约定、驱动改动和证据。当前runtime main已经演进，不用旧Python命令直接控制新runtime。HAT针脚、IMU型号/ID/波特率本次不代为确认；未知项是阻塞，不是“参考接上试试”。

## L15｜供电

标准XL330-M288-T：3.7–6.0V，推荐5.0V。先断电查网、核对极性与回流，再限流测试独立稳压；选择电流预算要看实际负载与瞬态，不能简单给所有舵机分摊主控USB电源。2S常见满充电压超出规格，禁止直连。主控与舵机按合格设计分支；不可把多个稳压输出并联，不可忽略USB回灌。IMU不得未经载流验证当所有舵机电源的串接通道。用适合的电子负载/受控负载测试，不做堵转实验。精确针脚图必须等当前原理图、板版次与实际通断证据。

## L16｜单舵机只读

使用已验证的TTL半双工适配器，不直接将普通USB-UART TX/RX当DXL接口。先停掉可能占用总线的控制进程，确认机械安全。
```bash
# 在隔离环境安装dynamixel-sdk后使用；这里只演示型号出厂通信参数
# 必须以实物现配置为准：ID=1、57600不是每个舵机必然状态
python3 tools/lab.py dxl --port /dev/ttyUSB0 --id 1 --baud 57600
```

脚本仅对指定ID发送ping/read，验证Model Number=1200后读表；不写ID、不启停扭矩、不移动。若原有扭矩已开启，只读不会自动解除；必须物理安全并避免其他控制进程。通信失败先查适配器/参数/接线，不加电压“解决”。

## L17｜IMU

填写frame_contract：板系与机身系的XYZ、加速度/角速度单位、四元数顺序、主动/被动旋转和时间戳域。静止、单轴缓转、多朝向分别留原始数据。仅凭静态加速度不能唯一确定航向；不要从一组静止数据声称完成全部姿态标定。I2C替代需实现runtime的采集/换算/超时/观测适配与回归，不是换一个读函数就完成。

## L18｜断电干装

结构版本、打印材料/方向、舵盘参考位、螺丝长度和走线都记录。关节范围按照具体机构核对，不强行反驱或顶住机械止挡。以照片验证夹点、排线应力、左右件、足底平整。没有统一适用于所有打印件的紧固扭矩，遵从实际零件资料。

## L19｜受保护联调

先真实验证急停、失联保护、姿态失效与超期处理，再按只读→单关节→受保护姿态→低速落地的关卡推进。吊带/支架承重情况必须说明，不能把支撑站立写成自主平衡。未满足条件，不提供一键全扭矩脚本。本仓库不自动下发任何真实机器人动作。

## L20｜复盘

更新`status.json`与证据说明。各关只允许not_started/partial/blocked/verified；不自动从内容已生成推断技术通过。仿真、真实硬件、独立训练三类成绩分别汇总。记录失败假设、有效对照和下一次实验，不给40天到期自动盖章。
