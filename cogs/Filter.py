import discord
from discord.ext import commands
import datetime as dt
from config import RED, GREEN
import aiosqlite

Approved = "👍"
Denied = "👎"


class Filter(commands.Cog, name="Filter"):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = dt.datetime.now()

    @commands.Cog.listener()
    async def on_message(self, message):
        async with aiosqlite.connect("data.db") as db:
            WHITELIST = await db.execute("SELECT Whitelist FROM Config")
            WHITELIST = await WHITELIST.fetchone()
            WHITELIST = WHITELIST[0]
        whitelist = message.guild.get_role(WHITELIST)
        if whitelist not in message.author.roles or message.author.roles is None:
            if message.attachments:
                await message.delete(delay=1)
                for info in message.attachments:
                    try:
                        AttachmentURL = info.proxy_url
                        async with aiosqlite.connect("data.db") as db:
                            QUEUE = await db.execute("SELECT Queue FROM Config")
                            QUEUE = await QUEUE.fetchone()
                            QUEUE = QUEUE[0]
                        channel = self.bot.get_channel(QUEUE)
                        async with aiosqlite.connect("data.db") as db:
                            STAFF = await db.execute("SELECT Staff FROM Config")
                            STAFF = await STAFF.fetchone()
                            STAFF = STAFF[0]
                        msg = await channel.send(
                            f"<@&{STAFF}> A new message with an attachment has been detected! Please check this "
                            f"and react bellow to approve this message! UserID - {message.author.id} - "
                            f", {AttachmentURL} , Channel ID: {message.channel.id}")
                        await msg.add_reaction(Approved)
                        await msg.add_reaction(Denied)
                    except:
                        pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass
        elif Denied == payload.emoji.name:
            channel = self.bot.get_channel(payload.channel_id)
            partial = channel.get_partial_message(payload.message_id)
            message = await partial.fetch()
            content = message.content.split(": ")
            author = message.content.split("- ")
            user = self.bot.get_user(int(author[1]))
            postchannel = int(content[1])
            postchannel = self.bot.get_channel(postchannel)
            em = discord.Embed(title="⛔ Denied ⛔",
                               description=f"{user.mention}, your post violates our rules/discord TOS"
                               , colour=RED)
            em.timestamp = dt.datetime.utcnow()
            await postchannel.send(f"{user.mention}", embed=em)
            await message.delete(delay=1)
        elif Approved == payload.emoji.name:
            channel = self.bot.get_channel(payload.channel_id)
            partial = channel.get_partial_message(payload.message_id)
            message = await partial.fetch()
            content = message.content.split(": ")
            image = message.content.split(" ,")
            postchannel = int(content[1])
            postchannel = self.bot.get_channel(postchannel)
            await postchannel.send(f"This image has been checked and verified as safe: {image[1]}")
            await message.delete(delay=1)
        else:
            pass

    @commands.command()
    async def config(self, ctx, Queue: discord.TextChannel, Whitelist: discord.Role, Staff: discord.Role):
        QueueID = Queue.id
        WhitelistID = Whitelist.id
        StaffID = Staff.id
        async with aiosqlite.connect("data.db") as db:
            await db.execute("UPDATE Config SET Queue = ?, Whitelist = ?, Staff = ?",
                             (QueueID, WhitelistID, StaffID))
            await db.commit()
        em = discord.Embed(title="Success!", description=f"The Queue channel is now {Queue.mention}\n"
                                                         f"The Whitelist role is now {Whitelist.mention}\n"
                                                         f"The Staff role is now {Staff.mention}",
                           colour=GREEN)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Filter(bot))
