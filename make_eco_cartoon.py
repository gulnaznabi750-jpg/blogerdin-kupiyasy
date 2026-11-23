import asyncio, math, os, subprocess, wave, io, random, time
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import numpy as np
from pathlib import Path

OUT=Path("public")
OUT.mkdir(exist_ok=True)
VIDEO=OUT/"eco-fraction-lab-cartoon.mp4"
W,H,FPS=960,540,12
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F=lambda s,b=False:ImageFont.truetype(BOLD if b else FONT,s)
S=[
{"title":"ЭКОЛАБОРАТОРИЯ ОТКРЫТА!","formula":["ECO FRACTION LAB","МИССИЯ: СПАСТИ ЭКОШКОЛУ"],"dialog":[
("girl","Привет, ребята! Я Лиза. Добро пожаловать в нашу экологическую лабораторию! Сегодня нам нужны настоящие математические исследователи."),
("robot","Бип-бип! Я ЭкоБот. Чтобы сделать школу ещё зеленее, нам предстоит научиться складывать и вычитать дроби с разными знаменателями!"),
("girl","И никаких скучных секретов! Всё покажем на примерах. Поехали!")],"mode":"intro"},
{"title":"МИССИЯ 1. ЗЕЛЁНАЯ КРЫША","formula":["1/2 + 1/3 = ?","НЕ СКЛАДЫВАЙ ЗНАМЕНАТЕЛИ!"],"dialog":[
("girl","Мы озеленили одну вторую часть крыши, а потом ещё одну третью. Сколько крыши теперь зелёное?"),
("robot","Ой! Если просто сложить верхние и нижние числа, получится две пятых. Но это ошибка!"),
("girl","Почему? Потому что половинка и треть — кусочки разного размера. Сначала сделаем их одинаковыми!")],"mode":"roof"},
{"title":"ШАГ 1. ОБЩИЙ ЗНАМЕНАТЕЛЬ","formula":["НОК(2, 3) = 6","1/2 = 3/6   •   1/3 = 2/6"],"dialog":[
("robot","Наш общий знаменатель — шесть. Половину превращаем в три шестых, а одну треть — в две шестых."),
("girl","Посмотрите на шесть одинаковых частей. Теперь складывать удобно, ведь каждая часть одного размера!")],"mode":"pieces"},
{"title":"ШАГ 2. СКЛАДЫВАЕМ","formula":["3/6 + 2/6 = 5/6","КРЫША ПОЧТИ ЗЕЛЁНАЯ!"],"dialog":[
("girl","Три шестых плюс две шестых — пять шестых! Мы складываем числители, а знаменатель оставляем шесть."),
("robot","Тадам! На крыше уже растут растения! Это пять из шести одинаковых частей. Отличная работа, экокоманда!")],"mode":"roofdone"},
{"title":"МИССИЯ 2. ЭКОНОМИМ ВОДУ","formula":["5/6 − 1/4 = ?","НОК(6, 4) = 12"],"dialog":[
("robot","А теперь новая задача. В резервуаре было пять шестых объёма воды. Одну четвёртую объёма потратили на полив."),
("girl","Сколько осталось? Сперва найдём общий знаменатель: двенадцать. А теперь превратим обе дроби в двенадцатые!")],"mode":"water"},
{"title":"ШАГ 3. ВЫЧИТАЕМ","formula":["5/6 = 10/12   •   1/4 = 3/12","10/12 − 3/12 = 7/12"],"dialog":[
("girl","Пять шестых — это десять двенадцатых. Одна четвёртая — три двенадцатых."),
("robot","Десять минус три равно семь. Значит, осталось семь двенадцатых резервуара. Ура, мы всё вычислили!")],"mode":"waterdone"},
{"title":"ТВОЯ ОЧЕРЕДЬ!","formula":["3/4 + 1/8 = ?","ПАУЗА: ПОДУМАЙ 5 СЕКУНД"],"dialog":[
("girl","А теперь твоя очередь! Три четвёртых плюс одна восьмая. Сначала найди общий знаменатель."),
("robot","Поставь видео на паузу и реши задачу. Три четверти — это шесть восьмых. Шесть восьмых плюс одна восьмая — семь восьмых!"),
("girl","Супер! Ты настоящий математический экогерой!")],"mode":"quiz"},
{"title":"ЭКОШКОЛА СПАСЕНА!","formula":["1. ОБЩИЙ ЗНАМЕНАТЕЛЬ","2. РАВНЫЕ ДРОБИ","3. ДЕЙСТВИЕ • ПРОВЕРКА"],"dialog":[
("robot","У нас получилось! Зелёная крыша готова, воду мы рассчитали. И самое главное — разобрались с дробями."),
("girl","Запомни три шага: найди общий знаменатель, приведи дроби к нему, сложи или вычти числители. Увидимся на новой экомиссии!"),
("robot","Бип-бип! Маленькие шаги дают большие результаты!")],"mode":"final"}]

def tts():
 async def go():
  for i,s in enumerate(S):
   for j,(who,text) in enumerate(s["dialog"]):
    path=f"/tmp/eco_{i}_{j}.mp3"
    for retry in range(4):
     try:
      await edge_tts.Communicate(text,"ru-RU-SvetlanaNeural" if who=="girl" else "ru-RU-DmitryNeural",rate="+8%" if who=="girl" else "+5%",pitch="+5Hz" if who=="girl" else "-2Hz").save(path)
      if os.path.getsize(path)>1000:break
     except Exception:
      if retry==3:raise
      await asyncio.sleep(2)
 asyncio.run(go())
tts()

def ffprobe(path):
 return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path]).decode())
def wordwrap(d,s,font,maxw):
 lines=[];cur=""
 for word in s.split():
  cand=(cur+" "+word).strip()
  if d.textbbox((0,0),cand,font=font)[2]>maxw and cur:lines.append(cur);cur=word
  else:cur=cand
 if cur:lines.append(cur)
 return lines
def rrect(d,box,r,fill,outline=None,width=1):d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def girl(d,t,talking,point,blink):
 # silhouette x around 145-280, with exactly 2 arms
 bounce=4*math.sin(2.4*t)
 x,y=177,315+bounce
 # legs and shoes
 d.line((x-19,y+98,x-21,y+160),fill="#1B7043",width=18)
 d.line((x+23,y+98,x+25,y+160),fill="#1B7043",width=18)
 d.ellipse((x-47,y+150,x-3,y+169),fill="#172c38")
 d.ellipse((x+6,y+150,x+53,y+169),fill="#172c38")
 # body 
 d.polygon([(x-45,y+10),(x+45,y+10),(x+59,y+117),(x-59,y+117)],fill="#188A50")
 d.polygon([(x-40,y+6),(x+40,y+6),(x+24,y+31),(x-18,y+31)],fill="#f8fff9")
 d.line((x-43,y+35,x-43,y+112),fill="#0d6536",width=5)
 d.line((x+43,y+35,x+43,y+112),fill="#0d6536",width=5)
 # left arm at side
 d.line((x-44,y+26,x-68,y+80),fill="#F3B88B",width=15)
 d.ellipse((x-76,y+75,x-60,y+93),fill="#F3B88B")
 # right arm points to board, moving within a bounded range
 px=x+47;py=y+28
 handx=x+111 if point else x+62
 handy=y+11+6*math.sin(4*t) if point else y+89+8*math.sin(2*t)
 d.line((px,py,handx,handy),fill="#F3B88B",width=15)
 d.ellipse((handx-10,handy-10,handx+10,handy+10),fill="#F3B88B")
 # head and hair
 hx,hy=x,y-58+2*math.sin(3*t)
 d.ellipse((hx-60,hy-67,hx+60,hy+60),fill="#503421")
 d.ellipse((hx-51,hy-62,hx+51,hy+48),fill="#f5c5a0")
 d.pieslice((hx-57,hy-66,hx+52,hy+6),185,350,fill="#503421")
 d.ellipse((hx-55,hy+0,hx-32,hy+36),fill="#5B3424")
 d.ellipse((hx+31,hy+0,hx+53,hy+36),fill="#5B3424")
 # leaf-shaped hair bow
 d.ellipse((hx+25,hy-66,hx+62,hy-48),fill="#44B85A")
 d.ellipse((hx+41,hy-82,hx+60,hy-54),fill="#5DE071")
 # face
 for ex in (hx-21,hx+20):
  if blink:d.line((ex-6,hy-5,ex+6,hy-5),fill="#39201b",width=3)
  else:
   d.ellipse((ex-7,hy-13,ex+7,hy+3),fill="#251f24")
   d.ellipse((ex-4,hy-11,ex-1,hy-7),fill="white")
 d.ellipse((hx-40,hy+10,hx-23,hy+22),fill="#ee9c96")
 d.ellipse((hx+23,hy+10,hx+40,hy+22),fill="#ee9c96")
 if talking:
  op=5+int(9*abs(math.sin(t*12)))
  d.ellipse((hx-12,hy+24-op//3,hx+12,hy+24+op),fill="#843c4b")
  d.arc((hx-11,hy+23-op//3,hx+11,hy+24+op),0,180,fill="white",width=2)
 else:d.arc((hx-13,hy+18,hx+13,hy+36),0,180,fill="#8c4a45",width=3)
 # leaf insignia
 d.ellipse((x-11,y+59,x+10,y+80),fill="#D9FFBA")
 d.line((x-5,y+75,x+5,y+63),fill="#188A50",width=2)

def robot(d,t,talking,point):
 x,y=805,317+5*math.sin(t*2.8+1)
 # legs
 d.line((x-19,y+115,x-22,y+154),fill="#bfcbd7",width=14)
 d.line((x+18,y+115,x+22,y+154),fill="#bfcbd7",width=14)
 d.ellipse((x-44,y+149,x-3,y+163),fill="#367aa8")
 d.ellipse((x+4,y+149,x+45,y+163),fill="#367aa8")
 # arms (two)
 d.line((x-54,y+53,x-81,y+86),fill="#e0ebef",width=18)
 d.ellipse((x-93,y+76,x-72,y+96),fill="#2195ca")
 hand=(x+100,y+14+6*math.sin(t*3)) if point else (x+76,y+95+4*math.sin(t*3))
 d.line((x+54,y+53,*hand),fill="#e0ebef",width=18)
 d.ellipse((hand[0]-12,hand[1]-11,hand[0]+12,hand[1]+11),fill="#2195ca")
 # body
 rrect(d,(x-58,y,x+58,y+123),35,"#f2fbfd","#55a4be",4)
 d.ellipse((x-17,y+58,x+17,y+91),fill="#40B957")
 d.polygon([(x-10,y+80),(x+10,y+64),(x+3,y+85)],fill="#f9fff0")
 # head
 d.ellipse((x-74,y-104,x+74,y+15),fill="#f3fcfc",outline="#488dbe",width=5)
 rrect(d,(x-61,y-90,x+61,y-4),38,"#102b3c")
 d.ellipse((x-62,y-44,x-45,y-21),fill="#279ee5")
 d.ellipse((x+45,y-44,x+62,y-21),fill="#279ee5")
 for ex in (x-29,x+28):
  if talking:
   d.ellipse((ex-11,y-65,ex+11,y-43),fill="#6ef4ff")
  else:
   d.arc((ex-13,y-66,ex+13,y-39),185,355,fill="#6ef4ff",width=4)
 if talking:
  h=5+int(8*abs(math.sin(t*13)))
  d.ellipse((x-18,y-36-h//2,x+18,y-36+h),fill="#6bf7ff")
 else:d.arc((x-21,y-49,x+21,y-23),0,180,fill="#6bf7ff",width=4)
 d.ellipse((x-7,y-118,x+7,y-106),fill="#56c753")
 d.line((x,y-106,x,y-99),fill="#5dbe5c",width=5)

def board(d,s,t):
 # big clear board in center 
 rrect(d,(308,111,696,365),24,"#fffef8","#159362",6)
 rrect(d,(323,129,679,168),15,"#ddf8da")
 d.text((345,137),s["title"][:30],font=F(17,True),fill="#126c45")
 fields=s["formula"]
 fsz=34 if max(len(x) for x in fields)<29 else 25
 if s["mode"]=="final":fsz=21
 for j,ln in enumerate(fields):
  x=341;y=193+j*59
  # no clipping text to board
  if d.textbbox((0,0),ln,font=F(fsz,True))[2]>328:
   f=F(22,True)
  else:f=F(fsz,True)
  d.text((x,y),ln,font=f,fill="#164a44")
 if s["mode"] in ("roof","roofdone","pieces"):
  yy=320
  for k in range(6):
   fill="#4BC36D" if (s["mode"]=="roofdone" and k<5) or (s["mode"]=="pieces" and k<3) or (s["mode"]=="roof" and k<3) else "#ffffff"
   d.rectangle((348+k*50,yy,395+k*50,yy+23),fill=fill,outline="#17784a",width=2)
 if s["mode"].startswith("water"):
  d.rounded_rectangle((351,319,638,346),6,fill="#e8faff",outline="#2288c4",width=2)
  ww=237 if s["mode"]=="waterdone" else 260
  d.rounded_rectangle((354,322,354+ww,343),4,fill="#3aaae7")
 # moving leaf sparkles
 for idx,(x,y) in enumerate([(328,93),(674,93),(680,370)]):
  dd=2*math.sin(t*3+idx)
  d.ellipse((x-5,y-5+dd,x+5,y+5+dd),fill="#62cc66")

def draw_frame(s,t,who,subtitle,progress):
 im=Image.new("RGB",(W,H))
 d=ImageDraw.Draw(im)
 # sky & land
 for y in range(H):
  v=y/H
  co=(int(132+72*v),int(222+17*v),int(255-92*v)) if y<385 else (int(103-22*(v-.7)),int(196-40*(v-.7)),int(105-17*(v-.7)))
  d.line((0,y,W,y),fill=co)
 # trees with gentle foliage
 for tx in (32,920):
  d.rectangle((tx-8,185,tx+8,447),fill="#835a33")
  for ox,oy,rad in [(-26,0,59),(30,-24,68),(-19,-78,62)]:
   sway=4*math.sin(t*1.5+tx)
   d.ellipse((tx+ox-rad+sway,177+oy-rad,tx+ox+rad+sway,177+oy+rad),fill="#3da95b")
 # school silhouette
 rrect(d,(327,28,675,105),15,"#faf9eb","#7fcf8d",3)
 d.text((399,48),"ECO FRACTION LAB",font=F(29,True),fill="#16874b")
 d.ellipse((50,24,119,93),fill="#fff6b6")
 d.rectangle((0,465,W,H),fill="#e2cc95")
 for i in range(22):
  x=(i*53+17)%W; yy=461+8*math.sin(i+t)
  d.ellipse((x,yy,x+10,yy+9),fill="#dd6fb0" if i%3==0 else "#fff0a1")
 board(d,s,t)
 girl(d,t,who=="girl",point=(s["mode"] not in ("intro","final")),blink=(int(t*2.1)%9==0 and t%1<.1))
 robot(d,t,who=="robot",point=(s["mode"] not in ("intro","final")))
 # subtitle and speaker badge
 rrect(d,(50,397,910,480),18,"#fffff5","#24a15e",3)
 rrect(d,(55,382,230,413),12,"#319f5b" if who=="girl" else "#298db8")
 d.text((68,386),"ЛИЗА" if who=="girl" else "ЭКОБОТ",font=F(17,True),fill="white")
 lines=wordwrap(d,subtitle,F(20),820)
 for k,line in enumerate(lines[:3]):d.text((75,419+k*22),line,font=F(20),fill="#17452e")
 d.rectangle((0,H-8,W,H),fill="#e6f4d9")
 d.rectangle((0,H-8,int(W*progress),H),fill="#22a855")
 return im

def scene_audio(s,i):
 tracks=[]
 for j,(who,txt) in enumerate(s["dialog"]):
  p=f"/tmp/eco_{i}_{j}.mp3"
  dur=ffprobe(p)
  tracks.append((p,dur,who,txt))
 return tracks

clips=[]
for i,s in enumerate(S):
 tracks=scene_audio(s,i)
 # join audio with 0.1s silent between tracks using filter_complex
 inputs=[]
 for p,dur,_,_ in tracks:inputs+=["-i",p]
 fc="".join(f"[{j}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{j}];" for j in range(len(tracks)))
 fc+="".join(f"[a{j}]" for j in range(len(tracks)))+f"concat=n={len(tracks)}:v=0:a=1[a]"
 aud=f"/tmp/eco-scene{i}.m4a"
 subprocess.run(["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",fc,"-map","[a]","-c:a","aac","-b:a","128k",aud],check=True)
 duration=ffprobe(aud)
 starts=[];acc=0
 for _,dur,_,_ in tracks:starts.append(acc);acc+=dur
 # pipe raw pixels to ffmpeg, keep video and voice in same scene
 clip=f"/tmp/eco-scene{i}.mp4"
 proc=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0","-i",aud,"-map","0:v","-map","1:a","-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p","-c:a","copy","-t",str(duration),"-movflags","+faststart",clip],stdin=subprocess.PIPE)
 nframes=math.ceil(duration*FPS)
 for fi in range(nframes):
  t=fi/FPS
  j=len(tracks)-1
  for k,v in enumerate(starts):
   if t<v+tracks[k][1]:j=k;break
  who,txt=tracks[j][2],tracks[j][3]
  frame=draw_frame(s,t,who,txt,(i+t/max(duration,.01))/len(S))
  proc.stdin.write(frame.tobytes())
 proc.stdin.close()
 if proc.wait()!=0:raise RuntimeError("ffmpeg failed scene "+str(i))
 clips.append(clip)
 print("RENDERED",i+1,round(duration,1),flush=True)
with open("/tmp/eco_clips.txt","w") as f:
 for clip in clips:f.write(f"file '{clip}'\n")
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","/tmp/eco_clips.txt","-c","copy","-movflags","+faststart",str(VIDEO)],check=True)
# Landing video plays immediately (muted due browser audio restrictions), one tap unmutes
landing="""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ECO FRACTION LAB — мультфильм 5 класс</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;font-family:Arial,sans-serif;background:linear-gradient(130deg,#d0f9cf,#e0fff4,#a9e0f5);display:flex;align-items:center;justify-content:center;padding:18px;color:#16412e}.wrap{width:min(100%,980px);text-align:center;background:white;border-radius:24px;padding:18px;box-shadow:0 15px 45px #106a4730}h1{font-size:clamp(24px,5vw,38px);color:#11834a;margin:10px}.info{margin:6px 0 16px}video{width:100%;display:block;background:#193b43;border-radius:14px;aspect-ratio:16/9}button{background:#0f9854;color:white;border:0;border-radius:16px;font-size:20px;font-weight:800;padding:15px 30px;margin:15px auto;cursor:pointer}small{display:block;color:#536f61;margin-bottom:8px}</style></head><body><main class="wrap"><h1>🌿 ECO FRACTION LAB</h1><div class="info">Живой мультурок · Математика · 5 класс</div><video id="v" autoplay muted playsinline controls preload="auto"><source src="eco-fraction-lab-cartoon.mp4" type="video/mp4"></video><button id="sound">🔊 Включить звук и смотреть</button><small>Видео запускается автоматически без звука. Для голосов персонажей нажмите кнопку — это ограничение браузеров.</small></main><script>const v=document.getElementById('v'),b=document.getElementById('sound');v.play().catch(()=>{});b.onclick=()=>{v.muted=false;v.currentTime=0;v.play();b.textContent='🔊 Звук включён';};</script></body></html>"""
(OUT/"eco-fraction-video.html").write_text(landing,encoding="utf-8")
print("FINAL",str(VIDEO),VIDEO.stat().st_size,ffprobe(str(VIDEO)),flush=True)
