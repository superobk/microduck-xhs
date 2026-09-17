# Microduck · 40天技术与心得分享

从ZERO 3W摄像头与软件测试，到RL仿真，再到安全的硬件台架与拼装。20期、每2天一期；正文＋两日任务＋验收清单＋实拍计划＋技术封面＋GPT生图稿。

**先打开 `publisher.html`：逐期复制标题/正文、下载封面PNG、查看验收与补图清单。不会自动登录或发布到小红书。**

## 从这里开始

```bash
git clone https://github.com/superobk/microduck-xhs.git
cd microduck-xhs
python3 tools/build.py
# macOS可直接双击publisher.html；或仅本机预览
python3 -m http.server 8000 --bind 127.0.0.1
```

浏览器打开 `http://127.0.0.1:8000/publisher.html`。生成器只用Python标准库，不安装CUDA、不控制机器人。已有日期需要整体平移时：`python3 tools/build.py --start-date 2026-09-17`。默认实验期2026-09-17至2026-10-26，首次建议发布9月18日，每期第2天发布，不是自动提醒。

| 文件 | 用法 |
|---|---|
| [CONTENT_PLAN.md](CONTENT_PLAN.md) | 20期主题、实验窗口与建议发布日期 |
| [ALL_POSTS.md](ALL_POSTS.md) | 全部正文与逐期技术清单；正文不含待填占位符 |
| [posts/](posts/) | 每期title.txt、body.txt、checklist.md、image_prompt.txt |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | L01–L20操作步骤、命令和阻塞条件 |
| [docs/SOURCES.md](docs/SOURCES.md) | 一手资料、上游SHA、实际进度边界 |
| [assets/covers/](assets/covers/) | 20张原创技术示意SVG；PNG在发布包或构建后获得 |
| [assets/GPT_IMAGE_PROMPTS.md](assets/GPT_IMAGE_PROMPTS.md) | 20份统一风格GPT Image输入稿 |
| [status.json](status.json) | 技术实际进度；与内容完成状态分开 |
| [docs/hardware_inventory.md](docs/hardware_inventory.md) | 实物型号、关节映射与IMU坐标合同 |

## 图片完成状态：必须区分

已经制作：20张程序绘制的技术示意封面，3:4、1080×1440；不是实测画面，不是GPT生成图。当前会话没有原生gpt-image工具，**实际GPT图片为0张**；20份逐期生图稿与自愿执行的API脚本已准备，不能把提示词算成图片。

```bash
# 默认dry-run，不读密钥、不发请求、不产生费用
python3 tools/generate_gpt_images.py --start 1 --count 20
# 只有你在本机准备OPENAI_API_KEY并明确执行时才会发出付费请求
# 先单张验证，审图后再分批；不要把密钥提交GitHub
# python3 tools/generate_gpt_images.py --execute --start 1 --count 1
```

生成图必须人工审查并加“AI示意，非实测”标识。不能用它代替板卡照片、万用表读数、训练截图或行走视频。现成PNG技术封面已明确标识“非GPT生成”。浏览器发布板可无依赖导出PNG；批量PNG可在安装CairoSVG与系统中文字体后运行`python3 tools/build.py --png`。字体不随仓库分发。

## 每期怎么用

第1天按checklist实验并保存原始证据，第2天复测、写实际结果、审图、复制正文。P1放技术示意封面；P2–P4按该期清单补真实照片/截图。正文现为可直接发布的方法笔记，未把未来测试写成成功战报。取得数据后只添加已验证结论。失败时保留错误与下一项实验，不编成功数字。

```bash
# 例：先把真实日志保存在evidence/raw/05/，再记录故障进度
python3 tools/manage.py 5 --state blocked --result 'GLFW仍无法初始化，下一步检查图形会话'
# 通过必须有真实存在的证据文件；此处为语法示例，不代表已经通过
# python3 tools/manage.py 5 --state verified --evidence evidence/raw/05/viewer-log.txt --result '实际验证结论'
python3 tools/test_project.py
```

`evidence/raw/`默认不入Git：保留原始数据，不做不可逆的信息删减。只将人工检查过的公开副本放`evidence/public/`。本仓库是公开仓库，不要提交家庭画面、密钥、私人日志或未经授权的人像。`status.json`可保留原始证据相对路径与哈希，但不要填写敏感内容。

## 真实起点与安全边界

现有记录只确认推理启动并遭遇DISPLAY/GLFW错误；不证明摄像头已出图、模型已稳定、自训已收敛或真机已行走。第5期因此初始化为blocked，其余实验等待证据。参考RL仓库固定到`1e79c29c97d8b38aee9eefde77a545860ba7658e`，不覆盖个人已有工作区，也不假设当前runtime main与该版本完全兼容。

标准XL330-M288-T官方输入3.7–6.0V，推荐5V；仿真日志的7.40V不是供电许可。未确认板版次和原理图前不提供精确针脚接线。只读脚本不下发运动或扭矩写命令，但原有扭矩状态与其他控制进程仍需人工排除。所有硬件结论都必须在正确保护下实测。

## 维护约定

编辑`content/series.py`后运行build和测试。生成器不覆盖`status.json`已有记录。非正文模板里的unknown是内部待核实项，不会进入正文。新增实测结论先补证据，再改文案。不得用合成数据或示意封面给实验清单打通过。
