# QuoteBot
Hey there, welcome to the QuoteBot code repo! This is where the code that ran QuoteBot is stored after shutdown, if you want to know more about the shutdown, please [read this](https://gist.github.com/comhad/f7b6fe04b0733058f555c2e0fa75e8bd).

# Notes
If you used QuoteBot, you would have known there was a dashboard to upload sprites. That's not included in this code. It would have made an already complex system to impractical to release as source code. So instead, I've reimplemented a local database system I used for testing a while ago, see the help command for more info.

There's two different types of generators, the old generator refers to the generator ran by Demi, and the new generator refers to the one created by me. I can't entirely remember why I seperated them, but the new generator uses custom sprites, where the old generator just uses discord profile pictures and UNDERTALE/DELTARUNE sprites, use `help quote` for more info on these.

**This tutorial assumes you have some experience coding**

# How do I use it?
You'll need to download the repo to your computer. After this, start by editing `auth.json` to contain the following details.

```
{
	"bot":"yourtoken",
	"prefix":",",
	"new_generator" : 1,
	"delete_message" : 0,
	"delete_command" : 0
}
```

Check `quotebot.py` for more details on what these mean.

Next, create a `sprites.db` using `sqlite3 sprites.db`, and running `.read custom_db.sql` when in the terminal.

Then install `requirements.txt` using `pip`.

Once this is done, clone `https://github.com/comhad/textbox-generator` into the same directory, and change the name of the folder to `tb`.