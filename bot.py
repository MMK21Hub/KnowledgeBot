import traceback
import discord
from discord.ext import commands

import urllib.request
import json
import time
import os
from datetime import datetime

# Discord stuff
token = open("token.txt", mode="r")
bot = commands.Bot(command_prefix='^')


def intToEmoji(number):
    if number == 0:
        return ":zero:"
    if number == 1:
        return ":one:"
    if number == 2:
        return ":two:"
    if number == 3:
        return ":three:"
    if number == 4:
        return ":four:"
    if number == 5:
        return ":five:"
    if number == 6:
        return ":six:"
    if number == 7:
        return ":seven:"
    if number == 8:
        return ":eight:"
    if number == 9:
        return ":nine:"
    if number == 10:
        return ":keycap_ten:"


# Global variables
branch = "main"
latestTree = {}
newsList = {}

# Bot command declarations


@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)


@bot.command(brief="Check the bot's status", description="Check that the bot is alive. Also returns latency.")
async def ping(ctx):
    await ctx.send('Pong! Latency: `'+str(round(bot.latency*1000))+"ms`")


@bot.group()
@commands.is_owner()
async def admin(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **Incorrect or missing subcommand.**")


@admin.error
async def admin_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **You do not have permission.**")


@admin.command(brief="Big red button", description="Immediately closes the bot's connection to Discord.")
async def disconnect(ctx):
    await ctx.channel.send("Goodbye.")
    await bot.close()


@bot.group()
async def mc(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **Incorrect or missing subcommand.**", embed=discord.Embed(description="Command help - `"+bot.command_prefix+"help mc`"))


@mc.command(brief="Structured block infomation", description="Returns JSON data for a Minecraft block, to reduce reliance on the MCW.")
async def block(ctx, block):
    f = open("assets/minecraft-data/minecraft/item.json")
    blocks = json.loads(f.read())
    if block in blocks["entries"]:
        for entry in blocks["entries"]:
            if entry["name"] == block:
                output = json.dumps(entry, indent=2)
                await ctx.send("```json\n"+output+"\n```")
                break
    else:
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **Could not find a block with the namespaced ID of `"+block+"`**", embed=discord.Embed(title="Things to try", description=" 1. Check your spelling.\n 2. Is your ID correct? E.g. `minecraft:beef` is incorrect.\n 2. Have you included the namespace? E.g. `cooked_steak` is invalid.\n 3. Is your block from the wrong Minecraft version?"))


@bot.event
async def on_ready():
    print("Connected!")


@bot.group(description="Preform common tasks without needing to open up the Minecraft Launcher", brief="Utils related to the MC launcher")
async def launcher(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **Incorrect or missing subcommand.**", embed=discord.Embed(description="Command help - `"+bot.command_prefix+"help launcher`"))


@launcher.command(brief="Receive important infomation", description="Infomation from Mojang about scheduled downtime etc. Usually empty.")
async def notices(ctx):
    await ctx.channel.trigger_typing()
    noticeList = json.loads(urllib.request.urlopen(
        "https://launchercontent.mojang.com/alertMessaging.json").read().decode('UTF-8'))
    if len(noticeList["entries"]) == 0:
        await ctx.send("**No notices!**")
    elif len(noticeList["entries"]) > 0:
        await ctx.send(len(noticeList["entries"])+" notices are available. I haven't implemented notices yet, as I have no idea what the format for them will be. (<@484593355859427329> fix it!)\nHere's the raw JSON:")
        for notice in noticeList:
            await ctx.send("```json\n"+notice+"\n```")


@launcher.group(brief="Latest Minecraft news", description="Get the 10 latest MC News posts across all categories. See subcommands for more options.")
async def news(ctx):
    await ctx.channel.trigger_typing()
    if globals()["newsList"] == {}:
        newsList = json.loads(urllib.request.urlopen(
            "https://launchercontent.mojang.com/news.json").read().decode('UTF-8'))
    else:
        newsList = globals()["newsList"]

    output = ""
    newses = 0
    for newsItem in newsList["entries"]:
        if newses != 10:
            output = output + intToEmoji(newses + 1) + " **" + newsItem["title"] + "** " + \
                "[`" + newsItem["id"] + "`]\n"
            newses = newses + 1
    if output == "":
        output = "**No news found!**"
    await ctx.send(output)


@news.command(brief="View a specific news item")
async def get(ctx, id):
    if globals()["newsList"] == {}:
        newsList = json.loads(urllib.request.urlopen(
            "https://launchercontent.mojang.com/news.json").read().decode('UTF-8'))
    else:
        newsList = globals()["newsList"]

    # Errors


@bot.event
async def on_command_error(ctx, error):
    await ctx.send("❌ Unhandled error: `"+str(error)+"`")
    traceback.print_exc()

bot.run(token.read())
