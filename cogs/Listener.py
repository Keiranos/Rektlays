import discord
from discord.ext import commands
import datetime as dt
from config import QUEUE, STAFF, RED, WHITELIST

Approved = "👍"
Denied = "👎"


class Listener(commands.Cog, name="Listener"):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = dt.datetime.now()

    @commands.Cog.listener()
    async def on_message(self, message):
        whitelist = message.guild.get_role(WHITELIST)
        if whitelist not in message.author.roles:
            if message.attachments:
                await message.delete(delay=1)
                for info in message.attachments:
                    try:
                        AttachmentURL = info.proxy_url
                        channel = self.bot.get_channel(QUEUE)
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


def setup(bot):
    bot.add_cog(Listener(bot))
