import traceback
import discord
from discord.embeds import Embed, EmbedProxy
from discord.ext import commands
import html2text

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


def newsToEmbed(newsItem):
    try:
        link = newsItem["readMoreLink"]
    except:
        link = newsItem["linkButton"]["url"]
    embed = discord.Embed(
        title=newsItem["title"],
        url=link,
        description=newsItem["text"]
    )
    embed.set_image(
        url="https://launchercontent.mojang.com/" +
            newsItem["playPageImage"]["url"]
    )
    embed.set_footer(
        text=newsItem["date"]
    )
    embed.set_author(
        name=newsItem["category"]
    )
    return embed


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


@bot.group(description="Preform common tasks without needing to open up the Minecraft Launcher. See subcommands for more options.", brief="Utils related to the MC launcher")
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


@launcher.group(brief="Latest Minecraft news", description="Get the 10 latest MC News posts across all categories. See subcommands for more options.", invoke_without_command=True)
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


@news.command(brief="View a specific news item", description="Get the full details of a news item from its ID.")
async def get(ctx, id):
    await ctx.channel.trigger_typing()
    found = False
    if globals()["newsList"] == {}:
        newsList = json.loads(urllib.request.urlopen(
            "https://launchercontent.mojang.com/news.json").read().decode('UTF-8'))
    else:
        newsList = globals()["newsList"]
    for newsItem in newsList["entries"]:
        if newsItem["id"] == id:
            await ctx.send(embed=newsToEmbed(newsItem))
            found = True
    if not found:
        await ctx.send("❌ Could not find a news item with ID of `"+id+"`")


@news.command(brief="View the latest news item")
async def latest(ctx):
    await ctx.channel.trigger_typing()
    if globals()["newsList"] == {}:
        newsList = json.loads(urllib.request.urlopen(
            "https://launchercontent.mojang.com/news.json").read().decode('UTF-8'))
    else:
        newsList = globals()["newsList"]
    await ctx.send("", embed=newsToEmbed(newsList["entries"][0]))


@news.command(brief="List the latest news items", name="list")
async def listNews(ctx, limit=10):
    await ctx.channel.trigger_typing()
    if globals()["newsList"] == {}:
        newsList = json.loads(urllib.request.urlopen(
            "https://launchercontent.mojang.com/news.json").read().decode('UTF-8'))
    else:
        newsList = globals()["newsList"]

    output = ""
    count = 0
    for newsItem in newsList["entries"]:
        if count != limit:
            if limit <= 10:
                prefix = intToEmoji(count+1)
            else:
                prefix = ":hash:"
            newsType = ""
            for i in newsItem["newsType"]:
                if i == "Java":
                    newsType = "<:mmk21bot__mcje:799363479316201543>"
                elif i == "Dungeons":
                    newsType = "<:mmk21bot__dungeons:799916874263560233>"

            output = output + newsType + " **" + newsItem["title"] + "** " + \
                "[`" + newsItem["id"] + "`]\n"
            count = count + 1
    if output == "":
        output = "**No news found!**"
    await ctx.send(output)


@launcher.group(brief="View patch notes", invoke_without_command=True)
async def history(ctx):
    await ctx.send("❌ **Incorrect or missing subcommand**\nTry `launcher history mc`.")


@history.command(brief="Get a specific version's patch notes", name="get")
async def historyGet(ctx, version):
    javaPatchNotes = json.loads(urllib.request.urlopen(
        "https://launchercontent.mojang.com/javaPatchNotes.json").read().decode('UTF-8'))
    launcherPatchNotes = json.loads(
        urllib.request.urlopen("https://launchercontent.mojang.com/launcherPatchNotes_v2.json").read().decode('UTF-8'))
    patchNote = {}
    for i in javaPatchNotes["entries"]:
        if i["version"] == version:
            patchNote = i
            project = "MC"
    for i in launcherPatchNotes["entries"]:
        for patchVersion in i["versions"]:
            if i["versions"][patchVersion] == version:
                patchNote = i
                project = "MCL"
    if patchNote == {}:
        await ctx.send("❌ Could not find `"+version+"` in the Launcher patch notes or the Minecraft: Java Edition patch notes.\nMake sure it is in the format `x.y.z`.")
    else:
        await ctx.send(html2text.html2text(patchNote["body"]))


# Errors


@bot.event
async def on_command_error(ctx, error):
    await ctx.send("❌ Unhandled error: `"+str(error)+"`")
    # traceback.print_exception(error)

bot.run(token.read())
