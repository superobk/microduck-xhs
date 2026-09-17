#!/usr/bin/env python3
import ast,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
series=load('series_test',ROOT/'content/series.py');lab=load('lab_test',ROOT/'tools/lab.py')
class ProjectTests(unittest.TestCase):
 def test_twenty(self):self.assertEqual([e['id'] for e in series.EPISODES],list(range(1,21)))
 def test_copy_budget(self):
  for e in series.EPISODES:
   self.assertLessEqual(len(e['title']),20);self.assertLessEqual(len(e['body']),950);self.assertGreater(len(e['body']),250);self.assertNotIn('TODO',e['body']);self.assertEqual(len(e['checks']),4)
 def test_generated(self):
  for n in range(1,21):
   for file in ['title.txt','body.txt','checklist.md','image_prompt.txt']:self.assertTrue((ROOT/'posts'/f'{n:02}'/file).is_file())
   self.assertIn('非GPT生成',(ROOT/'assets/covers'/f'{n:02}.svg').read_text())
 def test_quantiles(self):self.assertEqual(lab.quantile([1,2,3],.5),2);self.assertIsNone(lab.quantile([],.95))
 def test_trajectory_guard(self):
  with self.assertRaises(ValueError):lab.validate_record({})
 def test_trajectory_sample(self):
  r=dict(provenance='synthetic',run_id='test',episode_id='test-0',env_id=0,step=0,t_sim_s=0.,seed=0,policy_sha256='0'*64,config_sha256='1'*64,observation=[0.]*61,action=[0.]*14,next_observation=[0.]*61,reward=0.,terminated=False,truncated=False)
  lab.validate_record(r);r['action'][0]=float('nan')
  with self.assertRaises(ValueError):lab.validate_record(r)
 def test_no_servo_writes(self):
  tree=ast.parse((ROOT/'tools/lab.py').read_text())
  attrs=[n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)]
  self.assertFalse(any('write' in n.lower() and ('tx' in n.lower() or 'packet' in n.lower()) for n in attrs))
 def test_status_not_claimed(self):
  s=json.loads((ROOT/'status.json').read_text())
  for e in s['episodes']:
   if e['state']=='verified':self.assertTrue(e['evidence'])
if __name__=='__main__':unittest.main()
