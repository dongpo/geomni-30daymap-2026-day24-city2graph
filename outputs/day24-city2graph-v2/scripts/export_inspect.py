from pathlib import Path
from collections import Counter
import json,gzip,sys,geopandas as gpd
P=Path('outputs/day24-city2graph-v2')
for i in range(6):
 if len(sys.argv)>1 and str(i)!=sys.argv[1]:continue
 if not (P/f'evidence/{i}-graph.json').exists():continue
 ns={k:gpd.read_parquet(P/f'data/{i}-nodes-{k}.parquet') for k in ['place','movement']};degrees={k:{r:Counter() for r in ['pp','mm','pm']} for k in ns};rec=[]
 for a,r,z,k in [('place','touched_to','place','pp'),('movement','connected_to','movement','mm'),('place','faced_to','movement','pm')]:
  e=gpd.read_parquet(P/f'data/{i}-edges-{a}--{r}--{z}.parquet');degrees[a][k].update(e.index.get_level_values(0));degrees[z][k].update(e.index.get_level_values(1))
 for t,(kind,g) in enumerate(ns.items()):
  for ix,row in g.iterrows():
   oid=str(row.get('osm_id',''));oid='' if oid in ('nan','None','<NA>') else oid
   if kind=='movement':oid='w'+oid
   rec.append([round(row.geometry.x,2),round(row.geometry.y,2),t,str(ix),oid,*[degrees[kind][r][ix] for r in ['pp','mm','pm']]])
 (P/f'data/inspect-{i}.json.gz').write_bytes(gzip.compress(json.dumps(rec,separators=(',',':')).encode()));print(i,len(rec),flush=True)
