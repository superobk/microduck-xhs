#!/usr/bin/env python3
"""Record manually reviewed experimental progress; content readiness is a separate state."""
import argparse,datetime,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('episode',type=int);p.add_argument('--state',choices=['not_started','partial','blocked','verified'],required=True);p.add_argument('--evidence',action='append',default=[]);p.add_argument('--result',required=True);a=p.parse_args()
 if not 1<=a.episode<=20:p.error('Episode must be 1..20')
 path=ROOT/'status.json'
 if not path.exists():p.error('Run tools/build.py first')
 data=json.loads(path.read_text());row=next(e for e in data['episodes'] if e['id']==a.episode);files=[]
 for filename in a.evidence:
  f=(ROOT/filename).resolve()
  try:rel=f.relative_to(ROOT/'evidence')
  except ValueError:p.error('Evidence must be inside evidence/, not artwork or arbitrary external paths')
  if not f.is_file() or f.stat().st_size==0:p.error('Evidence must exist and be nonempty')
  if 'synthetic' in str(rel).lower():p.error('Synthetic samples cannot be proof of measured progress')
  h=hashlib.sha256(f.read_bytes()).hexdigest();files.append({'path':'evidence/'+str(rel),'sha256':h})
 if a.state=='verified' and not (row['evidence'] or files):p.error('verified requires a real evidence path; scripts cannot judge scientific truth')
 row['state']=a.state;row['result']=a.result;row['evidence']+=files;row['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(path);print(f'EP{a.episode:02}: {a.state}; evidence recorded, not uploaded or independently verified')
if __name__=='__main__':main()
