import discord
from discord.ext import commands   
import re
import requests
import time

# Univeral stuff

class SafeCharacters(commands.Converter) :
    safeRegex = re.compile("[^a-zA-Z\-\d#]") # These are all the characters that are allowed through

    async def convert(self, ctx, argument) :
        if self.safeRegex.search(argument) :
            # If something not permitted is found
            raise ForbiddenCharacters("The string " + argument + " contains forbidden characters")

        return argument # Just return the argument if nothing was found

class ConnectionTime :
    def ping(host) :
        try :
            before = time.perf_counter()
            returnCode = requests.get("https://" + host + "/", timeout=5).status_code
            after = time.perf_counter()
            timeTaken = after - before
            return timeTaken, returnCode
        except :
            return -1, -1

# User stuff

class Status(commands.Converter):
    statusList = { 
        "listening" : discord.ActivityType.listening,
        "competing" : discord.ActivityType.competing,
        "streaming" : discord.ActivityType.streaming,
        "playing" : discord.ActivityType.playing }

    async def convert(self, ctx, argument):
        status = None
        try :
            status = self.statusList[argument]
        except KeyError:
            raise InvalidStatus("The status (" + argument + ") was not valid")
        return status

# Error handling

class ExtensionError(Exception) :
    pass

class InvalidStatus(ExtensionError) :
    pass

class ForbiddenCharacters(ExtensionError) :
    pass

# Save space in main code
class NoPrivateMessage(commands.CheckFailure) :
    pass

class PermissionDenied(commands.CheckFailure) :
    pass
