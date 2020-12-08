import discord
import urllib.request
import json
import time
import os

token = open("token.txt",mode="r")

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    command = message.content[1:]
    args = command.split(' ')
    if message.author == client.user:
        return

    if message.content.startswith('^ping'):
        await message.channel.send('Pong!')

    if message.content == "^help":
        await message.channel.send("This server's prefix is `^`\n__**Commands**__\n`ping` - Check the bot's uptime\n`update-cache` - Contact the Github and Mojang servers\n`admin` - perform maintenance on the bot")

    if message.content.startswith("^help "):
        await message.channel.send("No")
    
    if message.content == "^admin":
        if message.author.id == 569602218731372710:
            await message.add_reaction("⛔")
        else:
            await message.channel.send("You're not an admin!")
    if message.content.startswith("^admin "):
        if args[1] == "branch":
            global branch
            if "branch" in globals():
                pass
            else:
                branch = "main"
            if args[2] != branch:
                branch = args[2]
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")
                await message.channel.send("I am already on that branch!")

    if message.content.startswith("^update-cache"):
        async with message.channel.typing():
            await message.channel.send("Reloading!")
            time.sleep(0.5)
            rawjson = urllib.request.urlopen("https://launchermeta.mojang.com/mc/game/version_manifest.json").read()
            pyjson  = json.loads(rawjson)
            await message.channel.send("Latest release: "+pyjson["latest"]["release"]+"\n"+"Latest snapshot: "+pyjson["latest"]["snapshot"])
            rawjson = urllib.request.urlopen("https://api.github.com/repos/SheepCommander/KnowledgeBase").read()
            pyjson  = json.loads(rawjson)
            await message.channel.send("Repo last updated at: "+pyjson["updated_at"])

    if message.content.startswith("^pastes"):
        await message.channel.trigger_typing()
        faqList = list()
        rawjson = urllib.request.urlopen("https://api.github.com/repos/SheepCommander/KnowledgeBase/branches/"+branch).read()
        pyjson  = json.loads(rawjson)
        rawjson = urllib.request.urlopen(pyjson["commit"]["commit"]["tree"]["url"]).read()
        pyjson  = json.loads(rawjson)
        for i in pyjson["tree"]:
            if i["path"] == "1.16.4":
                rawjson = urllib.request.urlopen(i["url"]).read()
                pyjson  = json.loads(rawjson)
                for folder in pyjson["tree"]:
                    if folder["path"] == "faq":
                        rawjson = urllib.request.urlopen(folder["url"]).read()
                        pyjson  = json.loads(rawjson)
                        for faq in pyjson["tree"]:
                            faqList.append(faq["path"])
        else:
            faqListMD = ""
            for i in faqList:
                faqListMD = faqListMD + "`" + i + "` "
            await message.channel.send("**Available FAQs: **"+faqListMD)

client.run(token.read())
