from pathlib import Path
import json,subprocess,bisect,hashlib
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent;rows=json.loads((p/'capture.json').read_text());im=Image.open(p/'frames'/rows[0]['file']);w,h=im.size;outheight=h+64
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',22)
ff=Path('work/day07-env/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0').resolve();out=p/'Day24-city2graph-operation-32s.mp4'
pr=subprocess.Popen([str(ff),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{outheight}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
times=[r['t'] for r in rows]
def caption(t):
 if t<5:return '五個都市區，同一尺度：雙北／桃園／臺中／臺南／高雄'
 if t<13:return '點選臺中、逐級放大：從城市紋理走進異構圖'
 if t<16:return '兩類節點：藍色圓點＝場所；金色方點＝街段'
 if t<19:return '關係一：場所與場所的相鄰（藍色）'
 if t<22:return '關係二：街段與街段的連通（深藍）'
 if t<25:return '關係三：場所與街段的介面（紫色）'
 if t<28:return '合回完整異構圖：兩類節點 × 三種空間關係'
 return '返回五城總覽，比較不同都市的空間紋理'
for i in range(32*30):
 t=i/30;r=rows[max(0,bisect.bisect_right(times,t)-1)];im=Image.open(p/'frames'/r['file']).convert('RGB');can=Image.new('RGB',(w,outheight),'#17394b');can.paste(im,(0,0));ImageDraw.Draw(can).text((24,h+18),caption(t),fill='white',font=font);pr.stdin.write(can.tobytes())
 if i in [30,360,435,525,615,705,795,900]:can.save(p/f'preview-{i//30}.png')
pr.stdin.close();assert pr.wait()==0
subprocess.run([str(ff),'-v','error','-i',str(out),'-f','null','-'],check=True)
gaps=[b-a for a,b in zip(times,times[1:])];q={'seconds':32,'resolution':[w,outheight],'original_frame_resolution':[w,h],'encoded_fps':30,'capture_frames':len(rows),'capture_method':'Timestamped actual browser screenshots during CUA UI operations; resampled to 30fps, no map frame synthesis','capture_average_fps':len(rows)/32,'max_capture_gap_s':max(gaps),'audio':'none; map has no audio','aspect_ratio':'original frame retained pixel-for-pixel; added 64px subtitle band','decode':'PASS','sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(p/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(q)
