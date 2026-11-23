from pathlib import Path
import geopandas as gpd,shapely,json
P=Path('outputs/day24-city2graph-v3');Q=Path('outputs/day24-city2graph-v2');out={}
for key in ['place--touched_to--place','movement--connected_to--movement','place--faced_to--movement']:
 old=set();oldcount=0
 for i in [0,1]:
  e=gpd.read_parquet(Q/f'data/{i}-edges-{key}.parquet');oldcount+=len(e);old.update(shapely.to_wkb(shapely.normalize(shapely.set_precision(e.geometry,.01)),hex=True))
 new=gpd.read_parquet(P/f'data/0-edges-{key}.parquet');cross=gpd.read_parquet(P/f'data/0-cross-{key}.parquet');ks=set(shapely.to_wkb(shapely.normalize(shapely.set_precision(cross.geometry,.01)),hex=True));out[key]={'separate_edge_rows_sum':oldcount,'rebuilt_edge_rows':len(new),'cross_city_rows':len(cross),'cross_city_geometries_not_in_separate_graphs_at_1cm':len(ks-old)}
(P/'evidence/rebuild-vs-stitch.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
