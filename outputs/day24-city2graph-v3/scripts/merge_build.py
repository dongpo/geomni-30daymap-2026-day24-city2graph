from pathlib import Path
import geopandas as gpd,pandas as pd,shapely,json,time,city2graph as c,shutil
P=Path('outputs/day24-city2graph-v3');Q=Path('outputs/day24-city2graph-v2')
for i in [2,3,4,5]:
 for f in (Q/'data').glob(f'*{i}*'):
  if f.name.startswith((f'{i}-',f'view-{i}',f'inspect-{i}')):shutil.copy2(f,P/'data'/f.name)
 shutil.copy2(Q/f'evidence/{i}-graph.json',P/f'evidence/{i}-graph.json')
stat={}
for kind in ['buildings','streets']:
 frames=[]
 for i,city in [(0,'臺北市'),(1,'新北市')]:
  d=gpd.read_parquet(Q/f'data/{i}-{kind}.parquet');d['source_city']=city;frames.append(d)
 d=gpd.GeoDataFrame(pd.concat(frames,ignore_index=True),crs=frames[0].crs)
 if kind=='buildings':key=d.osm_id.astype(str)
 else:key=d.osm_id.astype(str)+'|'+shapely.to_wkb(shapely.normalize(d.geometry),hex=True)
 mask=~key.duplicated();stat[kind]={'before':len(d),'duplicate_rows_removed':int((~mask).sum()),'after':int(mask.sum())};d=d[mask].reset_index(drop=True);d.to_parquet(P/f'data/0-{kind}.parquet')
(P/'evidence/dedup.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2));print(stat,flush=True)
b=gpd.read_parquet(P/'data/0-buildings.parquet');s=gpd.read_parquet(P/'data/0-streets.parquet');s=s[s.bridge.isin(['no','']) & s.tunnel.isin(['no',''])].copy().reset_index(drop=True);s=s.explode(ignore_index=True);b=b.explode(ignore_index=True);b=b[(b.geom_type=='Polygon') & (b.area>1)].reset_index(drop=True)
t=time.perf_counter();print('START unified Taipei/NewTaipei',len(b),len(s),flush=True)
nodes,edges=c.morphological_graph(b,s,keep_buildings=True,keep_segments=True,tessellation_n_jobs=4,tessellation_fallback=False)
stat={'city':'雙北','city2graph':c.__version__,'seconds':time.perf_counter()-t,'nodes':{},'edges':{},'method':'one morphological_graph call on deduplicated merged inputs; no internal city boundary barrier'}
for k,g in nodes.items():g.to_parquet(P/f'data/0-nodes-{k}.parquet');stat['nodes'][k]=len(g)
for k,g in edges.items():
 name='--'.join(k);g.to_parquet(P/f'data/0-edges-{name}.parquet');stat['edges'][name]=len(g)
(P/'evidence/0-graph.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2));print(stat,flush=True)
