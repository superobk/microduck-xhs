# 来源与版本边界

核对日期：2026-09-17。来源标号用于逐期技术清单，不把个人实验结果归因给上游。

| 编号 | 一手来源 | 用途与边界 |
|---|---|---|
| S1 | https://docs.radxa.com/en/zero/zero3/accessories/camera | ZERO 3 CSI规格、支持相机、rsetup流程；以匹配的Radxa OS为前提 |
| S2 | https://docs.radxa.com/en/zero/zero3 | 板卡系列规格，不证明用户手中配置 |
| S3 | https://docs.kernel.org/userspace-api/media/v4l/v4l2.html | V4L2节点、格式、能力；不能用节点名代替采集验收 |
| S4 | https://gstreamer.freedesktop.org/documentation/video4linux2/v4l2src.html | v4l2src及管线能力协商 |
| S5 | https://mujoco.readthedocs.io/en/stable/python.html | MuJoCo Python与viewer；离屏、计算和交互窗口分开 |
| S6 | https://github.com/pollen-robotics/microduck_rl/blob/1e79c29c97d8b38aee9eefde77a545860ba7658e/README.md | 本系列固定参考：mjlab/PPO、50Hz、61维/14维、导出归一化；不是本机已验证版本 |
| S7 | https://github.com/pollen-robotics/microduck_rl/blob/1e79c29c97d8b38aee9eefde77a545860ba7658e/scripts/infer_policy.py | 已核读前220行：模型路径、默认姿态、统一命令开关、终端键盘输入 |
| S8 | https://onnxruntime.ai/docs/api/python/api_summary.html | InferenceSession、元数据、输入输出描述 |
| S9 | https://arxiv.org/abs/1707.06347 | PPO原始论文；比喻只用于解释，不替代算法定义 |
| S10 | https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html | VideoCapture接口参考；本次采集脚本仍须在真实节点验证 |
| S11 | https://github.com/pollen-robotics/microduck/blob/main/README.md | 2026-09-17核读当前入口：runtime与训练仓库分开。当前runtime已演进，不能把旧教程与main接口混用 |
| S12 | https://github.com/pollen-robotics/elec_RPI_Robot_HAT | 原理图检索入口；本次未做具体板版次/针脚验证，禁止据此直接接线 |
| S13 | https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ | XL330-M288-T 3.7–6.0V/推荐5V；Model Number 1200；寄存器表与机械电气警告 |
| S14 | https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/ | DYNAMIXEL SDK接口参考；只读台架也需实际供电/适配器确认 |
| S15 | https://developers.openai.com/api/docs/guides/image-generation | GPT Image API。批量脚本未发出任何付费请求，不能把提示词算作图片 |

## 出版与引用

本仓库不重新分发上游CAD、权重、固件或视频。引用上游代码请保留原始许可与来源；生成的概念图不是官方外观或结构尺寸认证。公开发布截图需去掉API密钥、MAC/IP、SSID、个人目录和私人界面；原始证据保留本地，不因发布裁剪丢失原始信息。

## 实际进度与来源分级

- 用户实际记录：已启动`uv run scripts/infer_policy.py --walking alpha_walking.onnx --new-cmd-obs`，日志出现场景/策略加载与GLFW缺少DISPLAY错误。没有本次重新执行的证据。
- 已有规划：ZERO 3W摄像头、RL仿真、GPU训练、IMU/HAT/供电研究。
- 未确认：相机实际型号/首帧、板卡具体内存版本、完整稳定仿真、训练收敛、舵机单测、IMU实测、装配与自主行走。
- 本机GPU数量是资源背景，不构成多卡训练证据。7.40V仿真参数不构成硬件供电依据。
