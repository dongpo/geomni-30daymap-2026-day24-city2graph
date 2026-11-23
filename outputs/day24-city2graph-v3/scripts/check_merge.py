from pathlib import Path
import geopandas as gpd,pandas as pd,shapely,json
P=Path('outputs/day24-city2graph-v3');Q=Path('outputs/day24-city2graph-v2');out={}
b=pd.concat([gpd.read_parquet(Q/f'data/{i}-buildings.parquet') for i in [0,1]],ignore_index=True)
dup=b[b.osm_id.duplicated(False)];out['duplicated_building_ids']=dup.osm_id.unique().tolist();out['conflicting_building_geometry_ids']=[str(k) for k,g in dup.groupby('osm_id') if len(set(shapely.to_wkb(shapely.normalize(g.geometry),hex=True)))>1]
s=gpd.read_parquet(P/'data/0-streets.parquet');keys=s.osm_id.astype(str)+'|'+shapely.to_wkb(shapely.normalize(s.geometry),hex=True);out['remaining_duplicate_street_keys']=int(keys.duplicated().sum());out['remaining_duplicate_building_ids']=int(gpd.read_parquet(P/'data/0-buildings.parquet').osm_id.duplicated().sum());out['all_unique_source_streets_preserved']=len(s)==146378;out['all_unique_source_buildings_preserved']=len(gpd.read_parquet(P/'data/0-buildings.parquet'))==130198
(P/'evidence/qa-merge.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
