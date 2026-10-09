import json, importlib.util
from pathlib import Path
root=Path(__file__).parent
s=importlib.util.spec_from_file_location('local_node',root/'ComfyUI-H3-LocalPrompt/__init__.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for count in [1,2,12,100,436]:
 ids=m.sample_indices(count,12)
 assert len(ids)==min(count,12) and len(ids)==len(set(ids))
 assert ids[0]==0 and ids[-1]==count-1
for file in root.glob('H3_*.json'):
 d=json.loads(file.read_text());ns={n['id']:n for n in d['nodes']};ls={l[0]:l for l in d['links']}
 assert len(ns)==len(d['nodes']) and len(ls)==len(d['links'])
 for lid,src,ss,dst,ds,typ in d['links']:
  assert lid in ns[src]['outputs'][ss]['links']
  assert ns[dst]['inputs'][ds]['link']==lid
  assert ns[src]['outputs'][ss]['type']==typ or typ=='*'
 for n in d['nodes']:
  for inp in n.get('inputs',[]):
   if inp.get('link') is not None:assert inp['link'] in ls
  for out in n.get('outputs',[]):
   for lid in out.get('links') or []:assert lid in ls
 for nid,cls in [(186,m.H3LocalVideoPrompt),(187,m.H3PromptReview)]:
  spec=cls.INPUT_TYPES();assert [i['name'] for i in ns[nid]['inputs']]==list(spec['required'])+list(spec.get('optional',{}))
 assert ns[143]['mode']==0 and ns[136]['inputs'][12]['link']==379
 if 'Analyze_Only' in file.name:
  assert all(n['mode']==2 for n in ns.values() if n['id'] not in [143,132,139,186,187])
 print(file.name,'PASS:',len(ns),'nodes,',len(ls),'links')
assert m.H3PromptReview().review('auto','report','manual')['result']==('manual',)
assert m.H3PromptReview().review('auto','report',' ')['result']==('auto',)
print('Sampling, interfaces, review override: PASS')
