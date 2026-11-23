import asyncio, os, subprocess, math, random, textwrap
from PIL import Image, ImageDraw, ImageFont
import edge_tts
W,H=1280,720
OUT="public"; os.makedirs(OUT,exist_ok=True)
VOICE="kk-KZ-AigulNeural"
SCENES=[
("01 / КІРІСПЕ — ЖҰМБАҚ ОҚИҒА","БЛОГЕРДІҢ ҚҰПИЯСЫ","100 → 200 → 400 ...","Сендер әлеуметтік желіде танымал блогерлерді көріп жүрсіңдер ме? Кейбір блогерлердің жазылушылары күн сайын көбейіп отырады. Бірақ олардың саны қалай өсетінін математикалық тұрғыдан түсіндіруге бола ма? Бүгін біз бір блогердің құпиясын ашамыз. Оның жетістігінің артында қандай математикалық заңдылық жатқанын бірге анықтайық!"),
("02 / ҚҰПИЯ ТІЗБЕК","ЖАЗЫЛУШЫЛАРДЫҢ ӨСУІ","100  →  200  →  400  →  800  →  1600","Блогердің парақшасында алғашқы кезеңде 100 жазылушы болды. Келесі кезеңде олардың саны 200-ге жетті. Одан кейін 400, 800 және 1600 болды. Назар аударыңдар! Бұл сандардың арасында қандай заңдылық бар? Әрбір келесі сан алдыңғы саннан екі есе үлкен. Демек, біз әр жолы бірдей санды қосып отырған жоқпыз, алдыңғы санды екіге көбейтіп отырмыз. Міне, біздің алғашқы құпиямыз осы!"),
("03 / ГЕОМЕТРИЯЛЫҚ ПРОГРЕССИЯ","ЕСЕЛІКТІ ТАП!","200 : 100 = 2     400 : 200 = 2     800 : 400 = 2","Математикада осындай тізбек геометриялық прогрессия деп аталады. Геометриялық прогрессия дегеніміз — екінші мүшесінен бастап әрбір мүшесі алдыңғы мүшесін нөлден өзгеше бір тұрақты санға көбейту арқылы алынатын тізбек. Бұл тұрақты сан прогрессияның еселігі деп аталады және q әрпімен белгіленеді. Біздің мысалымызда q тең 200 бөлінген 100, яғни екі. Демек, блогердің жазылушыларының өсу моделіндегі геометриялық прогрессияның еселігі екіге тең."),
("04 / ФОРМУЛАНЫҢ ҚҰПИЯСЫ","n-ШІ МҮШЕНІҢ ФОРМУЛАСЫ","bₙ = b₁ · qⁿ⁻¹","Ал енді геометриялық прогрессияның кез келген мүшесін қалай табамыз? Ол үшін энші мүшенің формуласын қолданамыз. Бэ бір — прогрессияның алғашқы мүшесі. Ку — прогрессияның еселігі. Эн — бізге қажет мүшенің реттік нөмірі. Ал эн минус бір — дәреженің көрсеткіші. Бұл формула бізге тізбектің кез келген мүшесін табуға мүмкіндік береді. Енді оны нақты есепте қолданып көрейік."),
("05 / МАТЕМАТИКАЛЫҚ ЕСЕП","5-КЕЗЕҢДЕ ҚАНША ЖАЗЫЛУШЫ?","b₅ = 100 · 2⁴ = 100 · 16 = 1600","Бізге не белгілі? Алғашқы мүшесі бэ бір жүзге тең. Еселігі ку екіге тең. Ал біз бесінші мүшені табуымыз керек. Сондықтан эн бес. Формулаға мәндерді қоямыз: бэ бес тең жүз көбейтілген екінің төртінші дәрежесі. Екі санының төртінші дәрежесі он алты. Жүзді он алтыға көбейтсек, мың алты жүз шығады. Демек, бесінші кезеңде блогердің жазылушылар саны мың алты жүзге тең болады!"),
("06 / СЕНІҢ КЕЗЕГІҢ","ӨЗІҢ ЕСЕПТЕ!","b₁ = 50     q = 3     b₃ = ?","Енді сендердің кезектерің! Блогердің алғашқы жазылушылары елу. Әр кезең сайын олардың саны үш есе артады. Үшінші кезеңдегі жазылушылар санын табыңдар. Ойланып көріңдер! Дұрыс жауап: бэ үш тең елу көбейтілген үштің екінші дәрежесі, яғни елу көбейтілген тоғыз. Бұл төрт жүз елу!"),
("07 / ҚОРЫТЫНДЫ","ҚҰПИЯ АШЫЛДЫ!","МАТЕМАТИКА — ЗАҢДЫЛЫҚТАРДЫ АШАТЫН ҒЫЛЫМ!","Сонымен, біз бүгін блогердің құпиясын аштық! Жазылушылар санының шартты түрде екі есе өсуі геометриялық прогрессия арқылы модельденеді. Біз геометриялық прогрессияның еселігін анықтауды, энші мүшесінің формуласын қолдануды және практикалық есептер шығаруды үйрендік. Есте сақтаңдар: математика тек сандар мен формулалардан тұрмайды. Ол — күнделікті өмірдегі құбылыстарды түсіндіруге көмектесетін ғылым. Ал сен өз өміріңде қандай математикалық заңдылықтарды байқайсың? Келесі кездескенше!")
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(sz,b=True):return ImageFont.truetype(BOLD if b else FONT,sz)
def lines(draw,s,f,maxw):
    words=s.split(); lines=[]; part=""
    for w in words:
        cand=(part+" "+w).strip()
        if draw.textbbox((0,0),cand,font=f)[2]>maxw and part:lines.append(part);part=w
        else:part=cand
    if part:lines.append(part)
    return lines
def frame(i,phase):
    im=Image.new("RGB",(W,H))
    pix=im.load()
    for y in range(H):
        for x in range(W):
            t=x/W;v=y/H
            pix[x,y]=(int(42+75*t+20*v),int(27+14*t+18*v),int(96+45*t+25*v))
    d=ImageDraw.Draw(im,"RGBA")
    random.seed(i*47+phase)
    for k in range(34):
        x=random.randrange(W);y=random.randrange(H);r=random.randint(3,17)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,170,240,random.randint(20,75)))
    d.rounded_rectangle((54,48,W-54,H-48),radius=34,fill=(14,12,43,215),outline=(182,113,240,255),width=4)
    d.rounded_rectangle((80,75,W-80,130),radius=22,fill=(208,66,161,210))
    d.text((112,89),SCENES[i][0],font=font(22),fill="white")
    d.text((95,170),SCENES[i][1],font=font(43),fill="#fff4fd",stroke_width=1)
    value=SCENES[i][2]
    numfont=font(42 if len(value)<48 else 30)
    for j,line in enumerate(lines(d,value,numfont,1050)):
        d.text((106,305+j*61),line,font=numfont,fill="#69f3ed")
    if i==0:
        d.text((108,455),"9-СЫНЫП • ГЕОМЕТРИЯЛЫҚ ПРОГРЕССИЯ",font=font(28),fill="#ffd874")
    elif i==5 and phase>0:
        d.text((108,475),"ЖАУАП: b₃ = 50 · 3² = 450",font=font(34),fill="#ffdc69")
    elif i==6:
        d.text((108,505),"Жазылушылар саны — шартты математикалық модель",font=font(23,False),fill="#ffe1f1")
    else:
        d.text((108,510),"#MathBlogger  ✦  Геометриялық прогрессия",font=font(25),fill="#ffe1f1")
    d.rounded_rectangle((100,615,1180,630),radius=7,fill=(255,255,255,55))
    d.rounded_rectangle((100,615,100+int(1080*((i+1)/7)),630),radius=7,fill="#ff72c0")
    d.text((104,649),"БЛОГЕРДІҢ ҚҰПИЯСЫ  |  9-СЫНЫП",font=font(16),fill="#e5d7ed")
    return im.convert("RGB")
async def speech():
    for i,scene in enumerate(SCENES):
        target=f"/tmp/voice{i}.mp3"
        if os.path.exists(target):continue
        for attempt in range(3):
            try:
                await edge_tts.Communicate(scene[3],VOICE,rate="+7%").save(target)
                if os.path.getsize(target)>1000:break
            except Exception as exc:
                if attempt==2:raise
                await asyncio.sleep(3)
asyncio.run(speech())
def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path]).decode().strip())
clips=[]
for i in range(len(SCENES)):
    voice=f"/tmp/voice{i}.mp3";dur=duration(voice)+1.0
    slides=[]
    for j in range(2):
        img=frame(i,j)
        path=f"/tmp/frame{i}_{j}.jpg";img.save(path,quality=88);slides.append(path)
    # two short moving segments per narration; optional early answer reveal
    flist=f"/tmp/scene{i}.txt"
    with open(flist,"w") as f:
        f.write(f"file '{slides[0]}'\nduration {dur*.70:.3f}\nfile '{slides[1]}'\nduration {dur*.30:.3f}\nfile '{slides[1]}'\n")
    clip=f"/tmp/scene{i}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",flist,"-i",voice,"-vf","fps=12,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-b:a","112k","-t",str(dur),"-movflags","+faststart",clip],check=True)
    clips.append(clip)
with open("/tmp/clips.txt","w") as f:
    for clip in clips:f.write(f"file '{clip}'\n")
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","/tmp/clips.txt","-c","copy","-movflags","+faststart",OUT+"/blogerdin-kupiyasy-9synyp.mp4"],check=True)
page="""<!doctype html><html lang="kk"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Блогердің құпиясы — бейнеролик</title><style>body{margin:0;background:linear-gradient(130deg,#231345,#693273,#0e6979);color:white;font-family:Arial,sans-serif;min-height:100vh;display:grid;place-items:center}main{width:min(95vw,1000px);text-align:center}h1{font-size:clamp(29px,5vw,55px);margin-bottom:8px}p{font-size:18px}video{width:100%;border:4px solid white;border-radius:20px;box-shadow:0 20px 60px #0005}a{color:white;font-weight:bold}small{opacity:.85}</style><main><h1>🎬 Блогердің құпиясы</h1><p>9-сынып · Геометриялық прогрессия · Қазақша дыбыстау</p><video controls playsinline preload="metadata"><source src="blogerdin-kupiyasy-9synyp.mp4" type="video/mp4">Браузер бейнені қолдамайды.</video><p><a href="blogerdin-kupiyasy-9synyp.mp4">Бейнероликті жүктеу</a></p><small>Оқу мақсатындағы шартты математикалық модель</small></main></html>"""
open(OUT+"/video.html","w").write(page)
print("OUTPUT",os.path.getsize(OUT+"/blogerdin-kupiyasy-9synyp.mp4"),sum(duration(f"/tmp/voice{i}.mp3")+1 for i in range(7)))
