import datetime
import math
import os
import random
import pickle
import time

from discord.ext import tasks
from discord.utils import get

import user
import config
from typing import List, Dict
import asyncio

import discord
from youtube_dl import YoutubeDL

tokenFile = open("token", "r")
token = tokenFile.read()
tokenFile.close()
queue = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
save_data = {}
guild = None


# Picks a random filename in a directory
def randomFile(dir: str) -> str:
    fileNames: List[str] = os.listdir(dir)
    return f"{dir}/{random.choice(fileNames)}"


# Picks a random string from a weighted selection
def randomString(choices: Dict[str, int]) -> str:
    totalWeight = 0
    for value in choices.values():
        totalWeight += value

    selectedWeight = random.randrange(0, totalWeight)
    passedWeight = 0
    for key in choices:
        passedWeight += choices[key]
        if passedWeight > selectedWeight:
            return key
    raise RuntimeError("This shouldn't be able to happen.")


# Returns true if "new jersey" is in the string
def containsNJ(text: str) -> bool:
    return "newjersey" in text.lower().replace(" ", "")


def containsCivE(text: str) -> bool:
    return "civile" in text.lower().replace(" ", "") or "civil engineering" in text.lower().replace(" ", "")


# Returns the index after "I'm" or "Im", or -1 if not found
def containsIm(text: str) -> int:
    # "Im"
    index = text.lower().find("im ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 3
    # "I'm"
    index = text.lower().find("i'm ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 4
    # Not found
    return -1


def containsYour(text: str) -> int:
    # "Im"
    index = text.lower().find("youre ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 5
    # "I'm"
    index = text.lower().find("you're ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 6
    # Not found
    return -1


def get_user_from_at(at: str):
    str_id = at.replace("<", "").replace(">", "").replace("@", "")
    int_id = int(str_id)
    if int_id in user.users:
        return user.get_user(int_id)


def save():
    pickle.dump(save_data, open(config.save_data_file, "wb"))


class AntiNJClient(discord.Client):
    @tasks.loop(seconds=20)
    async def birthday_check(self):
        if "last_birthday" not in save_data or save_data["last_birthday"] + 86400 < time.time():
            save_data["last_birthday"] = time.time()
            save()
            c = await client.fetch_channel(925208760010551334)
            await c.send("Happy Birthday <@955141074161111072>!!!")

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        self.disabled = False
        user_files = os.listdir(config.user_save_dir)
        for user_i in user_files:
            user_file = open(f"{config.user_save_dir}/{user_i}", "rb")
            user.users[int(user_i)] = pickle.load(user_file)
            if len(config.user_reset_values) > 0:
                for reset in config.user_reset_values:
                    setattr(user.users[int(user_i)], reset, config.user_reset_values[reset])
                user.users[int(user_i)].save()
        global guild
        global save_data
        if os.path.isfile(config.save_data_file):
            save_data = pickle.load(open(config.save_data_file, "rb"))
        guild = await client.fetch_guild(925208758370590820)
        self.birthday_check.start()
        if "toad" not in save_data:
            save_data["toad"] = False
            save()
        await self.join_vc()

    async def on_message(self, message: discord.Message):
        split_message = message.content.split(" ")
        if "zach" in message.content.lower():
            await message.reply("*zak")
        if self.disabled:
            return
        if split_message[0] == "!getdata" and message.author.id:
            self.disabled = True
            await message.reply(
                "Getting data... All bot functions have been temporarily disabled to conserve API rate limit!")
            print("Generating Data...")
            async for message in message.channel.history(limit=1000000):
                file = open(config.output_path, "a")
                file.write("!" + str(message.author.id) + ":" + message.content + "§\n\n")
            self.disabled = False
            await message.reply("Done!")
        if message.author.id == 964331688832417802 or message.channel.id in config.banned_channels or message.author.bot:
            return
        if split_message[0] == "!toad":
            save_data["toad"] = not save_data["toad"]
            save()
            await message.reply("Toad mode set to " + str(save_data["toad"]))
        if split_message[0] == "!setiq":
            if len(split_message) != 2:
                await message.reply("Usage: !setiq <iq>")
                return
            try:
                iq = float(split_message[1])
            except ValueError:
                await message.reply("Usage: !setiq <iq>")
                return
            c_user = user.get_user(message.author.id)
            c_user.iq = iq
            c_user.save()
            await message.reply("Updated your IQ!")
            return
        if split_message[0] == "!getiq":
            if len(split_message) != 2:
                await message.reply("Usage: !getiq <user>")
                return
            if get_user_from_at(split_message[1]) is None:
                await message.reply("Usage: !getiq <user>")
                return
            a_user = get_user_from_at(split_message[1])
            if not hasattr(a_user, "iq"):
                await message.reply("User has not set an IQ. It must be super low!")
                return
            await message.reply("<@" + str(a_user.discord_id) + ">'s iq is " + str(a_user.iq))
            return
        if message.content.replace(" ", "") == "<@964331688832417802>":
            out = ""
            if len(queue) < 1:
                await message.reply("The queue is empty!")
                return
            for item in queue:
                out += "**" + item["info"]["title"] + "** in <#" + str(item["channel"].id) + "> by " + item[
                    "user"].display_name + "\n"
            await message.reply(out)
            return
        if split_message[0] == "bal":
            if len(split_message) == 1:
                c_user = user.get_user(message.author.id)
                await message.reply("You have " + str(c_user.jersey_coins) + " jersey coins!")
                return
            elif get_user_from_at(split_message[1]) is not None:
                a_user = get_user_from_at(split_message[1])
                await message.reply(
                    "<@" + str(a_user.discord_id) + "> has " + str(a_user.jersey_coins) + " jersey coins!")
                return
            else:
                await message.reply("Could not find that user!")
                return
        if split_message[0] == "pay":
            if len(split_message) != 3:
                await message.reply("Usage: pay <user> <amount>")
                return
            elif get_user_from_at(split_message[1]) is not None:
                a_user = get_user_from_at(split_message[1])
                c_user = user.get_user(message.author.id)
                try:
                    amount = float(split_message[2])
                except ValueError:
                    await message.reply("Usage: pay <user> <amount>")
                    return
                if amount < 0:
                    await message.reply("You may not pay negative jersey coins!")
                    return
                if c_user.jersey_coins - amount < 0:
                    await message.reply("You do not have enough jersey coins to make that payment!")
                    return
                c_user.jersey_coins -= amount
                a_user.jersey_coins += amount
                c_user.save()
                a_user.save()
                await message.reply("Payment successful!")
                return
            else:
                await message.reply("Could not find that user!")
                return
        if message.content[0] == ">" or message.content[0] == ")":
            url = message.content[1:]
            if message.channel.id == 925208760010551335 and random.randrange(config.music_commands_chance - 1) != 0:
                await message.reply("I do not play anything in <#925208760010551335>")
                return
            if message.guild.id != config.main_guild:
                await message.reply(
                    "I do not play anything out side of the main RPI Class of 2022 discord server! If you want a music playing bot I would recommend this one: https://fredboat.com/")
                return
            try:
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
            except:
                await message.reply("Something went wrong while attempting to get the video!")
            if info["duration"] > config.max_song_length:
                await message.reply("Video is too long!")
                return
            if containsNJ(info["title"]):
                await message.reply("I don't play songs that contain the slander of new jersey!")
                return
            if "static" in info["title"].lower():
                await message.reply("bad toby")
                return
            if message.author.voice is None or message.author.voice.channel is None:
                await message.reply("You must be in a voice channel to play music.")
                return
            if "toby" in message.author.display_name.lower():
                await message.reply(
                    "I'm very sorry but because your name contains \"toby\" you cannot play music. Please contact <@343545158140428289> if this is a mistake!")
                return
            if config.prospective_students in message.author.roles:
                await message.reply(
                    "You may not play songs as a prospective student!")
                return
            if message.content[0] == ">":
                c_user = user.get_user(message.author.id)
                delta_time = time.time() - c_user.last_song_skip
                if delta_time < config.song_skip_time and message.author.id not in config.moderators:
                    await message.reply("You cannot replace the song for another " + str(
                        math.floor((config.song_skip_time - delta_time) / 60)) + " minutes and " + str(
                        round((config.song_skip_time - delta_time) % 60, 0)) + " seconds!")
                    return
                c_user.skip_count += 1
                c_user.last_song_skip = time.time()
                c_user.save()
                if len(queue) > 0:
                    queue.insert(1, {
                        "channel": message.author.voice.channel,
                        "url": url,
                        "user": message.author,
                        "info": info,
                    })
                else:
                    queue.append(  # Fuck classes. Dictionaries for life. I regret this now.
                        {
                            "channel": message.author.voice.channel,
                            "url": url,
                            "user": message.author,
                            "info": info,
                        }
                    )
                await yt(message.author.voice.channel, url)
                await message.reply(f"Playing {info['title']}... (You've skipped " + str(c_user.skip_count) + " songs)")
                return
            if message.content[0] == ")":
                c = 0
                for item in queue:
                    if item["user"].id == message.author.id:
                        c += 1
                if c >= config.max_queue_per_user and message.author.id not in config.moderators:
                    await message.reply("You may only have a maximum of " + str(
                        config.max_queue_per_user) + " songs in the queue at a time!")
                    return
                if len(queue) < 1:
                    await yt(message.author.voice.channel, url)
                    await message.reply(f"Playing {info['title']}...")
                else:
                    await message.reply(f"Added {info['title']} to queue...")
                queue.append(  # Fuck classes. Dictionaries for life. I regret this now.
                    {
                        "channel": message.author.voice.channel,
                        "url": url,
                        "user": message.author,
                        "info": info,
                    }
                )
                return
        if message.content == "<ForceJoinVC":
            await self.join_vc(self)
            return
        if containsNJ(message.content):
            await message.add_reaction(await get_emoji(guild, "shut"))
            njcount = user.increment_user(message.author.id)
            if njcount % 100 == 0:
                try:
                    spam_channel = await client.fetch_channel(config.spam_channel_id)
                except:
                    print("ERROR: Failed to fetch spam channel from discord")
                else:
                    await spam_channel.send(f"{message.author.mention} has said new jersey {njcount} times!")
            if "good" in message.content:
                if random.randrange(config.chance2) == 0:
                    await message.reply(
                        "⚠️ **This Claim About New Jersey Is Disputed.**\nHelp keep Discord a place for reliable info. Find out more about why New Jersey is bad before posting.")
                else:
                    await message.reply(
                        "Don't use \"new jersey\" and \"good\" in the same sentence! Misinformation is a problem!")
            else:
                if message.channel.id in config.introduction_channels:
                    await message.reply("Oh, you’re from New Jersey? What exit?")
                else:
                    await message.reply(randomString(config.newJerseyReplies))
        if containsCivE(message.content):
            await message.reply(randomString(config.civilEReplies))
        indexIm = containsIm(message.clean_content)
        if indexIm >= 0:
            if random.randrange(config.chance) == 0:
                await message.reply(
                    "https://discord.com/oauth2/authorize?client_id=503720029456695306&scope=bot&permissions=537263168")
            else:
                await message.reply(
                    f"Hi {message.clean_content[indexIm:]}, I'm dad!")
        indexIm = containsYour(message.clean_content)
        if indexIm >= 0:
            await message.reply(f"I'm not {message.clean_content[indexIm:]}, I'm <@964331688832417802>!")
        if random.randrange(config.chance) == 0:
            await message.channel.send("https://media.tenor.com/ZWNF4V4ftdAAAAPo/new-jersey-walter-white-amogus.mp4")

    async def join_vc(self):
        async def queue_vc():
            # Randomly change the interval between 5 minutes to 1.5 hours
            if len(queue) > 1:
                queue.pop(0)
                await yt(queue[0]["channel"], queue[0]["url"])
            elif len(queue) == 1:
                queue.pop(0)
            else:
                await vc.disconnect()
            newinterval = random.randint(5 * 60, 90 * 60)
            self.loop.call_later(
                newinterval, self.loop.create_task, self.join_vc())

        selectedFile = randomFile("audio_files")
        # This may get me r8 limited. fix if it does
        vc_channel: discord.VoiceChannel = await client.fetch_channel(config.vc_channel_id)
        # If already connected to something, disconnect
        if vc_channel.guild.voice_client is not None:
            await vc_channel.guild.voice_client.disconnect()

        # Make sure it's an actual VC, not a text channel
        if not isinstance(vc_channel, discord.VoiceChannel):
            print(
                f"ERROR: channel {config.vc_channel_id} is not a voice channel.")
            return

        # Play the audio
        try:
            vc = await vc_channel.connect()
        except asyncio.TimeoutError:
            # Try again later.
            await queue_vc()
            return
        vc.play(discord.FFmpegPCMAudio(selectedFile),
                after=lambda err=None: self.loop.create_task(queue_vc()))
        # if message.guild.voice_client is not None:
        #     await guild.voice_client.disconnect()


async def yt(channel: discord.VoiceChannel, url):
    if save_data["toad"]:
        url = "https://youtu.be/wrdK57qgNqA"
    voice: discord.VoiceChannel = channel
    vc = get(client.voice_clients, guild=channel.guild)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        if vc is None or not vc.is_connected():
            vc = await voice.connect()
        else:
            await vc.disconnect()
            vc = await voice.connect()
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                after=lambda err: client.loop.create_task(song_finish()))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=info['title']))


async def song_finish():
    before_len = len(queue)
    try:
        queue.pop(0)
    except IndexError:
        pass
    if len(queue) > 0:
        await yt(queue[0]["channel"], queue[0]["url"])
    else:
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="nothing. Play a song!"))
        if datetime.datetime.today().weekday() == 2:
            channel = await client.fetch_channel(925208760434192414)
            await yt(channel, "https://youtu.be/wrdK57qgNqA")


async def get_emoji(guild: discord.Guild, arg):
    return get(guild.emojis, name=arg)


client = AntiNJClient()
client.run(token)
