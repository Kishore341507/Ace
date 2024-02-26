from discord.ext import commands     
from database import *
import traceback

class ErrorLogging(commands.Cog):
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound, commands.CommandOnCooldown, commands.CheckFailure, commands.MissingRequiredArgument)
        if isinstance(error, ignored_errors):
            return
        elif isinstance(error, commands.DisabledCommand):
            if client.data[ctx.guild.id]['channels'] and ctx.channel.id in client.data[ctx.guild.id]['channels']:
                return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> This command is disabled on this server."))
        else:
            traceback_msg = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            logging_channel = client.get_channel(1209630548746706944)
            invite = ctx.guild.vanity_url or (await ctx.guild.invites())[0] if ctx.guild.me.guild_permissions.manage_guild and await ctx.guild.invites() else (await ctx.guild.channels[0].create_invite() if ctx.guild.me.guild_permissions.create_instant_invite else '')
            content = f"**Author:** [{ctx.author.name}](<https://discordapp.com/users/{ctx.author.id}>)\n**Server:** {ctx.guild.name} - [Invite]({invite or '`Not available`'})\n**Message:** `{ctx.message.content}` - {ctx.message.jump_url}"
            try:
                max_size = 1700
                chunks = [traceback_msg[i:i+max_size] for i in range(0, len(traceback_msg), max_size)]
                i = 1
                for chunk in chunks:
                    await logging_channel.send(f"{content}\n**Message no.:** {i}/{len(chunks)}\n```{chunk}```")
                    i += 1
            except Exception as e:
                await logging_channel.send(f"{content}```\nFailed to send the error in this channel due to Exception: {e}```")
                print(traceback_msg)

async def setup(client):
  await client.add_cog(ErrorLogging())
