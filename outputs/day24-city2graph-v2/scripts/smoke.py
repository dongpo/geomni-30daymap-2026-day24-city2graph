import geopandas as gpd,city2graph as c,json,time,faulthandler
from pathlib import Path
from shapely.geometry import box
faulthandler.dump_traceback_later(60,repeat=True)
p=Path('outputs/day24-city2graph-v2');b=gpd.read_parquet(p/'data/0-buildings.parquet');s=gpd.read_parquet(p/'data/0-streets.parquet');bb=box(301000,2770000,302000,2771000);b=b[b.intersects(bb)].explode(ignore_index=True);s=s[s.intersects(bb)&s.bridge.eq('no')&s.tunnel.eq('no')].reset_index(drop=True);print(len(b),len(s),flush=True);t=time.perf_counter();ns,es=c.morphological_graph(b,s,limit=bb,keep_buildings=True,tessellation_n_jobs=1);print({k:len(v) for k,v in ns.items()},{k:len(v) for k,v in es.items()},time.perf_counter()-t,flush=True)
(p/'evidence/smoke.json').write_text(json.dumps({'scope':'1km test only, not six-city deliverable','version':c.__version__,'nodes':{k:len(v) for k,v in ns.items()},'edges':{'--'.join(k):len(v) for k,v in es.items()},'seconds':time.perf_counter()-t}))
