#!/usr/bin/env python3
"""Build publication packs and honest non-AI SVG covers from the editorial source."""
import argparse, base64, datetime as dt, html, importlib.util, json, pathlib, re, textwrap
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('series',ROOT/'content/series.py'); source=importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
REPLACE={'capture_metrics.py':'tools/lab.py capture','model_audit.py':'tools/lab.py model','onnx_audit.py':'tools/lab.py onnx','validate_trajectory.py':'tools/lab.py trajectory','dxl_readonly.py':'tools/lab.py dxl'}
def clean(t):
    for a,b in REPLACE.items(): t=t.replace(a,b)
    return t

def text(x,y,s,size=30,fill='#183435',weight=500,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(s))}</text>'
def box(x,y,w,h,fill='#FFFFFF',stroke='#183435',radius=20):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
def arrow(x1,y1,x2,y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#1C796A" stroke-width="5" fill="none" marker-end="url(#arrow)"/>'
def duck(x,y,s=1):
    return f'<g transform="translate({x},{y}) scale({s})"><rect x="-62" y="-95" width="120" height="85" rx="24" fill="#CDE8DE" stroke="#183435" stroke-width="5"/><rect x="40" y="-58" width="58" height="28" rx="9" fill="#EF9A50" stroke="#183435" stroke-width="4"/><circle cx="17" cy="-65" r="9" fill="#183435"/><path d="M-11 -9 V16" stroke="#183435" stroke-width="11"/><rect x="-65" y="15" width="115" height="91" rx="22" fill="#F7F4EA" stroke="#183435" stroke-width="5"/><circle cx="-30" cy="57" r="13" fill="#EF9A50" stroke="#183435" stroke-width="3"/><path d="M-40 104 L-58 145 L-40 174 M25 105 L48 145 L25 174" stroke="#183435" stroke-width="9" fill="none"/><path d="M-65 178 H-9 M6 178 H62" stroke="#1C796A" stroke-width="13" stroke-linecap="round"/></g>'
LABELS=[['实物丝印','系统镜像','排线规格'],['物理连接','配置探测','视频输出'],['设备能力','格式协商','首帧解码'],['帧到达间隔','读取状态','温度变化'],['计算执行','离屏渲染','交互窗口'],['动作索引','模型关节','实机映射'],['观测合同','ONNX策略','动作合同'],['模型加载','参考推理','独立评测'],['动作尝试','分项奖励','策略更新'],['128环境','512环境','1024环境'],['观测与动作','奖励与终止','版本与种子'],['固定考卷','保留失败','报告分布'],['代码与模型','接口与配置','安全准入'],['计算 / 电源','通信 / 姿态','替代验证'],['准确型号','稳压与保护','测量再接入'],['单颗接入','身份核对','只读反馈'],['传感器坐标','坐标变换','机身坐标'],['左右结构','机械参考位','夹点与走线'],['只读与急停','受控小动作','受保护姿态'],['通过的证据','未过的关卡','下一次实验']]
def diagram(i):
    labels=LABELS[i-1]; out=''
    if i==10:
        for r in range(5):
            for c in range(9):
                x=185+c*88;y=510+r*57
                out+=f'<rect x="{x}" y="{y}" width="42" height="25" rx="7" fill="#CDE8DE" stroke="#1C796A" stroke-width="2"/><circle cx="{x+30}" cy="{y+9}" r="3" fill="#183435"/><path d="M{x+8} {y+25}v9 M{x+30} {y+25}v9" stroke="#183435" stroke-width="3"/>'
        out+=text(540,474,'环境数量 ≠ 策略数量 ≠ GPU数量',30,anchor='middle')
        out+=arrow(540,820,540,854)+box(310,867,460,75,fill='#CDE8DE')+text(540,916,'共享策略 · 逐档扩容',30,anchor='middle')
    elif i==7:
        for r in range(5):
            for c in range(6): out+=box(165+c*22,538+r*26,15,18,fill='#CDE8DE',stroke='#1C796A',radius=3)
        out+=text(230,740,'61维',54,anchor='middle')+arrow(330,605,423,605)+box(446,526,188,165,fill='#CDE8DE')+text(540,605,'ONNX',38,anchor='middle')+text(540,650,'合同先行',25,anchor='middle')+arrow(657,605,741,605)
        for n in range(7):out+=box(770,525+n*24,110,13,fill='#F4D7B8',stroke='#183435',radius=4)
        out+=text(825,740,'14维',54,anchor='middle')+text(540,863,'先核对维度，再核对每一维的含义',31,anchor='middle')
    elif i in (4,12,20):
        for n,l in enumerate(labels):
            y=485+n*143;out+=box(150,y,780,114,fill=['#CDE8DE','#FFFFFF','#F4D7B8'][n])+text(195,y+48,f'0{n+1}',25,fill='#1C796A',weight=700)+text(285,y+67,l,38,weight=700)+text(865,y+68,'—',42,anchor='middle')
        out+=text(540,973,'没有实测的数据，不填成绩',26,anchor='middle')
    elif i in (6,14,17,18):
        out+=duck(534,590,1.2)
        for n,l in enumerate(labels):
            x=[152,694,370][n];y=[475,650,858][n];w=[253,250,340][n]
            out+=box(x,y,w,85,fill=['#FFFFFF','#F4D7B8','#CDE8DE'][n])+text(x+w/2,y+54,l,27,anchor='middle')
        out+=arrow(405,516,445,540)+arrow(677,704,640,697)
    elif i in (9,11,13):
        coords=[(175,486),(625,486),(401,795)]
        for n,((x,y),l) in enumerate(zip(coords,labels)):
            out+=box(x,y,275,107,fill=['#CDE8DE','#F4D7B8','#FFFFFF'][n])+text(x+137,y+62,l,30,anchor='middle')
        out+=arrow(465,540,602,540)+arrow(760,615,660,764)+arrow(371,817,277,619)+duck(540,638,.48)
    elif i==15:
        out+=box(143,495,365,245,fill='#CDE8DE')+text(325,553,'标准XL330-M288-T',24,anchor='middle')+text(325,649,'5.0 V',69,weight=800,anchor='middle')+text(325,699,'官方推荐电压',27,anchor='middle')
        out+=box(575,495,365,245,fill='#F4D7B8')+text(757,553,'现有仿真日志参数',26,anchor='middle')+text(757,649,'7.40 V',62,weight=800,anchor='middle')+text(757,699,'不能照抄为实物供电',24,anchor='middle')
        out+=text(540,837,'3.7–6.0 V：标准器件输入范围',32,anchor='middle')+text(540,908,'2S原始电压不得直接接入',34,fill='#AC4F22',weight=700,anchor='middle')
    elif i==5:
        out+=box(156,468,765,340,fill='#FFFFFF')+f'<path d="M156 528H920" stroke="#183435" stroke-width="3"/>'
        for x in [189,221,253]:out+=f'<circle cx="{x}" cy="498" r="8" fill="#EF9A50"/>'
        out+=text(540,610,'DISPLAY = ?',53,weight=800,anchor='middle')+text(540,674,'先确认图形会话',35,anchor='middle')+text(540,735,'EGL ≠ 交互窗口',31,anchor='middle')+duck(825,842,.48)
    else:
        for n,l in enumerate(labels):
            y=479+n*145;out+=box(220,y,640,99,fill=['#CDE8DE','#FFFFFF','#F4D7B8'][n])+text(267,y+62,f'0{n+1}',27,weight=700,fill='#1C796A')+text(565,y+64,l,36,weight=700,anchor='middle')
            if n<2:out+=arrow(540,y+108,540,y+132)
        if i in (16,19):out+=text(540,957,'前一关未通过，下一关不启动',28,anchor='middle')
        else:out+=text(540,957,'先看证据，再推进下一步',28,anchor='middle')
    return out

def cover(e):
    i=e['id']; a,b=e['cover'];color='#1C796A'
    rule=e['checks'][0]; lines=textwrap.wrap(rule,27)[:2]
    s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440"><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#1C796A"/></marker><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#DDE3D9" stroke-width="1"/></pattern></defs><g font-family="Noto Sans CJK SC, Noto Sans CJK TC, PingFang SC, Microsoft YaHei, sans-serif"><rect width="1080" height="1440" fill="#F7F4EA"/><rect x="60" y="410" width="960" height="600" rx="34" fill="url(#grid)"/>'''
    s+=text(65,77,'MICRODUCK / 40天复现实验',25,fill=color,weight=800)+text(1015,79,f'EP {i:02}',27,fill=color,weight=800,anchor='end')
    s+=f'<path d="M65 111H1015" stroke="#183435" stroke-width="2"/>'
    s+=text(65,217,a,78,weight=900)+text(65,320,b,78,weight=900)+text(67,372,f'DAY {2*i-1:02}—{2*i:02}   /   方法笔记 · 结果以实测为准',24,fill=color)
    s+=diagram(i)
    s+=box(64,1045,952,240,fill='#183435',stroke='#183435')+text(102,1100,'本期复现关卡',25,fill='#CDE8DE',weight=700)
    for n,line in enumerate(lines):s+=text(102,1159+n*46,line,31,fill='#FFFFFF',weight=600)
    s+=text(67,1350,'技术示意 · 非实测画面 · 非GPT生成',24,fill=color)+text(1015,1350,f'{i:02} / 20',25,fill=color,anchor='end')
    s+=text(67,1397,'从看到画面，到理解动作，再到安全装配。',21,fill='#63766E')+'</g></svg>'
    return s

PROMPT_STYLE='''为Microduck复现系列制作一张高质量技术插画。纵向构图，温暖纸白背景、深墨绿轮廓、薄荷绿模块、少量暖橙色强调。抽象双足机械鸭作为统一吉祥物：圆角头部、短喙、分节机械腿，不声称准确复刻官方外观。像工程师的实验手账，有趣但不是幼儿玩具广告。采用清晰的等距构图与少量技术示意元素，避免复杂纹理。顶部保留约25%留白、底部保留约18%留白供后期排版。不要生成任何字母、汉字、数字、logo、水印、假代码、假日志、假性能图表。不得模拟用户已完成的测试，不用照片级画面充当实物证据。不得绘制未经确认的精确针脚、电源接线或可误导的装配尺寸。图像仅作概念插画，发布时必须另行添加“AI示意图，非实测”。'''

def build(start, png=False):
    start=dt.date.fromisoformat(start); records=[]
    outdirs=['posts','assets/covers','assets/prompts','evidence/raw','evidence/public']
    for d in outdirs:(ROOT/d).mkdir(parents=True,exist_ok=True)
    plan=['# 40天 / 20期内容与复現清单','',f'起始日：{start}；每期第2天建议发布。日期是内容排期，不会自动发布或自动设提醒。','', '| 期数 | 实验窗口 | 建议发布 | 标题 | 实验入口 |','|---|---|---|---|---|']
    complete=['# 20期可复制正文与逐期技术清单','', '正文均可作为方法笔记发布；测量结论只从实际证据补充。每期正式发布前仍需人工审阅。','']
    cards=[]; prompts=['# 20份GPT Image生图稿','', '实际GPT生成图片：0张。本文件是生图输入，不是图片完成证明。','']
    for e0 in source.EPISODES:
        e={k:clean(v) if isinstance(v,str) else v for k,v in e0.items()}; i=e['id']; key=f'{i:02}';d1=start+dt.timedelta(days=2*(i-1));d2=d1+dt.timedelta(days=1)
        if len(e['title'])>20: raise ValueError(f'Title exceeds editorial budget: {key}')
        if len(e['body'])>950: raise ValueError(f'Body exceeds editorial budget: {key}')
        folder=ROOT/'posts'/key;folder.mkdir(exist_ok=True)
        (folder/'title.txt').write_text(e['title']+'\n',encoding='utf8');(folder/'body.txt').write_text(e['body']+'\n',encoding='utf8')
        svg=cover(e);(ROOT/'assets/covers'/f'{key}.svg').write_text(svg,encoding='utf8')
        if png:
            import cairosvg
            cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/'assets/covers'/f'{key}.png'),output_width=1080,output_height=1440)
        prompt=PROMPT_STYLE+'\n\n本期主题：'+e['title']+'\n画面内容：'+e['scene']+'\n后期排版主标题：'+ ' / '.join(e['cover'])+'（仅供理解，不在生成图中画字）。'
        (ROOT/'assets/prompts'/f'{key}.txt').write_text(prompt,encoding='utf8')
        refs='、'.join(e['refs']); checklist=f"# EP{key}｜{e['title']}\n\n实验：{d1}–{d2}；建议发布：{d2}。\n\n## 第一天\n{e['day1']}\n\n## 第二天\n{e['day2']}\n\n## 技术验收\n"+'\n'.join('- [ ] '+clean(x) for x in e['checks'])+f"\n\n操作入口：[RUNBOOK {e['lab']}](../../docs/RUNBOOK.md)；资料：{refs}，见[SOURCES](../../docs/SOURCES.md)。\n\n## 配图顺序\nP1：本期技术示意封面（非GPT生成、非实测）。\n"+'\n'.join(e['photos'])+'\n\n## 失败也可以发布\n未通过时保留方法正文，补充实际错误、已排除项、下一次只改变的变量。不要填写不存在的成功结果。\n\n## 实测补充槽位（内部使用，不直接复制）\n实际环境：\n原始证据路径：\n实际结果与单位：\n未解决项：\n公开图已检查隐私：否\n'
        (folder/'checklist.md').write_text(checklist,encoding='utf8')
        (folder/'image_prompt.txt').write_text(prompt,encoding='utf8')
        plan.append(f"| {key} | {d1}–{d2} | {d2} | [{e['title']}](posts/{key}/body.txt) | [{e['lab']}](docs/RUNBOOK.md) |")
        complete+=['---',f"## EP{key}｜{e['title']}",f'实验：{d1}–{d2}；建议发布：{d2}','',e['body'],'',checklist.replace('# EP'+key,'### 清单 EP'+key,1),'']
        prompts += [f'## EP{key} {e["title"]}',prompt,'']
        records.append({'id':i,'date':str(d2),'title':e['title'],'body_chars':len(e['body']),'title_chars':len(e['title']),'method_copy_ready':True,'gpt_image_generated':(ROOT/'assets/gpt-image'/f'{key}.png').is_file(),'cover_kind':'programmatic_technical_illustration','refs':e['refs']})
        img='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
        cards.append({'id':key,'title':e['title'],'body':e['body'],'date':str(d2),'img':img,'prompt':prompt,'checklist':checklist,'photos':e['photos']})
    (ROOT/'CONTENT_PLAN.md').write_text('\n'.join(plan)+'\n',encoding='utf8')
    (ROOT/'ALL_POSTS.md').write_text('\n'.join(complete),encoding='utf8')
    (ROOT/'assets/GPT_IMAGE_PROMPTS.md').write_text('\n'.join(prompts),encoding='utf8')
    (ROOT/'content/catalog.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    status=ROOT/'status.json'
    if not status.exists():
        status.write_text(json.dumps({'schema_version':1,'baseline_date':'2026-09-17','episodes':[{'id':e['id'],'state':'blocked' if e['id']==5 else 'not_started','evidence':[],'result':'现有日志：GLFW缺少DISPLAY；尚无修复验证。' if e['id']==5 else '', 'published_url':None} for e in source.EPISODES]},ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'assets/gpt-image').mkdir(exist_ok=True)
    gpt_status=ROOT/'assets/gpt-image/status.json'
    if not gpt_status.exists():gpt_status.write_text(json.dumps({'generated_count':0,'reviewed_count':0,'note':'No native image generation tool was available; programmatic covers are stored separately.'},ensure_ascii=False,indent=2),encoding='utf8')
    page=(ROOT/'tools/publisher.template.html').read_text(encoding='utf8').replace('__CARDS_JSON__',json.dumps(cards,ensure_ascii=False).replace('</','<\\/'))
    (ROOT/'publisher.html').write_text(page,encoding='utf8')
    print(json.dumps({'episodes':len(records),'range':[str(start),str(start+dt.timedelta(days=39))],'programmatic_svg':20,'programmatic_png':20 if png else 'not requested','gpt_generated':len(list((ROOT/'assets/gpt-image').glob('[0-9][0-9].png')))},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start-date',default=source.START_DATE);p.add_argument('--png',action='store_true');a=p.parse_args();build(a.start_date,a.png)
