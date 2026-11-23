from pathlib import Path
import json,gzip,array,sys
import geopandas as gpd, numpy as np,shapely
P=Path('outputs/day24-city2graph-v2')
centres=[(121.535,25.055),(121.465,25.015),(121.255,24.975),(120.675,24.16),(120.205,23.015),(120.315,22.65)]
for i in range(6):
 if len(sys.argv)>1 and str(i)!=sys.argv[1]:continue
 if not (P/f'evidence/{i}-graph.json').exists():continue
 b=gpd.read_parquet(P/f'data/{i}-buildings.parquet');bounds=b.total_bounds;origin=bounds[:2];out=array.array('f');meta={'bounds':bounds.tolist(),'origin':origin.tolist(),'layers':{}}
 from shapely.geometry import Point
 meta['centre']=gpd.GeoSeries([Point(*centres[i])],crs=4326).to_crs(3826).iloc[0].coords[0]
 def encode(geoms):
  start=len(out);count=0
  def put(g):
   nonlocal count
   if g is None or g.is_empty:return
   if g.geom_type=='Polygon':
    put(g.exterior)
    for r in g.interiors:put(r)
   elif g.geom_type in ('LineString','LinearRing'):
    count+=1
    for x,y,*_ in g.coords:out.extend((x-origin[0],y-origin[1]))
    out.extend((float('nan'),float('nan')))
   elif hasattr(g,'geoms'):
    for part in g.geoms:put(part)
  for g in geoms:put(g)
  return {'start':start,'length':len(out)-start,'paths':count}
 places=gpd.read_parquet(P/f'data/{i}-nodes-place.parquet');moves=gpd.read_parquet(P/f'data/{i}-nodes-movement.parquet')
 meta['counts']={'place':len(places),'movement':len(moves)}
 meta['layers']['cells']=encode(places.tessellation_geometry)
 meta['layers']['buildings']=encode(b.geometry)
 if 'building_geometry' in places:
  bg=places.building_geometry;tg=places.tessellation_geometry
  mask=bg.notna() & tg.notna() & (shapely.hausdorff_distance(bg.array,tg.array)<.01)
  meta['footprint_like_cells']=int(mask.sum());meta['layers']['fallback']=encode(tg[mask])
 for name,key in [('pp','place--touched_to--place'),('mm','movement--connected_to--movement'),('pm','place--faced_to--movement')]:
  g=gpd.read_parquet(P/f'data/{i}-edges-{key}.parquet');meta['layers'][name]=encode(g.geometry);meta['counts'][name]=len(g)
  if name in ('pp','pm'):
   built=set(places.index[places.osm_id.notna()]);mask=g.index.get_level_values(0).isin(built)
   if name=='pp':mask &= g.index.get_level_values(1).isin(built)
   meta['layers'][name+'Built']=encode(g.geometry[mask]);meta['counts'][name+'Built']=int(mask.sum())
 raw=out.tobytes();(P/f'data/view-{i}.bin.gz').write_bytes(gzip.compress(raw));(P/f'data/view-{i}-meta.json').write_text(json.dumps(meta,ensure_ascii=False));print(i,len(raw),meta['counts'],flush=True)
