import discord
import os
import requests
import random

import ocr_result

TOKEN = os.environ['DISCORD_BOT_TOKEN']
client = discord.Client()
os.makedirs("tmp", exist_ok=True)


@client.event
async def on_message(message):
    if not message.attachments:
        return
    if message.channel.id != 762898538572677140:
        return
    if os.path.splitext(message.attachments[0].url)[1] == '.jpg' or os.path.splitext(message.attachments[0].url)[1] == '.png':
        try:
            file_data = requests.get(message.attachments[0].url)
        except requests.exceptions.RequestException as err:
            print(err)
            return False
        file_path = 'tmp/' + str(int(random.random() * 10000000000)) + os.path.splitext(message.attachments[0].url)[1]
        with open(file_path, mode='wb') as f:
            f.write(file_data.content)
        result = ocr_result.loadfile(file_path)
        os.remove(file_path)
        if result is None:
            return
        channel = client.get_channel(762898538572677140)
        text = f"{result.title} {result.difficulty}"
        text += f"\nPERFECT {format(result.perfect, '04')}"
        text += f"\nGREAT   {format(result.great, '04')}"
        text += f"\nGOOD    {format(result.good, '04')}"
        text += f"\nBAD     {format(result.bad, '04')}"
        text += f"\nMISS    {format(result.miss, '04')}"
        await channel.send(text)


client.run(TOKEN)
