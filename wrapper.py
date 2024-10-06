'''
i don't entirely remember what the alias table was related to, this database was only supposed to be temporary

ay, it doesn't take up much space, and if it ain't broke don't fix it
'''
import tb.textbox as textbox
import sqlite3, io, os, requests, base64, requests_cache, hashlib

class CharacterDatabase :
    workingFolder = "/tmp/quotebot"

    def __init__(self) :
        self.connection = sqlite3.connect("sprites.db")
        self.database = self.connection.cursor()

    def listSprites(self, serverid) :
        sprites = self.database.execute("SELECT name, expression FROM sprites").fetchall()
        return sprites

    def getSprite(self, alias, expression = "default") :
        spriteName = self.database.execute("SELECT spritename FROM aliases WHERE alias = (?)", (alias,)).fetchone()[0]
        imageContent = self.database.execute("SELECT imagecontents FROM sprites WHERE name = (?) AND expression = (?)", (spriteName, expression,)).fetchone()[0]
        fp = io.BytesIO(bytes(imageContent))
        return fp
    
    def addSprite(self, name, expression, imageContent) :
        if self.database.execute("SELECT name from sprites where name = (?) and expression = (?)", (name, expression,)).fetchone() != None :
            raise ValueError("Sprite already exists")
        self.database.execute("INSERT INTO sprites (name, expression, imagecontents) VALUES (?, ?, ?)", (name, expression, imageContent))
        self.database.execute("INSERT INTO aliases (spritename, alias) VALUES (?, ?)", (name, name,))
        self.connection.commit()

    def passthrough(self, msg, character, expression, color) :
        if not os.path.exists(self.workingFolder):
            os.makedirs(self.workingFolder)
        else:    
            pass

        if not os.path.exists(self.workingFolder + "/" + str(msg.channel.id)):
            os.makedirs(self.workingFolder + "/" + str(msg.channel.id))
        else:    
            pass

        f = textbox.Features()
        f.setBackground(f.listBackgrounds()[0])
        f.setFont(f.listFonts()[0])
        if character != None :
            f.setAvatar(self.getSprite(character, expression))
        else :
            avatarUrl = msg.author.avatar.url + ".png" if msg.author.avatar else "https://cdn.discordapp.com/embed/avatars/1.png"
            file = requests.get(avatarUrl, stream=True).raw
            f.setAvatar(file)
        f.setColor(color)
        g = textbox.Generate(f)
        fileList = g.bulkMake(msg.content, self.workingFolder + "/" + str(msg.channel.id))
        return fileList

class SpriteNotFound(NameError) :
    pass
