'''
started writing 18/10/20
bot released to public on 02/03/21
bot decommisioned on 21/08/24

take careful care of this code. in its default state it doesn't have any protections against people uploading any sprites to it, including NSFW content.
it's designed for small private servers with friends, where everyone trusts each other to behave

if you want to limit people from uploading, you'll have to tweak the code to your specific use case
  https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.Member.guild_permissions

huge thanks to Demi for maintaining the generator and https://github.com/Rapptz for maintaining d.py

have fun, and try to not to break anything expensive

- Comhad <3
'''
from discord.ext import commands 
import discord, urllib, sys, datetime, aiohttp, io, re, extensions, json, wrapper

tokenFiles = json.load(open("auth.json", "r"))
startTime = datetime.datetime.now()
avatars = wrapper.CharacterDatabase()
token = tokenFiles["bot"] # the bot token from discord
prefix = tokenFiles["prefix"] # the prefix you want
newGenerator = tokenFiles["new_generator"] # 1 if to use the new generator by default, 0 if you don't
deleteMessage = tokenFiles["delete_message"] # 1 if you want to delete the message that was quoted, 0 if you don't
deleteCommand = tokenFiles["delete_command"] # 1 if you want to delete the command that quoted it, 0 if you don't

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")
# We need this for our own bot, it's taken by the module already

collectMessages = 30
commonColors = {
    'white' : (255, 255, 255),
    'blue' : (0, 0, 255),
    'red' : (255, 0, 0),
    'green' : (0, 255, 0),
    'yellow' : (255, 255, 0),
    'cyan' : (0, 255, 255) # add more
}


# Main functions of the bot

@bot.event
async def on_message(msg) :
    if not msg.guild : # don't reply in DM's
        return
    if msg.guild.me in msg.mentions : # see if the bot is pinged
        if not re.match(re.escape(prefix) + "(new|old){0,1}quote", msg.content) : # someone could be quoting the bot
            await msg.channel.send('My prefix is `' + prefix + '`, to change it, check the `README.md`')
    await bot.process_commands(msg)

async def _oldquote(msg, character, expression, color) :
    avatar = None
    # We change these later if we need to
    messageContents = msg.content
    # We only fill this if we find something suitable

    if character != None :
        avatar = "character=" + urllib.parse.quote(character, safe='') # Prevent parameter injection
    else :
        splitUrl = msg.author.avatar.url.split('.')
        splitUrl.pop()
        userIcon = '.'.join(splitUrl)
        avatar = "character=custom&url=" + userIcon + ".png?size=512" # The API won't support the webp format

        if expression != None and userIcon == None :
            avatar += "&expression=" + urllib.parse.quote(expression, safe='') # Add expression

    # The text box seems to only be able to take 90 characters, but seems to automaticly wrap words which will save me some time
    # Set an array of different text boxes to send
    allBoxes = []
    fileList = []
    if len(messageContents) > 90 : # If this message is over 90 characters than we split it
        splitText = messageContents.split(" ")
        msgBuffer = ""

        while len(splitText) != 0 :
            msgBuffer += splitText.pop(0) + " "
            if len(splitText) == 0 : # If this is the last one just give it it's own text box
                allBoxes.append(msgBuffer)
                break
            if len(msgBuffer) > 60 :  # I can only guess
                allBoxes.append(msgBuffer)
                msgBuffer = ""
                # Add message to boxes and clear the buffer for the next part

    else : # If it's not over 90 just give it its own box
        allBoxes.append(messageContents)

    boxNumber = 1
    for msgText in allBoxes :
        msgEncode = urllib.parse.quote(msgText, safe = '')
        textBox = "https://www.demirramon.com/gen/undertale_text_box.png?text={0}{1}&astrisk=true&{2}".format("%20color=" + urllib.parse.quote(color, safe='') + "%20" if color is not None else "", msgEncode, avatar)
        # It needs to be parsed incase it includes spaces

        # Download the textbox into files we can then send
        async with aiohttp.ClientSession() as session:
            async with session.get(textBox) as resp:
                if resp.status != 200:
                    raise Exception("Error downloading file : Non 200 status returned")
                    return
                data = io.BytesIO(await resp.read())
                fileList.append(discord.File(data, 'textbox' + str(boxNumber) + '.png'))
                boxNumber += 1
                # All the boxes need to be a different number, or they don't get through
    
    while len(fileList) > 10 : # Discord doesn't allow more than 10 files per message
        bufferFiles = []
        for i in range(10) :
            bufferFiles.append(fileList.pop(0))
        await msg.channel.send(files=bufferFiles)

    await msg.channel.send(files=fileList) # Just send the remaining files

async def _newquote(msg, character, expression, color) :
    if color == None :
        color = (255, 255, 255)
    elif re.findall("(#{0,1}[\dabcdefABCDEF]){6}", color) :
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4)) # stolen from stackoverflow
    else :
        try :
            color = commonColors[color]
        except KeyError :
            color = (255, 255, 255)
    fileList = []
    try :
        fileList = avatars.passthrough(msg, character, expression, color)
    except wrapper.SpriteNotFound :
        await msg.channel.send("I couldn't find that sprite!")
        return
    files = []
    for file in fileList :
        files.append(discord.File(file))
    while len(files) > 10 : # Discord doesn't allow more than 10 files per message
        bufferFiles = []
        for i in range(10) :
            bufferFiles.append(files.pop(0))
        await msg.channel.send(files=bufferFiles)
    await msg.channel.send(files=files)

@bot.command(name='quote', aliases=["newquote", "oldquote"], brief='Quote a message from a user', 
description='You can use this command to quote a message from a user, you can either quote using '+
'undertale sprites by using `oldquote` or using your own custom uploaded sprites using `newquote`!'+
'(you can also use `quote`, which is set to use the ' + ("new" if newGenerator else "old") + ' generator, you can change this using the `README.md`)\n\n' +
'You can quote a message by replying to it and saying `quote <character> <expression> <color>`, or by saying '+
'`quote <user> <character> <expression> <color>` and the bot will find the most recent message from that user and '+
'quote it!\n\nTo see all the characters you can use for `oldquote`, follow [this link](https://www.demirramon.com/en/help/undertale_text_box_generator_dev#char-codes), '+
'to see and add characters you can use with `newquote`, upload them to the bot, see the `help` command for more info.')
async def _quote(ctx, *args) :
    offset = 0 # this is used to determine where each item is in the array

    if ctx.message.reference == None : # if its quoted like normal
        if len(args) == 0 :
            raise discord.ext.commands.errors.MissingRequiredArgument(type('placeholder', (object,), {'name' : 'user'}))
        message = None
        messages = [message async for message in ctx.channel.history(limit=collectMessages)]
        skipBack = False 
        # If the user has pinged themselves, we don't want to quote them saying /quote
        # This determines if the message should be skipped

        offset = 1
        # if the user has used a ping in front of the characters, that means all the arguments are offset by one
        member = await commands.converter.MemberConverter().convert(ctx, args[0])
        # this is such a stupid hack but it works
    
        if(member == ctx.author) :
            skipBack = True

        for message in messages: 
            if (message.author == member) :
                if skipBack :
                    skipBack = False
                    continue
                    # Continue to the next iteration and skip this message
                    # if we know to skip it
                msg = message
                break # Break out of the loop, we've got the message

        if (msg == None) :
            await ctx.send("I couldn't find any messages by that user, I only look at the last " + str(collectMessages) + ", make sure to quote before " + str(collectMessages - 1) + " more messages appear!")
            return

    else :
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    
    character = args[0 + offset] if len(args) >= (1 + offset) else None
    expression = args[1 + offset] if len(args) >= (2 + offset) else "default"
    color = args[2 + offset] if len(args) >= (3 + offset) else None

    await ctx.message.add_reaction("\N{Anticlockwise Downwards and Upwards Open Circle Arrows}") # let people know it's ticking over

    if ctx.invoked_with == "oldquote" :
        method = _oldquote
    elif ctx.invoked_with == "newquote" :
        method = _newquote
    else :
        if newGenerator :
            method = _newquote
        else :
            method = _oldquote
    
    await method(msg, character, expression, color)

    try :
        if deleteMessage == 1 : # if this is set, delete the quoted message
            await msg.delete()
        if deleteCommand == 1 : # if this is set, delete the command
            await ctx.message.delete()
        else :
            await ctx.message.add_reaction("\N{White Heavy Check Mark}")
            await ctx.message.remove_reaction("\N{Anticlockwise Downwards and Upwards Open Circle Arrows}", bot.user)
            # tell the user it's done
    except discord.Forbidden :
        await ctx.channel.send("The bot is missing some permissions, either `manage messages` or `add reactions`")

@bot.command(name='listsprites', brief='List all sprites for this server',
description='This will show all the sprites that have been uploaded for this guild, in a \'`name`, `expression`\' manner, '+
'upload them at the dashboard, use `dashboard` to get your dashboard link')
async def _listsprites(ctx) :
    sprites = avatars.listSprites(ctx.guild.id)
    msg = "**All sprites for this server**\n\n"
    for each in sprites :
        msg += each[0] + "," + each[1] + "\n"
    await ctx.channel.send(msg)

@bot.command(name='showsprite', brief='Show a sprite with the name and expression',
description='Show a picture of a sprite in an embed')
async def _showsprite(ctx, character, expression = "default") :
    sprite = None
    try :
        sprite = avatars.getSprite(character, expression)
    except wrapper.SpriteNotFound :
        await ctx.channel.send("I couldn't find that sprite!")
    file=discord.File(sprite, "sprite.png")
    embed = discord.Embed(title='Sprite', description='`' + character + '` with expression `' + expression + '`')
    embed.set_image(url="attachment://sprite.png")
    await ctx.channel.send(file=discord.File(sprite, "sprite.png"), embed=embed)

@bot.command(name='addsprite', brief='Add a sprite to the bot',
description='To use this command, do `addsprite character expression` along with uploading your image')
async def _addsprite(ctx, character, expression = "default") :
    msg = ctx.message
    if len(msg.attachments) != 1 :
        await ctx.channel.send("Sorry, you didn't send the right amount of attachments! Make sure you only send one!")
        return
    image = await msg.attachments[0].read()
    avatars.addSprite(character, expression, image)
    await ctx.message.add_reaction("\N{White Heavy Check Mark}") # tell the user it's done

# Command to test server response time
@bot.command(name='ping', brief='Show the response times for the API the bot uses',
description='Ask the bot to send a GET request to a server to see the response time for it')
async def _ping(ctx) :
    message = await ctx.channel.send("Processing...")
    sites = ["discord.com", "demirramon.com"]
    timeEmbed = discord.Embed(title='Ping times', 
    description="These are the ping times for the sites the bot is using.\n\n"+
    "A response time under 5.0 is good, and the status code should be 200. Anything "
    "in the 500 can only be fixed by the people that own the site.")
    for each in sites :
        response = extensions.ConnectionTime.ping(each)
        if response[0] == -1 :
            timeEmbed.add_field(name=each, value="Error occured, site is probably down", inline=False)
        else :
            timeEmbed.add_field(name=each, value="Response time : " + str(response[0])[:5] + "\nStatus code : " + str(response[1]), inline=False)
    await message.edit(content="", embed=timeEmbed)

# Command to report info on bot
@bot.command(name='info', brief='Show some technical info on the bot',
description='Some info about the bot, such as uptime, server count etc')
async def _info(ctx) :
    embed = discord.Embed(title="Bot info", description="Various technical info about the bot")

    uptime = str(datetime.datetime.now() - startTime)
    embed.add_field(name = "Uptime :", value = "`" + uptime + "`", inline = False)

    pythonVersion = str(sys.version_info.major) + "." + str(sys.version_info.minor) + "." + str(sys.version_info.micro)
    embed.add_field(name = "Python version :", value = "`" + pythonVersion + "`", inline = False)

    library = "discord.py : " + discord.__copyright__
    embed.add_field(name = "Library info :", value = "`" + library + "`", inline=False)

    await ctx.channel.send(embed = embed)

@bot.command(name='debug', brief='Help debug why bot won\'t work in a certain channel',
description='Use this if the bot is erroring alot of not responding to messages') 
async def _debug(ctx) :
    embed = discord.Embed(title = "Permissions", description = "These are my permissions for " + ctx.channel.mention + ". "
        "These should all be granted else the bot will have some trouble in this channel. " + 
        "If the issues still occur, make sure the bot role is above any other bot roles like in the picture below.")
    granted = "\N{White Heavy Check Mark}"
    notGranted = "\N{Cross Mark}"
    if not ctx.channel.permissions_for(ctx.me).embed_links :
        await ctx.channel.send("Please allow me to embed links to send a full description of my permissions for " + ctx.channel.mention)
        return
    permissionsRequired = ["view_channel", "read_message_history", "send_messages", "embed_links", "add_reactions", "attach_files"]
    for each in permissionsRequired :
        isGranted = eval("ctx.channel.permissions_for(ctx.me)." + each)
        message = (granted + " Granted") if isGranted else (notGranted + " Not granted")
        embed.add_field(name = "`" + each + "`", value = message, inline = False)
    embed.set_image(url="https://comhad.github.io/img/roles.PNG")
    await ctx.channel.send(embed = embed)


# Error handler

@bot.event
async def on_command_error(ctx, error):
    try :
        if isinstance(error, commands.errors.CommandNotFound) :
            # This is just when someone prefixes a message with our prefix and we don't have the command
            # Chances are it was just another bot with the same prefix
            return

        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument) :
            await ctx.channel.send("Sorry, an argument was missing from the command! Make sure you supply all required commands! Check the `/help` page for more info.")
            return

        if isinstance(error, discord.ext.commands.errors.MemberNotFound) :
            await ctx.channel.send("Sorry, I couldn't find that user! Be careful of unicode characters! (P.S., you can use pings or just copy the id of the user you want to quote!)")
            return

        if isinstance(error, extensions.NoPrivateMessage) :
            await ctx.channel.send("Sorry, this command doesn't work in DM's!")
            return

        if isinstance(error, discord.ext.commands.errors.UnexpectedQuoteError) :
            await ctx.channel.send("Sorry, you can't use the `’` character!")
            return

        # Custom error from extensions

        if isinstance(error, discord.ext.commands.errors.ConversionError) :
            if isinstance(error.original, extensions.ForbiddenCharacters) :
                await ctx.channel.send("Sorry, one of your arguments contained forbidden characters!\n\n*" + str(error.original) + "*\n\n" +
                "P.S.: If you're trying to use `color=` and then a color, try using just the color on it's own!", 
                allowed_mentions=discord.AllowedMentions.none()) # Prevent an @ everyone vulnerability
                print("Forbidden characters : " + str(error.original), flush=True)
                return

        else :
            print("# # # ERROR # # #")
            print(type(error))
            print(str(error), flush=True)
            await ctx.channel.send("Sorry, something went wrong :( \nMake sure the bot has enough permissions by using the `debug` command, and you can check if the sites are up with `ping`")
            return
    except Exception as e :
        print("An error occured when handling the error : " + str(e), flush=True) 
        # This isn't ideal, but if someone does something wrong and the bot can't send back an error, it will crash

# Log when the bot comes online, this is useful for knowing when it crashes

@bot.event
async def on_ready():
    print(bot.user.name + "#" + bot.user.discriminator + " online",flush=True)
    status = discord.Activity(
        type=discord.ActivityType.listening,
        name=prefix + "help"
    )
    await bot.change_presence(activity=status)

class HelpCommand(commands.HelpCommand) :
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        embed = discord.Embed(title = "**Command list**", description='Here are the commands, for the bot, you `help <command>` to get more info')
        commands = bot.commands
        for command in commands :
            if command.name in ["eval", "help"] : # hidden commands
                continue
            embed.add_field(name=command.name, value=command.brief or "nothing", inline=False)
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        channel = self.get_destination()
        embed = discord.Embed(title = command.name)
        embed.add_field(name='Overview', value=command.brief, inline=False)
        embed.add_field(name='Description', value=command.description, inline=False)
        await channel.send(embed=embed)

    async def command_not_found(self, command) :
        return "That isn't one of my commands!"

bot.help_command = HelpCommand()
bot.intents.message_content = True
bot.run(token)
