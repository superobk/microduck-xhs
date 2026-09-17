# 交付核验与限制

核验日期：2026-09-17。

## 实际完成

- 20期正文、20期两日清单、80个技术验收项、60个实拍补图位。
- 20张1080×1440 PNG技术封面、20张对应SVG、总览图；均为程序绘制，非GPT生成、非实测。
- 20份GPT Image生图稿与默认dry-run的API辅助脚本；实际GPT图片0张，没有发出付费生成请求。
- 8项本地单元测试通过，Python源码编译检查与Shell语法检查通过。
- Chromium以内联HTML方式验证20期导航、20张封面加载、canvas转换PNG，无JavaScript错误。
- 当前浏览器环境策略阻止file/localhost导航，因此未验证本地URL打开方式、真实操作系统剪贴板和点击下载的全链路；已验证页面渲染与PNG编码逻辑。没有登录或发布到小红书。

## GitHub实际写入与构建

仓库：https://github.com/superobk/microduck-xhs

源文件提交：`1158a679feac4b65a2049f4b363ea476cb8285f4`。

GitHub Actions构建成功：https://github.com/superobk/microduck-xhs/actions/runs/35194943945

生成的20期独立文件、发布页面、PNG/SVG封面已提交main：`0855d6664f7b7c7bf0bc583c629fc9197ef9cc4d`。

本地与远端源文件目录Git tree哈希逐一核对一致：

| 目录 | 已匹配的tree SHA |
|---|---|
| tools | 582d892bb97daf0dfd95d91aa8e7566430f34dc7 |
| docs | 637d122604e244e2867442b2d5642bb1b4cf5a02 |
| .github | 1d9f59cfd8de753465e4c8fd4b4f19d3cacfcd3e |
| content中的series.py源 | e05f1b090b9d6cbb27b71bf6ffdb73dfc61d8cc2 |

PNG在本地和GitHub Linux环境分别渲染；不同系统字体与渲染器版本可能造成像素/文件哈希差异，不宣称二进制逐字节一致。所有字体来自运行系统，不随仓库或下载包分发。

## 未完成的不是测试通过项

没有在用户的ZERO 3W、摄像头、GPU工作站、IMU或舵机上执行新测试。没有运行强化学习训练、读取用户的ONNX文件、操作真实机器人或验证自主平衡。轨迹校验器和只读脚本不等于已经接入上游训练/真实台架。

实验状态与文案完成状态分离：EP05沿用用户日志标记blocked；其余技术关卡等待实际证据。内容排期2026-09-17至2026-10-26仅为可平移的计划，不是已设定的自动发布或提醒。
