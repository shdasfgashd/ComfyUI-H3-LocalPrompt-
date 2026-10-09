import json, copy
from pathlib import Path
root=Path(__file__).parent
original=json.load(open(root.parent/'upload/minimax视频参考1x加速(1).json'))
d=copy.deepcopy(original); nodes={n['id']:n for n in d['nodes']}
nodes[143]['mode']=0
nodes[138]['outputs'][0]['links']=[]
nodes[138]['title']='旧手写提示词（备份，已断开）'
d['links']=[l for l in d['links'] if l[0]!=279]
req=[('frames','IMAGE'),('source_duration','FLOAT'),('target_duration','FLOAT')]
widgets=[('model_folder','STRING'),('device','COMBO'),('max_frames','INT'),('max_side','INT'),('max_new_tokens','INT'),('transcribe','BOOLEAN'),('whisper_folder','STRING'),('direction','STRING')]
an={'id':186,'type':'H3LocalVideoPrompt','pos':[-2100,6500],'size':[520,500],'flags':{},'order':21,'mode':0,'inputs':[{'name':n,'type':t,'link':None} for n,t in req]+[{'name':n,'type':t,'widget':{'name':n}} for n,t in widgets]+[{'name':'audio','type':'AUDIO','shape':7,'link':None},{'name':'product_image','type':'IMAGE','shape':7,'link':None}], 'outputs':[{'name':'h3_prompt','type':'STRING','links':[]},{'name':'analysis_report','type':'STRING','links':[]}], 'properties':{'Node name for S&R':'H3LocalVideoPrompt'},'widgets_values':['Qwen3-VL-4B-Instruct','cpu',12,448,1400,False,'faster-whisper-small','Create a professional English H3 prompt following the reference video action order and camera pacing. Preserve the separately connected product image exactly. Do not invent product functions or nationality. No subtitles, captions or watermarks.']}
rev={'id':187,'type':'H3PromptReview','pos':[-1500,6500],'size':[600,520],'flags':{},'order':22,'mode':0,'inputs':[{'name':'generated_prompt','type':'STRING','link':None},{'name':'analysis_report','type':'STRING','link':None},{'name':'manual_override','type':'STRING','widget':{'name':'manual_override'}}], 'outputs':[{'name':'final_prompt','type':'STRING','links':[]}], 'properties':{'Node name for S&R':'H3PromptReview'},'widgets_values':['']}
d['nodes'] += [an,rev];nodes.update({186:an,187:rev})
def link(i,src,ss,dst,ds,t):
 d['links'].append([i,src,ss,dst,ds,t]);nodes[src]['outputs'][ss].setdefault('links',[]).append(i);nodes[dst]['inputs'][ds]['link']=i
for args in [(372,143,0,186,0,'IMAGE'),(373,143,2,186,1,'FLOAT'),(374,132,0,186,2,'FLOAT'),(375,143,1,186,11,'AUDIO'),(376,139,0,186,12,'IMAGE'),(377,186,0,187,0,'STRING'),(378,186,1,187,1,'STRING'),(379,187,0,136,12,'STRING')]:link(*args)
d['last_node_id']=187;d['last_link_id']=379
d['extra']['ds']={'scale':0.7,'offset':[2200,-6300]}
d['groups'].append({'title':'本地视频分析 → 英文 H3 提示词 → 预览/覆盖','bounding':[-2150,6440,1290,650],'color':'#385c76','font_size':24,'flags':{}})
for name,analysis in [('H3_Local_Auto.json',False),('H3_Local_Analyze_Only.json',True)]:
 out=copy.deepcopy(d)
 if analysis:
  for n in out['nodes']:
   if n['id'] not in [143,132,139,186,187]:n['mode']=2
 (root/name).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Created two workflows')
