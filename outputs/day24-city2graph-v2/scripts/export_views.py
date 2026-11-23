from pathlib import Path
import json,geopandas as gpd
P=Path('outputs/day24-city2graph-v2')
def paths(geoms):
 out=[]
 for g in geoms:
  if g is None or g.is_empty:continue
  if g.geom_type=='Polygon':
   out.append([[round(x,1),round(y,1)] for x,y,*_ in g.exterior.coords])
  elif g.geom_type=='LineString':out.append([[round(x,1),round(y,1)] for x,y,*_ in g.coords])
  elif hasattr(g,'geoms'):out.extend(paths(g.geoms))
 return out
for i in range(6):
 if not (P/f'data/{i}-nodes-place.parquet').exists():continue
 places=gpd.read_parquet(P/f'data/{i}-nodes-place.parquet');moves=gpd.read_parquet(P/f'data/{i}-nodes-movement.parquet');b=gpd.read_parquet(P/f'data/{i}-buildings.parquet')
 d={'bounds':b.total_bounds.tolist(),'counts':{'place':len(places),'movement':len(moves)},'cells':paths(places.tessellation_geometry),'buildings':paths(b.geometry)}
 for name,key in [('pp','place--touched_to--place'),('mm','movement--connected_to--movement'),('pm','place--faced_to--movement')]:
  d[name]=paths(gpd.read_parquet(P/f'data/{i}-edges-{key}.parquet').geometry)
 (P/f'data/view-{i}.json').write_text(json.dumps(d,separators=(',',':')))
 print(i,len(d['cells']),{k:len(d[k]) for k in ['pp','mm','pm']},flush=True)
