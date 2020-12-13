import discord
from discord.ext import commands

import urllib.request
import json
import time
import os
from datetime import datetime

# Discord stuff
token = open("token.txt",mode="r")
bot = commands.Bot(command_prefix='^')

# Global variables
branch = "main"
latestTree = {}

# Bot command declarations
@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)

@bot.command(brief="Check the bot's status", description = "Check that the bot is alive. Also returns latency.")
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

@admin.command(brief="Big red button", description = "Immediately closes the bot's connection to Discord.")
async def disconnect(ctx):
    await ctx.channel.send("Goodbye.")
    await bot.close()

@bot.group()
async def mc(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.add_reaction("❌")
        await ctx.send("❌ **Incorrect or missing subcommand.**",embed=discord.Embed(description="Command help - `"+bot.command_prefix+"help mc`"))

@mc.command(brief="Structured item data", description="Returns JSON data for a Minecraft item, to reduce reliance on the MCW.")
async def item(ctx,item):
    pass

@bot.event
async def on_ready():
    print("Connected!")

# Errors
@bot.event
async def on_command_error(ctx, error):
    await ctx.send("❌ Unhandled error: `"+str(error)+"`")

bot.run(token.read())
