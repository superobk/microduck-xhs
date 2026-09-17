#!/usr/bin/env python3
"""Opt-in GPT Image calls. Default is a dry run; requires an external paid API key to execute."""
import argparse,base64,hashlib,json,os,pathlib,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--start',type=int,default=1);p.add_argument('--count',type=int,default=1);p.add_argument('--model',default='gpt-image-2.5-flare');a=p.parse_args()
 if a.start<1 or a.count<1 or a.start+a.count-1>20:p.error('Requested episode range must be within 1..20')
 if a.execute and not os.environ.get('OPENAI_API_KEY'):p.error('Set OPENAI_API_KEY locally. Do not put a key in GitHub or this command line.')
 out=ROOT/'assets/gpt-image';out.mkdir(parents=True,exist_ok=True)
 for i in range(a.start,a.start+a.count):
  prompt_file=ROOT/'assets/prompts'/f'{i:02}.txt'
  if not prompt_file.exists():p.error('Run tools/build.py first')
  image=out/f'{i:02}.png'
  if image.exists():print(f'{i:02}: exists, skipped (no charge)');continue
  payload={'model':a.model,'prompt':prompt_file.read_text(),'size':'1024x1536','quality':'medium','n':1}
  if not a.execute:print(f'DRY RUN EP{i:02}: {a.model}; no network call; output {image.name}');continue
  req=urllib.request.Request('https://api.openai.com/v1/images/generations',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},method='POST')
  try:
   with urllib.request.urlopen(req,timeout=240) as response:result=json.load(response)
   raw=base64.b64decode(result['data'][0]['b64_json'],validate=True)
   if not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Expected PNG response; stopped without saving')
   image.write_bytes(raw)
   metadata={'episode':i,'model':a.model,'status':'generated_unreviewed','sha256':hashlib.sha256(raw).hexdigest(),'usage':result.get('usage'),'note':'Must review and add AI illustration label. Not a measured hardware image. Raw image is 2:3; crop/pad deliberately for a 3:4 cover, never stretch.'}
   image.with_suffix('.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2));print(f'EP{i:02}: generated, NOT reviewed or published')
   count=len(list(out.glob('[0-9][0-9].png')));(out/'status.json').write_text(json.dumps({'generated_count':count,'reviewed_count':0,'note':'All API outputs need manual review and AI disclosure.'},ensure_ascii=False,indent=2))
  except (urllib.error.URLError,KeyError,ValueError,OSError) as e:
   # Do not retry paid generations automatically: a timeout may have been charged.
   p.exit(2,f'EP{i:02} failed ({type(e).__name__}); no automatic retry. Check account/request status before retrying. Key and response body not logged.\n')
if __name__=='__main__':main()
