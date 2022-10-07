import discord
from discord.ext.commands import Bot
from discord.ext import commands
from bson.objectid import ObjectId
import asyncio
import datetime
import json
import threading
import os
import random
import types
from dateutil.relativedelta import relativedelta
import pymongo
import re

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content

client = commands.Bot(command_prefix = '!', intents=intents)

class Games(object):
    def __init__(self):
        self.dbClient = pymongo.MongoClient("mongodb://bot-db:27017/")
        self.gamesDb = None
        
    def init_db(self):
        if self.gamesDb != None:
            return
            
        dblist = self.dbClient.list_database_names()
        if "games" not in dblist:
            self.gamesDb = self.dbClient["Games"]
            self.gameinfoCollection = self.gamesDb["GameInfo"]
            
            with open('data/gameinfo.json', 'r') as f:
                gamesList = json.load(f)
                
            self.gameinfoCollection.insert_many(gamesList["Games"])
        else:
            self.gamesDb = self.dbClient["Games"]
            self.gameinfoCollection = self.gamesDb["GameInfo"]
            
        self.gameStateCollection = self.gamesDb["GameState"]
        
    @staticmethod
    def player_check(game, state):
        return len(game["Seats"]) - len(state["Seats"])
        
    async def create_game(self, gameName, seatName, creatorName, creatorId):
        #1st arg = game template name
        query = { "Name" : gameName }
        game = self.gameinfoCollection.find_one(query)
       
        # TODO Actually the initial_state could go into the start_game logic and probably should.
        initial_state = game["InitialState"]
       
        #2nd arg = optional seat name to sit at if missing sit at first seat
        if not seatName is None:
            if not game["Seats"].contains(seatName):
                print("Error, we're trying to sit in a seat that doesn't exist")
                return
            else:
                seat = { "Name" : seatName, "DisplayName" : creatorName, "Id" : creatorId }
                initial_state["Seats"].append(seat)
        else:
            seat = { "Name" : game["Seats"][0], "DisplayName" : creatorName, "Id" : creatorId }
            initial_state["Seats"].append(seat)
                
        gameId = self.gameStateCollection.insert_one(initial_state).inserted_id
        
        players_required = self.player_check(game, initial_state)
        if players_required == 0:
            return await self.start_game(gameId)
        else:
            return "Created game with ID: {} needs {} more players".format(gameId, players_required)
    
    async def join_game(self, gameId, seatName, playerName, playerId):

        query = { "_id" : ObjectId(gameId) }
        state = self.gameStateCollection.find_one(query)

        game_query = { "Name" : state["Game"] }
        game = self.gameinfoCollection.find_one(game_query)

        #2nd arg = seat?  Or sit at first open seat?  For now, just sit at 1
        if not seatName is None:
            if not game["Seats"].contains(seatName):
                print("Error, we're trying to sit in a seat that doesn't exist")
                return
            else:
                # TODO Check here if somebody is already sitting in that seat!
                seat = { "Name" : seatName, "DisplayName" : playerName, "Id" : playerId }
                state["Seats"].append(seat)
        else:
            # TODO not seat[1], but first free seat
            seat = { "Name" : game["Seats"][1], "DisplayName" : playerName, "Id" : playerId }
            state["Seats"].append(seat)

        self.gameStateCollection.replace_one(query, state)
        
        players_required = self.player_check(game, state)
        if players_required == 0:
            return await self.start_game(gameId)
        else:
            return "Joined game with ID: {} needs {} more players".format(gameId, players_required)
    
    async def start_game(self, gameId):
        print("Woo!  Got as far as start_game! {}".format(gameId))
        
        query = { "_id" : ObjectId(gameId) }
        state = self.gameStateCollection.find_one(query)

        for seat in state["Seats"]:
            await client.get_user(seat["Id"]).send("Game {} starting, you are in seat {}".format(gameId, seat["Name"]))

        return "Game with ID: {} Started".format(gameId)
       
        # 0. Run initial game state?
        # 1. Find out who is on turn
        # 2. Show them the board state (maybe + legal moves)
        # 3. Wait for them to message to say what move they are making
        # Also somewhere cache the last gameID that a player joined to shortcircuit their command?
        
games = Games()

allGoals = ["https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Acrobatic.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Ambusher.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Assassin.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Assistant.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Bastion.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Bully.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Contagious.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Covetous.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Cuddler.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Discerning.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Distracted.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Drowsy.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Elitist.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Exterminator.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Fearful.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Feeble.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Feral.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Finisher.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Hesitant.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Hothead.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Instigator.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Insulting.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Limping.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Lucky.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Marksman.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Miser.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Mugger.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Multitasker.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Paranoid.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Peacemonger.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Perforated.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Pickpocket.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Pincushion.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Prosperous.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Ravager.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Recluse.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Reserved.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Restless.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Retaliator.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Ritualistic.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Scavenger.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Shadow.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Sharpshooter.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Slayer.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Sleepless.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Sober.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Sociable.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Specialized.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Stalwart.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Stubborn.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Thorough.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Untouchable.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Wasteful.jpg",
            "https://raw.githubusercontent.com/eratos/DiscordCountdownBot/master/images/battle-goals/Winded.jpg",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/aggressor.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/diehard.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/dynamo.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/executioner.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/explorer.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/fasthealer.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/hoarder.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/hunter.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/indigent.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/layabout.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/masochist.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/neutralizer.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/opener.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/pacifist.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/plunderer.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/professional.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/protector.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/purist.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/sadist.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/scrambler.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/straggler.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/streamliner.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/workhorse.png",
            "https://raw.githubusercontent.com/any2cards/gloomhaven/master/images/battle-goals/zealot.png"]
        
liveGoals = []
usedGoals = []

draftOriginal = ["Big4", "MS", "CWI", "Mail", "LSL", "MC", "OI", "MPC", "SC", "TBC", "Blank"]

last_redacto = ""

# Prepare key
key = open('key.txt', 'r')
token = key.read()
key.close()

#Prepare datetime things
currentDT = datetime.datetime.utcnow()
print(str(currentDT.year) + ", " + str(currentDT.month) + ", " +str(currentDT.day) + ", " +str(currentDT.hour) + ", " +str(currentDT.minute) + ", " +str(currentDT.second))
currentDT = datetime.datetime.now()
print(str(currentDT.year) + ", " + str(currentDT.month) + ", " +str(currentDT.day) + ", " +str(currentDT.hour) + ", " +str(currentDT.minute) + ", " +str(currentDT.second))
print(os.getcwd())


# Boot confirmation
@client.event
async def on_ready():
    print("Ready")
    game = discord.Game("with a Mongo Database")
    await client.change_presence(status = discord.Status.idle, activity = game)
    #for u in client.users:
    #    print(u.name + ":" + str(u.id))
    games.init_db()
    last_redacto = ""

# Read message
@client.event
async def on_message(message):
    # Time till command
    if message.content.upper().startswith("TIME UNTIL "):
    
        if message.author == client.user:
            return
                
        try:
            args = message.content.split(" ")

            # Set message to check
            mess = (" ".join(args[2:]))
            # JSON file
            with open('data/timers.json', 'r') as f:
                timers = json.load(f)

            y = timers[mess.upper()]['year']
            m = timers[mess.upper()]['month']
            d = timers[mess.upper()]['day']
            h = timers[mess.upper()]['hour']
            mm = timers[mess.upper()]['minute']
            s = timers[mess.upper()]['second']
            
            if args[2].upper().startswith("LUNCH"):
                currentDT = datetime.datetime.utcnow()
                y = currentDT.year
                m = currentDT.month
                d = currentDT.day

            await message.channel.send(GetTimeTill(mess, y, m, d, h, mm, s))

        except Exception as e:
            print("Exception in TIME UNTIL: message content follows")
            print(message.content)
            print(e)
            await message.channel.send("¯\_(ツ)_/¯")

    if message.content.upper().startswith("HOW MANY HOURS"):
        try:
            args = message.content.split(" ")

            # Set message to check
            mess = "Gloomhaven"
            # JSON file
            with open('data/timers.json', 'r') as f:
                timers = json.load(f)

            y = timers[mess.upper()]['year']
            m = timers[mess.upper()]['month']
            d = timers[mess.upper()]['day']
            h = timers[mess.upper()]['hour']
            mm = timers[mess.upper()]['minute']
            s = timers[mess.upper()]['second']
            await message.channel.send(GetTimeTill(mess, y, m, d, h, mm, s))

        except Exception as e:
            print("Exception in HOW MANY HOURS: message content follows")
            print(message.content)
            print(e)
            await message.channel.send("¯\_(ツ)_/¯")
            # await message.channel.send("Still broken")
            # await message.channel.send("That timer doesn't exist! ensure spelling is exact, or type 'new timer, NAME' to create a new timer")

    # New timer
    if message.content.upper().startswith("NEW TIMER, "):
        try:
            #Load arguments
            args = message.content.split(", ")
            mess = args[1]
            y = int(args[2])
            m = int(args[3])
            d = int(args[4])
            h = int(args[5])-1
            mm = int(args[6])
            s = int(args[7])

            # JSON file
            with open('data/timers.json', 'r') as f:
                timers = json.load(f)


            await NewTimer(message.channel, timers, mess.upper(), y, m, d, h, mm, s)

            with open('data/timers.json', 'w') as f:
                f.write(json.dumps(timers, sort_keys=True, indent=4, separators=(',', ': ')))

        except:
            await message.channel.send("Sorry no can do, invalid syntax my dude\n\nUsage: **NEW TIMER, unique title with any spacing, 4digityear, month(1-12), day(1-31), hour(1-24), minute(1-60), second(1-60)**\nOnly use integer numbers for times, and divide each argument with ONE comma and ONE space.")

    if message.content.upper().startswith("!18XX"):
        await message.author.send("Not yet...")

    if message.content.upper().startswith("BATTLE GOAL PLEASE"):
        global liveGoals
        if not liveGoals:
            liveGoals = allGoals[:]
            random.shuffle(liveGoals)
            print("Shuffled battle goals!")
            
        await message.author.send(liveGoals.pop())
        await message.author.send(liveGoals.pop())

    mum = False
    match = re.search("^YOUR M(?:U|O)M IS (.*)", message.content, re.I)
    if match:  
        mum = True
        await message.channel.send("Your face is " + match.group(1))

    match = re.search("^YOUR M(?:U|O)M'*S (.*)", message.content, re.I)
    if match:     
        mum = True
        await message.channel.send("Your face's " + match.group(1))

    if not mum:
        match = re.search("^YOUR M(?:U|O)M (.*)", message.content, re.I)
        if match:     
            await message.channel.send("Your face " + match.group(1))       
        
    await client.process_commands(message)

# Read message
@client.event
async def on_message_delete(message):
    global last_redacto
    print("REDACTO ALERT! - {} deleted {}".format(message.author,message.content))
    last_redacto = "{} redacto'd {}".format(message.author,message.content)

# Function for adding new timer
async def NewTimer(chan, timers, mess, y, m, d, h, mm, s):
    if not mess in timers:
        timers[mess] = {}
        timers[mess]['year'] = y
        timers[mess]['month'] = m
        timers[mess]['day'] = d
        timers[mess]['hour'] = h
        timers[mess]['minute'] = mm
        timers[mess]['second'] = s
        await chan.send("Successfully added new timer: " + mess)
        print("ADDED NEW TIMER TO TIMERS.JSON: " + mess)
    else:
        await chan.send("A timer with that name already exists")

def GetTimeTill(mess, y, m, d, h, mm, s):
    currentDT = datetime.datetime.now()
    try:
        rd = relativedelta(datetime.datetime(y, m, d, h, mm, s), currentDT)
    except:
        return "Timer " + mess + " complete!"
        
    if rd.days < 0:
        return "You tell me!"
        
    if rd.days == 0 and rd.hours < -5:
        return "You tell me!"
    
    return "Time until " + mess + ": "+ str(rd.years) +" years, "+ str(rd.months) +" months, "+ str(rd.days) +" days, "+ str(rd.hours) +" hours, "+ str(rd.minutes) +" minutes, " + str(rd.seconds) + " seconds."

# Game-y stuff starts here.
@client.command()
async def redacto(context, *arg):
    await context.send(last_redacto)

# Game-y stuff starts here.
@client.command()
async def test(context, *arg):
    print("Recieved test message from " + str(context.author.name) + " with ID " + str(context.author.id) + " Discriminator " + str(context.author.discriminator))
    await context.send(str(arg))
    await context.author.send("`Thanks for sending me a test message`")
    await context.author.send("```Thanks for sending me a test message```")

@client.command()
async def bg(context):
    global liveGoals
    if not liveGoals:
        liveGoals = allGoals[:]
        random.shuffle(liveGoals)
        print("Shuffled battle goals!")
        
    await context.author.send(liveGoals.pop())
    await context.author.send(liveGoals.pop())

@client.command()
async def newgame(context, *args):
    response = await games.create_game(args[0], args[1] if len(args)>1 else None, context.author.name, context.author.id)
    await context.author.send(response)
   
@client.command()
async def joingame(context, *args):
    response = await games.join_game(args[0], args[1] if len(args)>1 else None, context.author.name, context.author.id)
    await context.author.send(response)

def roll_one(sides):
    return random.randint(1,sides)
    
@client.command()
async def roll(context, arg):
    """ Parse strings like "2d6" or "1d20" and roll accordingly """
    pattern = re.compile(r'^(?P<count>[0-9]*d)?(?P<sides>[0-9]+)$')
    match = re.match(pattern, arg)

    if not match:
        if arg.upper().startswith("RICK"):
            await context.channel.send("https://www.youtube.com/watch?v=xvFZjo5PgG0".format(arg))
        await context.channel.send("¯\_(ツ)_/¯ I don't know how to roll {}".format(arg))
        raise ValueError() # invalid input string

    sides = int(match.group('sides'))
    try:
        count = int(match.group('count')[:-1])
    except:
        count = 1

    if count > 9000:
        await context.channel.send("But that's over 9000!".format(arg))
        raise ValueError() # invalid input string
    
    rolls = [ roll_one(sides) for i in range(count) ]
    result = ",".join(str(r) for r in rolls)
    
    response = "Rolled {} and got [{}] which sums to {}".format(arg, result, sum(rolls))
    try:
        await context.channel.send(response)
    except:
        try:
            await context.channel.send("Can't send the list of values, but the sum was {}".format(sum(rolls)))
        except:
            await context.channel.send("¯\_(ツ)_/¯")

#@client.command()
#async def speak(context, arg):
#    await context.channel.send(arg, tts=True)

    
# Run bot
client.run(token)
