from pathlib import Path
import json,osmium,shapely,geopandas as gpd
from shapely.geometry import shape,LineString
from collections import Counter
P=Path('outputs/day24-city2graph-v2'); names=['臺北市','新北市','桃園市','臺中市','臺南市','高雄市']
cs=json.loads(Path('outputs/day23-taste-v2/source/counties.geojson').read_text())
polys={f['properties']['COUNTYNAME']:shape(f['geometry']) for f in cs['features'] if f['properties']['COUNTYNAME'] in names}
for p in polys.values():shapely.prepare(p)
fac=osmium.geom.WKBFactory(); buildings={n:[] for n in names}; roads={n:[] for n in names}
def cities(g):
 p=g.representative_point();return [n for n,b in polys.items() if b.covers(p)]
class Buildings(osmium.SimpleHandler):
 def area(self,a):
  if not a.tags.get('building') or a.tags.get('building')=='no':return
  try:g=shapely.from_wkb(fac.create_multipolygon(a));g=shapely.make_valid(g)
  except Exception:return
  if g.geom_type not in ('Polygon','MultiPolygon') or g.is_empty:return
  for n in cities(g):buildings[n].append({'osm_id':('w' if a.from_way() else 'r')+str(a.orig_id()),'geometry':g})
class Roads(osmium.SimpleHandler):
 def way(self,w):
  if not w.tags.get('highway'):return
  try: coords=[(n.lon,n.lat) for n in w.nodes];g=LineString(coords)
  except Exception:return
  if g.is_empty or g.length==0:return
  row={'osm_id':w.id,'refs':[n.ref for n in w.nodes],'coords':coords,'bridge':w.tags.get('bridge','no'),'tunnel':w.tags.get('tunnel','no'),'highway':w.tags.get('highway')}
  for n,p in polys.items():
   if p.intersects(g):roads[n].append(row)
print('Reading buildings',flush=True)
Buildings().apply_file(str(P/'source/buildings.osm.pbf'),locations=True)
print('Reading streets',flush=True)
Roads().apply_file('outputs/day24-network-v1/source/motor-roads.osm.pbf',locations=True)
summary={}
for i,n in enumerate(names):
 b=gpd.GeoDataFrame(buildings[n],crs=4326).drop_duplicates('osm_id').to_crs(3826);b.to_parquet(P/f'data/{i}-buildings.parquet')
 counts=Counter(r for w in roads[n] for r in set(w['refs'])); ss=[]
 for w in roads[n]:
  start=0
  for j in range(1,len(w['refs'])):
   if j==len(w['refs'])-1 or counts[w['refs'][j]]>1:
    g=LineString(w['coords'][start:j+1]);ss.append({'osm_id':w['osm_id'],'bridge':w['bridge'],'tunnel':w['tunnel'],'highway':w['highway'],'geometry':g});start=j
 s=gpd.GeoDataFrame(ss,crs=4326).to_crs(3826);s=s[s.length>0.01];s.to_parquet(P/f'data/{i}-streets.parquet')
 summary[n]={'buildings':len(b),'segments':len(s)};print(n,summary[n],flush=True)
(P/'evidence/source-counts.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
