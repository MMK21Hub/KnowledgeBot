import discord
from discord import client
from discord.ext import commands
import asyncio

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

# Errors
@bot.event
async def on_command_error(ctx, error):
    await ctx.send("❌ Unhandled error: `"+error+"`")

# Bot command declarations
@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)

@bot.command()
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

@admin.command()
async def disconnect(ctx):
    await ctx.channel.send("Goodbye.")
    await bot.close()

@bot.event
async def on_ready():
    print("Connected!")

bot.run(token.read())
