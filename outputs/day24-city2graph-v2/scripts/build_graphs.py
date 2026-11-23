from pathlib import Path
import time,json,sys,traceback
import geopandas as gpd,city2graph as c,shapely
P=Path('outputs/day24-city2graph-v2')
names=['臺北市','新北市','桃園市','臺中市','臺南市','高雄市']
for i,n in enumerate(names):
 if len(sys.argv)>1 and str(i)!=sys.argv[1]:continue
 t=time.perf_counter();print('START',n,c.__version__,flush=True)
 b=gpd.read_parquet(P/f'data/{i}-buildings.parquet');s=gpd.read_parquet(P/f'data/{i}-streets.parquet')
 # Surface morphology: exclude bridges/tunnels from planar graph rather than falsely connect crossings.
 s=s[s.bridge.isin(['no','']) & s.tunnel.isin(['no',''])].copy().reset_index(drop=True)
 s=s.explode(ignore_index=True);b=b.explode(ignore_index=True)
 b=b[b.geometry.geom_type=='Polygon'];b=b[b.area>1].reset_index(drop=True)
 try:
  nodes,edges=c.morphological_graph(b,s,keep_buildings=True,keep_segments=True,tessellation_n_jobs=1,tessellation_fallback=False)
  stats={'city':n,'city2graph':c.__version__,'seconds':time.perf_counter()-t,'nodes':{},'edges':{}}
  for k,g in nodes.items():
   g.to_parquet(P/f'data/{i}-nodes-{k}.parquet');stats['nodes'][k]=len(g)
  for k,g in edges.items():
   name='--'.join(k);g.to_parquet(P/f'data/{i}-edges-{name}.parquet');stats['edges'][name]=len(g)
  (P/f'evidence/{i}-graph.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print(stats,flush=True)
 except Exception as e:
  traceback.print_exc();(P/f'evidence/{i}-failure.txt').write_text(traceback.format_exc())
