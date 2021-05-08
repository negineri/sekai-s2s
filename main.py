from PIL import Image
import pyocr
import sys
import discord
import os
import requests
import random
from typing import Optional

class ScoreResult:
    def __init__(self):
        self.title = ""
        self.difficulty = ""
        self.perfect = 0
        self.great = 0
        self.good = 0
        self.bad = 0
        self.miss = 0

def ocr_scoreresult(im: Image.Image) -> Optional[ScoreResult]:
    if im.height/im.width > 0.5625:
        h = int(im.width*0.5625)
        w = im.width
        im_crop = im.crop((0,int((im.height-h)/2),w,int((im.height-h)/2)+h))
        im_title = im.crop((0,0,w,h))
        im_difficulty = im_title.crop((int(w*0.091),int(h*0.077),int(w*0.175),int(h*0.117))).convert("L").point(lambda _: 0 if _ > 200 else 1,mode="1")
        im_title = im_title.crop((int(w*0.081),0,int(w*0.5),int(h*0.066))).convert("L").point(lambda _: 0 if _ > 180 else 1,mode="1")
    else:
        w = int(im.height*16/9)
        h = im.height
        im_crop = im.crop((int((im.width-w)/2),0,int((im.width-w)/2)+w,h))
        im_difficulty = im_crop.crop((int(w*0.091),int(h*0.077),int(w*0.175),int(h*0.117))).convert("L").point(lambda _: 0 if _ > 200 else 1,mode="1")
        im_title = im_crop.crop((int(w*0.081),0,int(w*0.5),int(h*0.066))).convert("L").point(lambda _: 0 if _ > 180 else 1,mode="1")
    im_score = im_crop.crop((int(w*0.041),int(h*0.622),int(w*0.526),int(h*0.964)))
    im_perfect = im_score.crop((int(im_score.width*0.859),int(im_score.height*0.249),int(im_score.width*0.978),int(im_score.height*0.389))).convert('1', dither=Image.NONE).point(lambda _: 1 if _ == 0 else 0)
    im_great = im_score.crop((int(im_score.width*0.859),int(im_score.height*0.389),int(im_score.width*0.978),int(im_score.height*0.532))).convert('1', dither=Image.NONE).point(lambda _: 1 if _ == 0 else 0)
    im_good = im_score.crop((int(im_score.width*0.859),int(im_score.height*0.532),int(im_score.width*0.978),int(im_score.height*0.675))).convert('1', dither=Image.NONE).point(lambda _: 1 if _ == 0 else 0)
    im_bad = im_score.crop((int(im_score.width*0.859),int(im_score.height*0.675),int(im_score.width*0.978),int(im_score.height*0.818))).convert('1', dither=Image.NONE).point(lambda _: 1 if _ == 0 else 0)
    im_miss = im_score.crop((int(im_score.width*0.859),int(im_score.height*0.818),int(im_score.width*0.978),int(im_score.height*0.958))).convert('1', dither=Image.NONE).point(lambda _: 1 if _ == 0 else 0)
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    tool = tools[0]
    title = tool.image_to_string(im_title,lang="jpn",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    difficulty = tool.image_to_string(im_difficulty,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    perfect = tool.image_to_string(im_perfect,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    great = tool.image_to_string(im_great,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    good = tool.image_to_string(im_good,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    bad = tool.image_to_string(im_bad,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    miss = tool.image_to_string(im_miss,lang="eng",builder=pyocr.builders.TextBuilder(tesseract_layout=7))
    result = ScoreResult()
    result.title = title
    if not difficulty in ["EASY", "NORMAL", "HARD", "EXPERT", "MASTER"]: return None
    result.difficulty = difficulty
    if not perfect.isdecimal(): return None
    result.perfect = int(perfect)
    if not great.isdecimal(): return None
    result.great = int(great)
    if not good.isdecimal(): return None
    result.good = int(good)
    if not bad.isdecimal(): return None
    result.bad = int(bad)
    if not miss.isdecimal(): return None
    result.miss = int(miss)
    return result

TOKEN = os.environ['DISCORD_BOT_TOKEN']
client = discord.Client()
os.makedirs("tmp", exist_ok=True)

@client.event
async def on_message(message):
    if not message.attachments: return
    if message.channel.id != 762898538572677140: return
    if os.path.splitext(message.attachments[0].url)[1] == '.jpg' or os.path.splitext(message.attachments[0].url)[1] == '.png':
        try:
            file_data = requests.get(message.attachments[0].url)
        except requests.exceptions.RequestException as err:
            print(err)
            return False
        file_path = 'tmp/' + str(int(random.random()*10000000000)) + os.path.splitext(message.attachments[0].url)[1]
        with open(file_path, mode='wb') as f:
            f.write(file_data.content)
        result = ocr_scoreresult(Image.open(file_path))
        os.remove(file_path)
        if result is None: return
        channel = client.get_channel(762898538572677140)
        text = f"{result.title} {result.difficulty}"
        text += f"\nPERFECT {format(result.perfect, '04')}"
        text += f"\nGREAT   {format(result.great, '04')}"
        text += f"\nGOOD    {format(result.good, '04')}"
        text += f"\nBAD     {format(result.bad, '04')}"
        text += f"\nMISS    {format(result.miss, '04')}"
        await channel.send(text)



client.run(TOKEN)
#im = Image.open('data/src/image1.jpg')
#ocr_scoreresult(im)