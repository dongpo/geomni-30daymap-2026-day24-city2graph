from pathlib import Path
import geopandas as gpd,numpy as np,json
P=Path('outputs/day24-city2graph-v3')
c=gpd.read_file(P/'source/counties.geojson').to_crs(3826);c=c[c.COUNTYNAME.isin(['臺北市','新北市'])]
ns={k:gpd.read_parquet(P/f'data/0-nodes-{k}.parquet') for k in ['place','movement']};stats={};labels={}
for k,n in ns.items():
 label=np.full(len(n),'界外／待核',dtype=object)
 for _,r in c.iterrows():label[n.geometry.intersects(r.geometry).to_numpy()]=r.COUNTYNAME
 labels[k]=dict(zip(n.index,label));n['assigned_city']=label;n.to_parquet(P/f'data/0-nodes-{k}.parquet');stats[k]={str(v):int((label==v).sum()) for v in np.unique(label)}
stats['cross_city']={}
for a,r,z in [('place','touched_to','place'),('movement','connected_to','movement'),('place','faced_to','movement')]:
 key='--'.join([a,r,z]);e=gpd.read_parquet(P/f'data/0-edges-{key}.parquet');aa=np.array([labels[a][x] for x in e.index.get_level_values(0)]);zz=np.array([labels[z][x] for x in e.index.get_level_values(1)]);mask=(aa!=zz)&np.isin(aa,['臺北市','新北市'])&np.isin(zz,['臺北市','新北市']);stats['cross_city'][key]=int(mask.sum());e[mask].to_parquet(P/f'data/0-cross-{key}.parquet')
for city in ['臺北市','新北市']:
 b=gpd.read_parquet(P/'data/0-buildings.parquet');stats.setdefault('source_buildings',{})[city]=int((b.source_city==city).sum())
(P/'evidence/cross-city.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print(stats)

import csv
with (P/"data/city-statistics.csv").open("w",encoding="utf-8-sig",newline="") as f:
 w=csv.writer(f);w.writerow(["city","source_buildings","model_places","movement_nodes"])
 for city in ["臺北市","新北市","界外／待核"]:w.writerow([city,stats["source_buildings"].get(city,0),stats["place"].get(city,0),stats["movement"].get(city,0)])
