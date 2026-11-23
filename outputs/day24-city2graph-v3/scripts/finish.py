from pathlib import Path
import subprocess,time,sys
P=Path('outputs/day24-city2graph-v3');deadline=time.monotonic()+3600
while not (P/'evidence/0-graph.json').exists():
 if time.monotonic()>deadline:raise TimeoutError('Merged graph not complete; no output substituted')
 time.sleep(10)
for args in [('cross_city.py',),('export_binary.py','0'),('export_inspect.py','0'),('validate.py',),('compare_rebuild.py',)]:
 print('RUN',args,flush=True);subprocess.run([sys.executable,str(P/'scripts'/args[0]),*args[1:]],check=True)
print('EXPORTS_AND_DATA_QA_COMPLETE',flush=True)
