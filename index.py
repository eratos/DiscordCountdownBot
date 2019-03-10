import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import datetime
import json
import threading
from dateutil.relativedelta import relativedelta

Client = discord.Client()
client = commands.Bot(command_prefix = "time till ")

# Prepare key
key = open('key.txt', 'r')
token = key.read()
key.close()

#Prepare datetime things
currentDT = datetime.datetime.utcnow()
print(str(currentDT.year) + ", " + str(currentDT.month) + ", " +str(currentDT.day) + ", " +str(currentDT.hour) + ", " +str(currentDT.minute) + ", " +str(currentDT.second))

# Boot confirmation
@client.event
async def on_ready():
    print("Botesaw is readyyyy")

# Read message
@client.event
async def on_message(message):
    # Time till command
    if message.content.upper().startswith("TIME TILL "):
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
            await client.send_message(message.channel, GetTimeTill(mess, y, m, d, h, mm, s))

            #with open('data/timers.json', 'w') as f:
                #f.write(json.dumps(timers, sort_keys=True, indent=4, separators=(',', ': ')))
        except:
            await client.send_message(message.channel, "That timer doesn't exist! ensure spelling is exact, or type 'new timer, NAME' to create a new timer")

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
            await client.send_message(message.channel, "Sorry no can do, invalid syntax my dude\n\nUsage: **NEW TIMER, unique title with any spacing, 4digityear, month(1-12), day(1-31), hour(1-24), minute(1-60), second(1-60)**\nOnly use integer numbers for times, and divide each argument with ONE comma and ONE space.")


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
        await client.send_message(chan, "Successfully added new timer: " + mess)
        print("ADDED NEW TIMER TO TIMERS.JSON: " + mess)
    else:
        await client.send_message(chan, "A timer with that name already exists")

def GetTimeTill(mess, y, m, d, h, mm, s):
    currentDT = datetime.datetime.utcnow()
    try:
        rd = relativedelta(datetime.datetime(y, m, d, h, mm, s), currentDT)
    except:
        return "Timer " + mess + " complete!"
    return "Time until " + mess + ": "+ str(rd.years) +" years, "+ str(rd.months) +" months, "+ str(rd.days) +" days, "+ str(rd.hours) +" hours, "+ str(rd.minutes) +" minutes, " + str(rd.seconds) + " seconds."

# def GetTimeTill(mess, y, m, d, h, mm, s):
#     targetDT = datetime.datetime(y,m,d,h,s)
#     currentDT = datetime.datetime.utcnow()
#     diffDT = (targetDT - currentDT)
#
#     # Days
#     days = diffDT.days
#
#     # Hours
#     hours = int(diffDT.seconds / 60 / 60) - 1
#     if hours < 0:
#         days = 0
#         hours += 23
#
#     # Minutes
#     minutes = int(diffDT.seconds / 60) - 1 - ((1 + hours) * 60) # Reports for returning wrong minute, unable to reproduce
#
#     # Seconds
#     seconds = int(diffDT.seconds) - 1 - ((1 + hours) * 60 * 60) - ((1 + minutes) * 60)
#
#     return "time until " + mess + ": " + str(days) + " days, " + str(hours) + " hours, " + str(minutes) + " minutes, " + str(seconds) + " seconds."

# This was an old attempt but I'm not deleting it because i like the month thing
#
# def GetTimeTill(msg, y, m, d, h, mm, s):
#     currentDT = datetime.datetime.now()
#     #Years
#     year = y - currentDT.year - 1
#     yearout = str(year) + " years, "
#     if (year <= 0):
#         yearout = ""
#
#     # Month
#     month = m - currentDT.month - 1
#     monthout = str(month) + " months, "
#     if (month <= 0):
#         monthout = ""
#
#     # Day
#     # Determine how many days in current month
#     if month % 2 == 0:
#         # Months with 31 days
#         mdays = 31
#     else:
#         # Months with 30 days
#         mdays = 30
#     if month == 2:
#         # February exception
#         if year % 4 == 0:
#             mdays = 29
#         else:
#             mdays = 28
#
#     # Get day
#     day = d - currentDT.day - 1
#     dayout = str(day) + " days, "
#     if (day == 0):
#         dayout = ""
#
#     #Hour
#     hour = g - currentDT.hour - 1
#
#     # Minute
#     min = mm - currentDT.minute - 1
#
#     # Second
#     sec = s - currentDT.second - 1
#     return str(msg) + ": " + yearout + monthout + dayout + str(hour) + " hours, " + str(min) + " min, " + str(sec) + " sec."

# Run bot
client.run(token)
