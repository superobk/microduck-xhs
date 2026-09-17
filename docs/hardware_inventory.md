# 实物与接口登记（由实际操作填写）

本文件中的unknown是内部清单，不会被拼进可发布正文。

| 项目 | 实物型号/版本 | 接口/配置 | 证据 | 状态 |
|---|---|---|---|---|
| ZERO 3W | unknown | 镜像/内核/内存/eMMC：unknown | 无 | 待核实 |
| 相机 | unknown | 传感器/排线规格/overlay：unknown | 无 | 待核实 |
| HAT/通信适配器 | unknown | 原理图版次/半双工/逻辑电平：unknown | 无 | 待核实 |
| IMU/转换板 | unknown | 固件/坐标系/ID/波特率：unknown | 无 | 待核实 |
| 舵机 | unknown | 准确型号/ID清单：unknown | 无 | 待核实 |
| 电池/稳压/保护 | unknown | 电压/载流/急停/回灌：unknown | 无 | 待核实 |

## joint_map

| 动作索引 | 模型关节名 | 执行器名 | 实机ID | 方向 | 零位 | 机械限位 | 证据 |
|---|---|---|---|---|---|---|---|
| 待从模型导出 | unknown | unknown | unknown | unknown | unknown | unknown | 无 |

## frame_contract

| 项目 | 实际约定 | 验证方法/证据 |
|---|---|---|
| 传感器板坐标与机身坐标 | unknown | 静止/分轴旋转/多朝向 |
| 角速度/加速度单位 | unknown | 原始数据与固件 |
| 四元数顺序、旋转方向 | unknown | 固件与正向变换测试 |
| 时间戳域与超时处理 | unknown | 数据时序记录 |
