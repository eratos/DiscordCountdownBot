# Important: This bot has been deactivated
Between the odd bug discovery, the monthly Heroku emails telling me I've used up my hours, and the fact that other bots exist for the same purpose, I've decided to put this bot to rest. If you'd still like to use the bot, feel free to download the source code and launch it under your own bot. Thanks to everyone who tried it!

That being said, you can still use my Smash Countdown Bot which counts down to only one specific hardcoded date in the wrong timezone which has already passed: https://github.com/Brettehwarrior/SmashCountdownBot

Another Countdown Bot by da_Cat: https://top.gg/bot/542150321288380457

Everything below this point has been kept for archiving purposes.

#
#
#
#
#

# Discord Countdown Bot
ADD COUNTDOWN BOT TO YOUR SERVER: https://discordapp.com/api/oauth2/authorize?client_id=553306817808302104&permissions=67584&scope=bot

A simple python Discord bot to return a countdown to custom date-times to the second.
This was made as a customizable future-proof improvement on my "Smash Countdown" Discord bot.

All times in UTC


# Commands
All commands are case insensitive

* 'time till [title]'

Returns the remaining time to the countdown specified with [title]



* 'new timer, [title], [year], [month], [day], [hour], [minute], [second]

Adds a new timer to timers.json with specified parameters that can be checked using the 'time till [title]' command
