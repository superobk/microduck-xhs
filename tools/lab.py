#!/usr/bin/env python3
"""Read-only / software-only helpers. No actuator write instructions are sent."""
import argparse, csv, hashlib, json, math, pathlib, time

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def quantile(values,p):
    if not values: return None
    x=sorted(values); k=(len(x)-1)*p; i=int(k)
    return x[i]+(x[min(i+1,len(x)-1)]-x[i])*(k-i)

def model(a):
    import mujoco
    m=mujoco.MjModel.from_xml_path(str(pathlib.Path(a.path).resolve()))
    rows=[]
    for i in range(m.nu):
        trn=int(m.actuator_trntype[i]); j=int(m.actuator_trnid[i,0])
        joint=None
        if trn in (int(mujoco.mjtTrn.mjTRN_JOINT),int(mujoco.mjtTrn.mjTRN_JOINTINPARENT)):
            joint=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,j)
        rows.append({'index':i,'actuator':mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_ACTUATOR,i),'transmission_type':trn,'target_id':j,'joint':joint})
    print(json.dumps({'file':str(a.path),'sha256_xml_only':digest(a.path),'note':'Includes/meshes require their own manifest','nq':m.nq,'nv':m.nv,'njnt':m.njnt,'nu':m.nu,'actuators':rows},ensure_ascii=False,indent=2))

def onnx(a):
    import onnxruntime as ort
    s=ort.InferenceSession(str(a.path),providers=['CPUExecutionProvider'])
    def desc(x): return {'name':x.name,'shape':x.shape,'type':x.type}
    print(json.dumps({'sha256':digest(a.path),'inputs':[desc(x) for x in s.get_inputs()],'outputs':[desc(x) for x in s.get_outputs()],'metadata':s.get_modelmeta().custom_metadata_map,'note':'Metadata inspection only; not a gait or safety test'},ensure_ascii=False,indent=2))

def temperatures():
    result={}
    for p in pathlib.Path('/sys/class/thermal').glob('thermal_zone*'):
        try: result[p.name+':'+(p/'type').read_text().strip()]=float((p/'temp').read_text())/1000
        except (OSError,ValueError): pass
    return result

def capture(a):
    import cv2
    if a.seconds<=0 or a.width<=0 or a.height<=0: raise ValueError('Positive duration and dimensions required')
    out=pathlib.Path(a.out); out.mkdir(parents=True,exist_ok=True)
    if (out/'frames.csv').exists(): raise ValueError('Output already exists; choose a new directory')
    c=cv2.VideoCapture(a.device,cv2.CAP_V4L2)
    if not c.isOpened(): raise RuntimeError('Could not open capture node; check V4L2/ISP/format first')
    c.set(cv2.CAP_PROP_FRAME_WIDTH,a.width); c.set(cv2.CAP_PROP_FRAME_HEIGHT,a.height)
    actual={'width':c.get(cv2.CAP_PROP_FRAME_WIDTH),'height':c.get(cv2.CAP_PROP_FRAME_HEIGHT),'reported_fps':c.get(cv2.CAP_PROP_FPS)}
    intervals=[]; success=0; failures=0; start=time.monotonic(); previous=None; temp_at=0.; temp={}
    try:
        with (out/'frames.csv').open('w',newline='') as f:
            w=csv.writer(f); w.writerow(['host_monotonic_s','ok','read_duration_ms','success_interval_ms','thermal_c_json'])
            while time.monotonic()-start<a.seconds:
                before=time.monotonic(); ok,frame=c.read(); now=time.monotonic()
                valid=bool(ok and frame is not None and frame.size)
                delta=None
                if valid:
                    success+=1
                    if previous is not None: delta=(now-previous)*1000; intervals.append(delta)
                    previous=now
                else: failures+=1
                if now-temp_at>=1: temp=temperatures(); temp_at=now
                w.writerow([now,int(valid),(now-before)*1000,delta,json.dumps(temp)])
                if (success+failures)%50==0: f.flush()
                if not valid: time.sleep(.01)
    finally: c.release()
    result={'device':a.device,'requested':{'width':a.width,'height':a.height,'seconds':a.seconds},'actual':actual,'elapsed_s':time.monotonic()-start,'success_reads':success,'failed_reads':failures,'arrival_interval_ms':{f'p{int(p*100)}':quantile(intervals,p) for p in (.5,.95,.99)},'note':'Host arrival intervals only, NOT end-to-end latency. Repeated-image freeze is NOT detected.'}
    (out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)); print(json.dumps(result,indent=2))

def finite(x): return type(x) in (int,float) and math.isfinite(x)
def validate_record(r):
    required={'provenance','run_id','episode_id','env_id','step','t_sim_s','seed','policy_sha256','config_sha256','observation','action','reward','next_observation','terminated','truncated'}
    if not required.issubset(r): raise ValueError('Missing fields: '+str(sorted(required-set(r))))
    if r['provenance'] not in ('measured','synthetic'): raise ValueError('Invalid provenance')
    for field,size in [('observation',61),('action',14),('next_observation',61)]:
        if not isinstance(r[field],list) or len(r[field])!=size or not all(finite(v) for v in r[field]): raise ValueError(f'{field}: expected {size} finite numbers; this validator is for the unified contract only')
    for f in ('reward','t_sim_s'):
        if not finite(r[f]): raise ValueError(f'{f}: finite number required')
    for f in ('terminated','truncated'):
        if type(r[f]) is not bool: raise ValueError(f'{f}: bool required')
    for f in ('env_id','step','seed'):
        if type(r[f]) is not int or r[f]<0: raise ValueError(f'{f}: nonnegative integer required')
    for f in ('run_id','episode_id'):
        if not isinstance(r[f],str) or not r[f]: raise ValueError(f'{f}: nonempty string required')
    for f in ('policy_sha256','config_sha256'):
        h=r[f]
        if not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h): raise ValueError(f'{f}: lowercase SHA256 required')

def trajectory(a):
    count=0; synthetic=0
    with open(a.path) as f:
        for line_no,line in enumerate(f,1):
            if not line.strip(): continue
            try: r=json.loads(line); validate_record(r)
            except (ValueError,TypeError) as e: raise ValueError(f'line {line_no}: {e}') from e
            count+=1; synthetic+=r['provenance']=='synthetic'
    if count==0: raise ValueError('Empty trajectory')
    print(json.dumps({'records':count,'synthetic':synthetic,'valid_schema':True,'note':'Schema validity does not establish truth, dynamics quality, or replay determinism'}))

def dxl(a):
    from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS
    if not 0<=a.id<=252 or a.baud<=0: raise ValueError('Invalid ID or baud')
    p=PortHandler(a.port); h=PacketHandler(2.0)
    if not p.openPort(): raise RuntimeError('Port could not be opened')
    try:
        if not p.setBaudRate(a.baud): raise RuntimeError('Baud rate setup failed')
        m,comm,err=h.ping(p,a.id)
        if comm!=COMM_SUCCESS or err: raise RuntimeError(f'Ping failed comm={comm}, error={err}')
        if m!=1200: raise RuntimeError(f'Model {m} is not XL330-M288-T (1200); refusing model-specific register reads')
        record={'model_number':m,'id':a.id,'baud':a.baud}
        for name,addr,size in [('firmware',6,1),('torque_enabled',64,1),('hardware_error',70,1),('position_raw',132,4),('voltage_raw',144,2),('temperature_c',146,1)]:
            value,comm,err=getattr(h,f'read{size}ByteTxRx')(p,a.id,addr)
            if comm!=COMM_SUCCESS or err: raise RuntimeError(f'Read {name} failed: comm={comm},error={err}')
            record[name]=value
        record['voltage_v']=record['voltage_raw']/10
        record['note']='Read-only. Existing torque state is NOT changed. Mechanical safety and exclusive bus access are required.'
        print(json.dumps(record,ensure_ascii=False,indent=2))
    finally: p.closePort()

def main():
    p=argparse.ArgumentParser(description=__doc__); s=p.add_subparsers(dest='task',required=True)
    for name,fn in [('model',model),('onnx',onnx),('trajectory',trajectory)]:
        q=s.add_parser(name); q.add_argument('path'); q.set_defaults(fn=fn)
    q=s.add_parser('capture'); q.set_defaults(fn=capture); q.add_argument('--device',required=True); q.add_argument('--width',type=int,default=640); q.add_argument('--height',type=int,default=480); q.add_argument('--seconds',type=float,default=600); q.add_argument('--out',required=True)
    q=s.add_parser('dxl'); q.set_defaults(fn=dxl); q.add_argument('--port',required=True); q.add_argument('--id',type=int,required=True); q.add_argument('--baud',type=int,required=True)
    a=p.parse_args()
    try: a.fn(a)
    except ImportError as e: p.exit(2,f'Missing dependency in this interpreter: {e}. See RUNBOOK.md; no packages installed automatically.\n')
    except (ValueError,RuntimeError,OSError) as e: p.exit(2,str(e)+'\n')
if __name__=='__main__': main()
