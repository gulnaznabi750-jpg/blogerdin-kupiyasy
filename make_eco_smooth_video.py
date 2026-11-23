import asyncio, math, os, subprocess, wave, io, random, time, re
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import numpy as np
from pathlib import Path

OUT=Path("public")
OUT.mkdir(exist_ok=True)
VIDEO=OUT/"eco-fraction-lab-smooth-lesson.mp4"
W,H,FPS=1280,720,18
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
 from gtts import gTTS
 async def go():
  for i,s in enumerate(S):
   for j,(who,dialog) in enumerate(s["dialog"]):
    path=f"/tmp/eco_{i}_{j}.mp3"
    try:
     await asyncio.to_thread(gTTS(text=dialog,lang="ru").save,path)
     if os.path.getsize(path)<1000:raise RuntimeError("TTS output empty")
    except Exception as first:
     print("Google TTS failed, retrying Microsoft:",str(first)[:180],flush=True)
     await edge_tts.Communicate(dialog,"ru-RU-SvetlanaNeural" if who=="girl" else "ru-RU-DmitryNeural").save(path)
    if who=="robot":
     deep=path+".deep.mp3"
     subprocess.run(["ffmpeg","-y","-loglevel","error","-i",path,"-af","asetrate=44100*0.92,aresample=44100","-codec:a","libmp3lame","-q:a","4",deep],check=True)
     os.replace(deep,path)
    print("VOICE",i,j,os.path.getsize(path),flush=True)
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


# Animated storyboard frames derived from the user's chosen cute characters
import base64,re
clip_bytes=base64.b64decode(Path("eco_motion_base64.txt").read_text().strip())
Path("/tmp/eco_actors_clip.mp4").write_bytes(clip_bytes)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","/tmp/eco_actors_clip.mp4","-vsync","0","/tmp/eco_actor_%02d.png"],check=True)
ACTORS=[Image.open(f"/tmp/eco_actor_{k:02d}.png").convert("RGB") for k in range(1,9)]
def fraction_text(draw,s,x,y,size=32,color="#136244"):
 # Render mathematical fractions with genuine horizontal fraction bars
 parts=re.split(r'(\d+/\d+)',s)
 cur=x
 for p in parts:
  if not p:continue
  if re.fullmatch(r'\d+/\d+',p):
   num,den=p.split("/")
   f=F(size,True); width=max(draw.textbbox((0,0),v,font=f)[2] for v in (num,den))+12
   draw.text((cur+(width-draw.textbbox((0,0),num,font=f)[2])/2,y-14),num,font=f,fill=color)
   draw.line((cur+3,y+26,cur+width-3,y+26),fill=color,width=3)
   draw.text((cur+(width-draw.textbbox((0,0),den,font=f)[2])/2,y+31),den,font=f,fill=color)
   cur+=width+9
  else:
   f=F(size-5,True); draw.text((cur,y+12),p,font=f,fill=color)
   cur+=draw.textbbox((0,0),p,font=f)[2]+4

# One stable illustrated pose avoids the old 8-frame snapping loop.
# All movements below are continuous functions of time.
CHAR_BASE=ACTORS[0].resize((440,440),Image.Resampling.LANCZOS)
from PIL import ImageFilter, ImageEnhance
CHAR_BASE=ImageEnhance.Sharpness(CHAR_BASE).enhance(1.35)

def fractions(draw,txt,x,y,size=37,color="#1c634e",maxw=624):
 # horizontally barred fractions and mathematically correct readable notation
 parts=re.split(r'(\d+/\d+)',txt)
 for frag in parts:
  if not frag:continue
  if re.fullmatch(r'\d+/\d+',frag):
   up,down=frag.split('/')
   ff=F(size,True)
   ww=max(draw.textbbox((0,0),piece,font=ff)[2] for piece in (up,down))+18
   draw.text((x+(ww-draw.textbbox((0,0),up,font=ff)[2])/2,y-12),up,font=ff,fill=color)
   draw.line((x+5,y+27,x+ww-5,y+27),fill=color,width=4)
   draw.text((x+(ww-draw.textbbox((0,0),down,font=ff)[2])/2,y+31),down,font=ff,fill=color)
   x+=ww+12
  else:
   ff=F(size-8,True)
   draw.text((x,y+14),frag,font=ff,fill=color)
   x+=draw.textbbox((0,0),frag,font=ff)[2]+2

def draw_frame(s,t,who,subtitle,progress):
 im=Image.new("RGB",(W,H))
 d=ImageDraw.Draw(im)
 # crisp, stable 720p background with a subtle color gradient
 for y in range(H):
  k=y/H
  d.line((0,y,W,y),fill=(int(231-27*k),int(251-10*k),int(239-31*k)))
 # sun, plant shapes, small details move independently, not the camera
 d.ellipse((1140,38,1244,142),fill="#ffefaa")
 for x,phase in [(35,0.0),(1190,2.3),(1220,1.3)]:
  d.line((x,180,x,540),fill="#8c794d",width=13)
  for n in range(3):
   yy=185+n*65
   dx=4*math.sin(.7*t+phase+n)
   d.ellipse((x-65+dx,yy-48,x+65+dx,yy+35),fill="#73d38d",outline="#50ab6b",width=2)
 # title banner
 d.rounded_rectangle((35,26,1245,103),25,fill="#138456")
 d.text((66,43),"ECO FRACTION LAB",font=F(43,True),fill="#fffce9")
 d.text((890,55),"МАТЕМАТИКА · 5 КЛАСС",font=F(22,True),fill="#d9ffeb")
 # original illustrated duo, always same anatomy; gentle 1-2-pixel bob
 d.rounded_rectangle((34,126,530,565),26,fill="#ffffff",outline="#79c989",width=4)
 top=131+int(round(1.7*math.sin(t*1.3)))
 xpos=62+int(round(1.2*math.sin(t*.9+.5)))
 im.paste(CHAR_BASE,(xpos,top))
 d=ImageDraw.Draw(im)
 # very small lip motion, only while speaking; independently driven, no pose swap
 a=abs(math.sin(t*8.5))
 if who=="girl":
  mx,my=xpos+144,top+207
  # subtly moving mouth inside girl's face
  d.ellipse((mx-7,my-1,mx+7,my+2+int(5*a)),fill="#9b4d57")
 elif who=="robot":
  mx,my=xpos+348,top+243
  d.rounded_rectangle((mx-13,my-9,mx+13,my+5),7,fill="#112938")
  d.arc((mx-13,my-7,mx+13,my+9+int(5*a)),0,180,fill="#6eeafa",width=3)
 # soft character name label, stable badge
 d.rounded_rectangle((64,520,505,557),16,fill="#f2fff4",outline="#a4e0b2",width=2)
 label="🌱 ЛИЗА ГОВОРИТ" if who=="girl" else "🤖 ЭКОБОТ ГОВОРИТ"
 # emoji fallback fonts can fail on Linux; draw plain Cyrillic
 d.text((94,528),"ЛИЗА ГОВОРИТ" if who=="girl" else "ЭКОБОТ ГОВОРИТ",font=F(21,True),fill="#157548")
 # mathematical board stays perfectly stable
 d.rounded_rectangle((554,127,1245,568),28,fill="#fffef9",outline="#41ac73",width=5)
 d.rounded_rectangle((578,146,1219,209),17,fill="#e2f6e5")
 title=s["title"]
 title_font=F(29 if len(title)<35 else 23,True)
 d.text((594,164),title,font=title_font,fill="#187a4e")
 mode=s["mode"]
 parts=s["formula"]
 y0=235
 for line_i,mathline in enumerate(parts[:3]):
  yy=y0+line_i*95
  if re.search(r'\d+/\d+',mathline):
   sz=36 if len(mathline)<27 else 28
   fractions(d,mathline,590,yy,sz)
  else:
   fs=33 if len(mathline)<23 else 25
   for z,line in enumerate(wordwrap(d,mathline,F(fs,True),615)[:2]):
    d.text((598,yy+24+z*38),line,font=F(fs,True),fill="#206a50")
 if mode in ("roof","pieces","roofdone"):
  # physically meaningful six equal-sized sections, filled in gradually
  fulln=3 if mode in ("roof","pieces") else 5
  fillpart=min(1,max(0,(t-0.8)/5.5))
  d.text((597,449),"6 одинаковых частей",font=F(22,True),fill="#567a61")
  for k in range(6):
   x=596+k*99
   if k<fulln and fillpart>k/max(fulln,1)*.5:
    fill="#56c779"
   else:fill="#f5fff6"
   d.rounded_rectangle((x,485,x+88,536),11,fill=fill,outline="#338f59",width=3)
 if mode.startswith("water"):
  d.text((595,441),"Запас воды в резервуаре",font=F(22,True),fill="#3d739d")
  d.rounded_rectangle((595,480,1200,527),13,fill="#e4f6ff",outline="#3d9bca",width=3)
  p=7/12 if mode=="waterdone" else 5/6
  frac=max(.01,min(1,(t-0.5)/2))
  d.rounded_rectangle((598,483,598+int(595*p*frac),524),10,fill="#4cb5e1")
 if mode in ("intro","final"):
  # leaf confetti moves slowly and consistently with no character jerk
  for n in range(11):
   xx=579+(n*59)%629
   yy=447+int(18*math.sin(t*.8+n))
   d.ellipse((xx-9,yy-4,xx+9,yy+4),fill="#8bd985")
 if mode=="quiz":
  # visual thinking countdown, no noisy overlays
  secs=int(max(0,5-((t-1)%7)))
  d.rounded_rectangle((982,463,1205,533),16,fill="#fff2b1",outline="#f3c351",width=3)
  d.text((1010,477),"ПОДУМАЙ!",font=F(22,True),fill="#8c6534")
 # captions at readable 2-line size
 d.rounded_rectangle((34,584,1246,691),22,fill="#ffffff",outline="#55bf83",width=4)
 words=wordwrap(d,subtitle,F(27),1153)
 for k,line in enumerate(words[:3]):
  d.text((66,601+k*32),line,font=F(27),fill="#1b5042")
 # film progress line
 d.rounded_rectangle((45,699,1235,709),4,fill="#d4ecd8")
 d.rounded_rectangle((45,699,45+int(1190*progress),709),4,fill="#1ba96a")
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
landing="""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ECO FRACTION LAB — мультфильм 5 класс</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;font-family:Arial,sans-serif;background:linear-gradient(130deg,#d0f9cf,#e0fff4,#a9e0f5);display:flex;align-items:center;justify-content:center;padding:18px;color:#16412e}.wrap{width:min(100%,980px);text-align:center;background:white;border-radius:24px;padding:18px;box-shadow:0 15px 45px #106a4730}h1{font-size:clamp(24px,5vw,38px);color:#11834a;margin:10px}.info{margin:6px 0 16px}video{width:100%;display:block;background:#193b43;border-radius:14px;aspect-ratio:16/9}button{background:#0f9854;color:white;border:0;border-radius:16px;font-size:20px;font-weight:800;padding:15px 30px;margin:15px auto;cursor:pointer}small{display:block;color:#536f61;margin-bottom:8px}</style></head><body><main class="wrap"><h1>🌿 ECO FRACTION LAB</h1><div class="info">Мультурок с Лизой и ЭкоБотом · Математика · 5 класс</div><video id="v" autoplay muted playsinline controls preload="auto"><source src="eco-fraction-lab-smooth-lesson.mp4" type="video/mp4"></video><button id="sound">🔊 Включить звук и смотреть</button><small>Видео запускается автоматически без звука. Для голосов персонажей нажмите кнопку — это ограничение браузеров.</small></main><script>const v=document.getElementById('v'),b=document.getElementById('sound');v.play().catch(()=>{});b.onclick=()=>{v.muted=false;v.currentTime=0;v.play();b.textContent='🔊 Звук включён';};</script></body></html>"""
(OUT/"eco-fraction-smooth-video.html").write_text(landing,encoding="utf-8")
print("FINAL",str(VIDEO),VIDEO.stat().st_size,ffprobe(str(VIDEO)),flush=True)
