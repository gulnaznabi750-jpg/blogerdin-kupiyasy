import asyncio, os, subprocess, math, random, textwrap
from PIL import Image, ImageDraw, ImageFont
import edge_tts
W,H=1280,720
OUT="public"; os.makedirs(OUT,exist_ok=True)
VOICE="ru-RU-SvetlanaNeural"
SCENES=[
("01 / СЕКРЕТНЫЙ БРИФИНГ","ДЕЛО №016: КТО УКРАЛ МИНУС?","ОБНАРУЖЕНЫ ОШИБКИ В ВЫЧИСЛЕНИЯХ","Внимание, математические детективы! Говорит Мистер Минус. В нашем бюро чрезвычайное происшествие. Искусственный интеллект прислал подозрительные решения. Где-то исчезают знаки, а ответы перестали совпадать с правилами математики. Ваша задача: внимательно изучить улики, восстановить каждый неверный шаг и доказать правильный ответ. Открываем дело номер ноль шестнадцать!"),
("02 / ДОСЬЕ НА ЗНАКИ","ПРАВИЛО ПЕРВОЕ: ЗНАКИ","(−) : (+) = (−)     (+) : (−) = (−)","Прежде чем расследовать дело, вспомним секретные правила. При делении рациональных чисел с разными знаками результат отрицательный. Например: минус двадцать четыре разделить на плюс шесть — минус четыре. Если знаки одинаковые, результат положительный. Минус двадцать четыре разделить на минус шесть — плюс четыре. Главное — сначала определить знак, а затем разделить модули чисел."),
("03 / УЛИКА № 1 — ОШИБКА ИИ","РАЗОБЛАЧЕНИЕ НЕВЕРНОГО ОТВЕТА","(−24) : (−6) = −4   НЕВЕРНО!   +4","Первая улика. Искусственный интеллект утверждает: минус двадцать четыре разделить на минус шесть равно минус четыре. Согласны? Нет! Два отрицательных числа при делении дают положительное число. Двадцать четыре разделить на шесть равно четыре. Вердикт детективов: правильный ответ плюс четыре. Не доверяйте ответу без доказательства!"),
("04 / УЛИКА № 2 — СКРЫТЫЙ ЗНАК","ПРОВЕРЬ ЦЕПОЧКУ ДЕЙСТВИЙ","(−48) : (+6) − (−3) · (−2)","Следующая улика сложнее. Сначала вычислим минус сорок восемь разделить на плюс шесть. Получится минус восемь. Затем минус три умножить на минус два — плюс шесть. Поэтому всё выражение равно минус восемь минус шесть. Итог: минус четырнадцать. Ошибка была в знаке произведения, из-за которого получался ложный ответ минус два."),
("05 / УЛИКА № 3 — ПРОВЕРКА","ПОЛОЖИТЕЛЬНЫЙ ИЛИ ОТРИЦАТЕЛЬНЫЙ?","(−35) : (+7) = −5     (−42) : (−6) = +7","Проверим ещё два доказательства. Минус тридцать пять разделить на плюс семь: разные знаки, ответ минус пять. А минус сорок два разделить на минус шесть: одинаковые знаки, ответ плюс семь. Запомните: знак результата определяется правилами, а не догадкой. У каждого ответа должно быть математическое объяснение."),
("06 / ФИНАЛЬНЫЙ СЕЙФ","ВВЕДИ СЕКРЕТНЫЙ КОД","(−36) : (−9) = ?","Время открыть финальный сейф! Перед вами последнее вычисление: минус тридцать шесть разделить на минус девять. Остановите видео и подумайте. Какой знак будет у результата? Делим два отрицательных числа, значит получаем положительный ответ. Тридцать шесть разделить на девять — четыре. Секретный код — четыре. Сейф открыт!"),
("07 / ДЕЛО ЗАКРЫТО","МИСТЕР МИНУС РАСКРЫЛ ТАЙНУ","РАЗНЫЕ ЗНАКИ → МИНУС   •   ОДИНАКОВЫЕ → ПЛЮС","Поздравляю, детективы! Мы нашли причину исчезнувших знаков и доказали, какие ответы были неверными. Сегодня вы не просто делили рациональные числа. Вы проверяли утверждения искусственного интеллекта, находили ошибки и обосновывали свои выводы. Помните девиз Мистера Минуса: не доверяйте ответу без доказательства, проверяйте каждый знак! Дело номер ноль шестнадцать закрыто!")
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
            pix[x,y]=(int(29+38*t+12*v),int(21+22*t+10*v),int(16+12*t+7*v))
    d=ImageDraw.Draw(im,"RGBA")
    random.seed(i*47+phase)
    for k in range(34):
        x=random.randrange(W);y=random.randrange(H);r=random.randint(3,17)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(230,171,90,random.randint(20,65)))
    d.rounded_rectangle((54,48,W-54,H-48),radius=34,fill=(34,23,16,230),outline=(189,140,77,255),width=4)
    d.rounded_rectangle((80,75,W-80,130),radius=22,fill=(128,45,37,210))
    d.text((112,89),SCENES[i][0],font=font(22),fill="white")
    d.text((95,170),SCENES[i][1],font=font(43),fill="#f5e6c3",stroke_width=1)
    value=SCENES[i][2]
    numfont=font(42 if len(value)<48 else 30)
    for j,line in enumerate(lines(d,value,numfont,1050)):
        d.text((106,305+j*61),line,font=numfont,fill="#edbc71")
    if i==0:
        d.text((108,455),"6 КЛАСС • ДЕЛЕНИЕ РАЦИОНАЛЬНЫХ ЧИСЕЛ",font=font(28),fill="#f4d29b")
    elif i==5 and phase>0:
        d.text((108,475),"СЕКРЕТНЫЙ КОД: +4",font=font(34),fill="#f7d58b")
    elif i==6:
        d.text((108,505),"МИСТЕР МИНУС: ДЕЛО РАСКРЫТО",font=font(23,False),fill="#e5cda1")
    else:
        d.text((108,510),"МАТЕМАТИЧЕСКОЕ БЮРО  ✦  ПРОВЕРЬ КАЖДЫЙ ЗНАК",font=font(25),fill="#e5cda1")
    d.rounded_rectangle((100,615,1180,630),radius=7,fill=(255,255,255,55))
    d.rounded_rectangle((100,615,100+int(1080*((i+1)/7)),630),radius=7,fill="#c99d5d")
    d.text((104,649),"ДЕЛО №016: КТО УКРАЛ МИНУС?  |  6 КЛАСС",font=font(16),fill="#f1ddbc")
    return im.convert("RGB")
async def speech():
    for i,scene in enumerate(SCENES):
        target=f"/tmp/voice{i}.mp3"
        if os.path.exists(target):continue
        for attempt in range(3):
            try:
                await edge_tts.Communicate(scene[3],VOICE,rate="+2%").save(target)
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
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","/tmp/clips.txt","-c","copy","-movflags","+faststart",OUT+"/delo-016-kto-ukral-minus-6klass.mp4"],check=True)
page="""<!doctype html><html lang="kk"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Дело №016 — Кто украл минус?</title><style>body{margin:0;background:linear-gradient(130deg,#231345,#693273,#0e6979);color:white;font-family:Arial,sans-serif;min-height:100vh;display:grid;place-items:center}main{width:min(95vw,1000px);text-align:center}h1{font-size:clamp(29px,5vw,55px);margin-bottom:8px}p{font-size:18px}video{width:100%;border:4px solid white;border-radius:20px;box-shadow:0 20px 60px #0005}a{color:white;font-weight:bold}small{opacity:.85}</style><main><h1>🕵 Дело №016. Кто украл минус?</h1><p>6 класс · Деление рациональных чисел · Русская озвучка</p><video controls playsinline preload="metadata"><source src="delo-016-kto-ukral-minus-6klass.mp4" type="video/mp4">Ваш браузер не поддерживает видео.</video><p><a href="delo-016-kto-ukral-minus-6klass.mp4">Скачать видеоролик</a></p><small>Математическое расследование · Мистер Минус</small></main></html>"""
open(OUT+"/delo-016-video.html","w").write(page)
print("OUTPUT",os.path.getsize(OUT+"/delo-016-kto-ukral-minus-6klass.mp4"),sum(duration(f"/tmp/voice{i}.mp3")+1 for i in range(7)))
