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

# Global variables
branch = "main"
latestTree = {}

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

# Errors


@bot.event
async def on_command_error(ctx, error):
    await ctx.send("❌ Unhandled error: `"+str(error)+"`")

bot.run(token.read())
