import discord
import urllib.request
import json
import time
import os
from datetime import datetime
token = open("token.txt",mode="r")

client = discord.Client()
branch = "main"
latestTree = {}

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    command = message.content[1:]
    args = command.split(' ')
    if message.author == client.user:
        return

    if message.content.startswith('^ping'):
        await message.channel.send('Pong! Latency: `'+str(round(client.latency*1000))+"ms`")

    if message.content == "^help":
        await message.channel.send('''
        This server's prefix is `^`
        __**Commands**__
        `ping` - Check the bot's status
        `update-cache` - Contact the Github and Mojang servers
        `admin` - Perform maintenance on the bot
        
        `faq` - Get an FAQ
        `oldfaq` - Get a FAQ (legacy file structure)
        ''')

    if message.content.startswith("^help "):
        await message.channel.send("No")
    
    if message.content == "^admin":
        if message.author.id == 569602218731372710:
            await message.add_reaction("⛔")
        else:
            await message.channel.send("You're not an admin!")
    if message.content.startswith("^admin "):
        if args[1] == "branch":
            if args[2] != branch:
                branch = args[2]
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")
                await message.channel.send("I am already on that branch!")

    if message.content.startswith("^update-cache"):
        async with message.channel.typing():
            await message.channel.send("**Reloading!**")
            pyjson = json.loads(urllib.request.urlopen("https://api.github.com/repos/sheepcommander/knowledgebase/branches/main").read().decode('UTF-8'))
            globals()["latestTree"] = json.loads(urllib.request.urlopen(pyjson["commit"]["commit"]["tree"]["url"]).read().decode('UTF-8'))
            time.sleep(0.5)
            rawjson = urllib.request.urlopen("https://launchermeta.mojang.com/mc/game/version_manifest.json").read()
            pyjson  = json.loads(rawjson)
            await message.channel.send("Latest release: "+pyjson["latest"]["release"]+"\n"+"Latest snapshot: "+pyjson["latest"]["snapshot"])
            rawjson = urllib.request.urlopen("https://api.github.com/repos/SheepCommander/KnowledgeBase").read()
            pyjson  = json.loads(rawjson)
            repoLastUpdate = datetime.fromisoformat(pyjson["updated_at"].replace("Z", "+00:00")) # Convert ISO-formatted time to python datetime object
            await message.channel.send("Repo last updated at: "+repoLastUpdate.strftime("%x %X"))

    if message.content.startswith("^pastes"):
        await message.channel.trigger_typing()
        branch = "main"
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

    if message.content.startswith("^faq "):
        branch = "main"
        # Return the FAQ
        await message.channel.trigger_typing()
        faqList = list()
        pyjson = json.loads(urllib.request.urlopen("https://api.github.com/repos/SheepCommander/KnowledgeBase/git/trees/773956d208ec33797566f2748bdf1139faba21da").read())
        for faq in pyjson["tree"]:
            faqList.append({
                "name": faq["path"],
                "url": faq["url"]
            })
        for faq in faqList:
            if faq["name"] == args[1]:
                requestedFAQ = {}
                requestedFAQ["name"] = args[1]
                pyjson = json.loads(urllib.request.urlopen(faq["url"]).read())
                requestedFAQ["content"] = urllib.request.urlopen("https://raw.githubusercontent.com/sheepcommander/knowledgebase/main/1.16.4/"+requestedFAQ["name"]+"/viewable-github-paste.md").read().decode('UTF-8')
                await message.channel.send(requestedFAQ["content"])

    if message.content.startswith("^oldfaq "):
        branch = "main"
        # Return a legacy FAQ
        await message.channel.trigger_typing()
        faqList = list()
        pyjson = globals()["latestTree"] # Not sure what's going on here but it works
        for folder in pyjson["tree"]:
            if folder["path"] == "faq":
                pyjson = json.loads(urllib.request.urlopen(folder["url"]).read().decode('UTF-8'))
        for faq in pyjson["tree"]:
            faqList.append({ 
                "name": faq["path"],
                "url": faq["url"]
            })
        
        for faq in pyjson["tree"]:
            faqList.append({
                "name": faq["path"],
                "url": faq["url"]
            })
        for faq in faqList:
            if faq["name"] == args[1]:
                requestedFAQ = {}
                requestedFAQ["name"] = args[1]
                pyjson = json.loads(urllib.request.urlopen(faq["url"]).read())
                requestedFAQ["content"] = urllib.request.urlopen("https://raw.githubusercontent.com/sheepcommander/knowledgebase/main/faq/"+requestedFAQ["name"]+"/raw-paste.txt").read().decode('UTF-8')
                await message.channel.send(requestedFAQ["content"])

client.run(token.read())
