from pathlib import Path
import json,hashlib
import geopandas as gpd,numpy as np
P=Path('outputs/day24-city2graph-v3');allstats={}
for i,n in enumerate(['雙北','新北市','桃園市','臺中市','臺南市','高雄市']):
 if i==1 or not (P/f'evidence/{i}-graph.json').exists():continue
 b=gpd.read_parquet(P/f'data/{i}-buildings.parquet');nodes={k:gpd.read_parquet(P/f'data/{i}-nodes-{k}.parquet') for k in ['place','movement']}
 stat={'source_building_objects':len(b),'place_nodes':len(nodes['place']),'movement_nodes':len(nodes['movement']),'edges':{}}
 p=nodes['place'];represented=set(p.osm_id.dropna());excluded=b[~b.osm_id.isin(represented)];excluded.to_parquet(P/f'data/{i}-unrepresented-buildings.parquet');stat['unrepresented_building_objects']=len(excluded);stat['places_without_building_id']=int(p.osm_id.isna().sum());stat['invalid_place_polygons']=int((~p.tessellation_geometry.is_valid).sum())
 for a,r,z in [('place','touched_to','place'),('movement','connected_to','movement'),('place','faced_to','movement')]:
  key='--'.join([a,r,z]);e=gpd.read_parquet(P/f'data/{i}-edges-{key}.parquet');idx=e.index;stat['edges'][key]={'count':len(e),'missing_endpoints':int((~idx.get_level_values(0).isin(nodes[a].index)).sum()+(~idx.get_level_values(1).isin(nodes[z].index)).sum()),'empty_geometry':int(e.geometry.is_empty.sum()),'invalid_geometry':int((~e.geometry.is_valid).sum()),'zero_length':int((e.length==0).sum())}
 allstats[n]=stat
(P/'evidence/qa-data.json').write_text(json.dumps(allstats,ensure_ascii=False,indent=2));print(json.dumps(allstats,ensure_ascii=False))
