# Day24 — Network · city2graph 城市紋理

[互動地圖](https://dongpo.github.io/geomni-30daymap-2026-day24-city2graph/) · [32秒影片](video/Day24-city2graph-operation-32s.mp4) · [資料說明](DATA-NOTES.txt)

雙北共同建圖，與桃園、臺中、臺南、高雄並列。保留完整兩類節點（場所、街段）及三類關係（PP相鄰、MM連通、PM介面）。總覽採共同30×30公里都市視窗，不是全市行政範圍；點選可查看完整圖。

## 使用
從本專案根目錄啟動 `python3 -m http.server 8000`，開啟 http://localhost:8000 。支援 WebGL 與 DecompressionStream 的瀏覽器。首次載入約百餘MB，手機效能未驗收。

## 資料與程式
- 網頁：`index.html`、`app.js`，使用 v7 視覺表達。
- `outputs/day24-city2graph-v3/data`：完整節點、關係與輸入 Parquet，以及網頁顯示資料。
- `outputs/day24-city2graph-v2/data`：原六市抽取建物與街段，供雙北去重重建。
- v2/v3 的 `scripts` 保存實際抽取、建圖、去重、驗證、顯示資料匯出程式；Python3.12與依賴鎖檔。
- 原始全臺PBF未重複上傳，使用2026-11-09 Geofabrik快照；已抽取輸入與來源證據保留。不是用今天的PBF就能重現同一份結果。

## 從已抽取輸入重建
於根目錄建立 `work/day24-venv`，安裝requirements-lock.txt。建立v2/v3的data/evidence目錄後執行：
```
work/day24-venv/bin/python outputs/day24-city2graph-v2/scripts/build_graphs.py
work/day24-venv/bin/python outputs/day24-city2graph-v3/scripts/merge_build.py
work/day24-venv/bin/python outputs/day24-city2graph-v3/scripts/cross_city.py
work/day24-venv/bin/python outputs/day24-city2graph-v3/scripts/export_binary.py 0
work/day24-venv/bin/python outputs/day24-city2graph-v3/scripts/export_inspect.py 0
work/day24-venv/bin/python outputs/day24-city2graph-v3/scripts/validate.py
```
其餘四市顯示檔已隨專案保留。端到端乾淨環境重建未另行驗證；原腳本保留原工作目錄結構及依賴，抽取階段需額外原始PBF（見v2 REPRODUCE）。

## 授權與限制
© OpenStreetMap contributors；衍生資料依ODbL 1.0：https://www.openstreetmap.org/copyright 。市界為NLSC政府資料開放授權條款第1版。程式未另宣告授予開源授權。city2graph本身授權請參閱其原專案。

場所是模型鑲嵌而非地籍；介面非核實出入口。OSM缺漏、橋隧排除及分割失敗會影響結果；不能把空白當作都市無建物、把線當作實際交通流量。詳見DATA-NOTES.txt。

影片為實際瀏覽器操作逐幀擷取後依時間戳編碼，無地圖影格合成；原比例保留，另加字幕帶，無音訊。Facebook草稿待本人審核，公開地圖不代表已發布貼文。
