import os
import random
from time import sleep
import pickle
import user
import config

import discord
from discord.ext.tasks import loop
from youtube_dl import YoutubeDL

f = open("token", "r")

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        user_files = os.listdir(config.user_save_dir)
        for user_i in user_files:
            user_file = open(config.user_save_dir + "/" + user_i, "rb")
            user.users[int(user_i)] = pickle.load(user_file)
        client.join_vc.start()
    async def on_message(self, message):
        if message.author.id == 964331688832417802 or  message.channel.id in config.banned_channels or message.author.bot:
            return
        if "newjersey" in message.content.lower().replace(" ",""):
            c_user = user.get_user(message.author.id)
            c_user.new_jersey_count += 1
            c_user.save()
            if c_user.new_jersey_count % 100 == 0:
                spam_channel = await client.fetch_channel(config.spam_channel_id)
                await spam_channel.send("<@" + str(message.author.id) + "> has said new jersey " + str(c_user.new_jersey_count) + " times!")
            if "good" in message.content:
                if random.randrange(config.chance2) == 0:
                    await message.reply(
                        "⚠️ **This Claim About New Jersey Is Disputed.**\nHelp keep Discord a place for reliable info. Find out more about why New Jersey is bad before posting.")
                else:
                    await message.reply(
                        "Don't use \"new jersey\" and \"good\" in the same sentence! Misinformation is a problem!")
            else:
                if message.channel.id == 925208759268147327: #this is the introductions channel
                    await message.reply("Oh, you’re from New Jersey? What exit?")
                elif random.randrange(config.chance2) == 0:
                    await message.reply("I̸̛̛͉͈͔̖̯̤̔̿̄͐̀͊̄̀ ̶̲͓͍͕̝͑́̒f̵̨͇͚̦̯̭̪̍͜ͅu̵̺̖̲̤̘̥͔̓c̷̢͍͒̿̒̔͑̇͠ͅk̷̨̠͓̻̠̣͕̯̩̅̌̔̆̅͌͘͝i̷̬̟̖̬̩͎̞̍ṇ̷̛͓̙̬͉̙͍̍̀̈́̀̈́̔̊͠ͅg̸̳̙̜͎̔̓̑͊͊͋̕͜͠ͅ ̸͔͚̝̳̅͛̉̓̔̆͝h̶̨̭̓̊̀̌͊̆͗̀̈́̇a̸̢̳̓͋t̶̢̛̝̫̺̭̫͍̮͍͈̍̊̈́̒̎̇̆͊̄e̸̡͉̳̲̲͓̾̅͐̈́́͗͗̓͜ͅ ̶̧̗̖͔̲̝͍͇̼͒̏̽͗̈̅̎̕n̸̗̫͙̞͗͒̆̇͂̅͆͜ḙ̸̻͕̈͆̋̉̾͌w̵̢̬̹̗̟͈̞͉͎͐̄ͅ ̸̢͉̪͍̹̼̮͚͔̐̉̌͂͂̃̚͜͠͠j̴͖͖̝͛̐̎̅̎̀̑̇͜e̴̩̦̮͙̽̓͂͐̏͝r̸͙̝̙̣͚͕̫̰̓̓̒̉͗̒ͅš̵̪̫͙͔̩̊͊̈̽̿́͋̌̽ë̸͖̹̥́̿̿̒͌̐̈́͝ỹ̷̭͍̿̈͝")
                elif random.randrange(config.chance2) == 1:
                    await message.reply("https://i.redd.it/sh4geimk2jv51.jpg")
                elif random.randrange(config.chance2) == 2:
                    await message.reply("https://www.youtube.com/watch?v=LTQpFmG2VJk")
                elif random.randrange(config.chance2) == 3:
                    await message.reply("https://www.youtube.com/watch?v=l_7XhzCc0-0")
                else:
                    await message.reply("I fucking hate new jersey 😡😡😡😡😡😡😡😡😡")
        if "im " in message.content.lower() or "i'm " in message.content.lower():
            if "im " in message.content.lower():
                index = message.content.lower().index("im") + 3
            if "i'm " in message.content.lower():
                index = message.content.lower().index("i'm") + 4  # stfu ignore the bad REALLY code
            if random.randrange(config.chance) == 0:
                await message.reply("https://discord.com/oauth2/authorize?client_id=503720029456695306&scope=bot&permissions=537263168")
            else:
                await message.reply(
                    "Hi " + message.content[index:] + ", I'm dad!")  # warning doesn't matter and i dont cate enough to fix
        if random.randrange(config.chance) == 0:
            await message.channel.send("https://images-ext-1.discordapp.net/external/2kxuirHSrAbZ9wYvmpJDF9XVoRC0cCai_5fLrhdbnf4/%3Fc%3DVjFfZGlzY29yZA/https/media.tenor.com/ZWNF4V4ftdAAAAPo/new-jersey-walter-white-amogus.mp4")
        if message.content[0] == ")":
            url = message.content[1:]
            print(url)
            await yt(message, url)

    @loop(seconds=3600)
    async def join_vc(self):
        audio_files = os.listdir("audio_files")
        vc_channel = await client.fetch_channel(config.vc_channel_id)  # This may get me r8 limited. fix if it does
        vc = await vc_channel.connect()
        vc.play(discord.FFmpegPCMAudio(source="audio_files/" + audio_files[random.randrange(len(audio_files))]))
        guild = await client.fetch_guild(925208758370590820)
        if message.guild.voice_client is not None:
            await guild.voice_client.disconnect()
        while vc.is_playing():
            sleep(.1)


async def yt(message, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = message.author.voice.channel
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        if info["duration"] > 900:
            await message.channel.send("Video is too long!")
            return
        if "newjersey" in info["title"].lower().replace(" ",""):
            await message.channel.send("I don't play songs that contain the slander of new jersey!")
            return
        if message.guild.voice_client is not None:
            await message.guild.voice_client.disconnect()
        if "static" in info["title"].lower():
            await message.channel.send("bad toby")
            return
        vc = await voice.connect()
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    await message.channel.send("Playing " + info["title"] + "...")

client = MyClient()
client.run(f.read())
f.close()
