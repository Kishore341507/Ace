import discord
from discord.ext import commands     
from database import client
import traceback
from commands.owner.help import helpCommandView
from utils import bembed, default_prefix

class ErrorLogging(commands.Cog):

    def __init__(self):
        self.bad_argument_cooldown_mapping = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.member)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound, commands.CommandOnCooldown, commands.CheckFailure, commands.MissingRequiredArgument)
        if isinstance(error, ignored_errors):
            return
        elif isinstance(error, commands.DisabledCommand):
            if client.data[ctx.guild.id]['channels'] and ctx.channel.id in client.data[ctx.guild.id]['channels']:
                return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> This command is disabled on this server."))
        elif isinstance(error, (commands.BadArgument, ValueError, commands.errors.BadLiteralArgument)):
            cooldown = self.bad_argument_cooldown_mapping.get_bucket(ctx.message)
            retry_after = cooldown.update_rate_limit()
            if not retry_after:
                command = ctx.command
                embed = bembed(">>> ", discord.Color.blue())
                embed.set_author(name=f"Help for {command.name.title()} command.")
                if command.description:
                    embed.description = embed.description + f"**Description:** `{command.description}`\n"
                if command.help:
                    embed.description = embed.description + f"**Help:** `{command.help}`\n"
                if command.usage:
                    embed.description = embed.description + f"**Usage:** `{client.data[ctx.guild.id]['prefix'] or default_prefix}{command.name} {command.usage}`\n"
                else:
                    embed.description = embed.description + f"**Usage:** `{client.data[ctx.guild.id]['prefix'] or default_prefix}{command.name} {command.signature}`\n"
                if command.cooldown:
                        embed.description = embed.description + f"**Cooldown:** `{command.cooldown.rate} per {command.cooldown.per:.0f} seconds.`\n"
                if command.aliases:
                    embed.description = embed.description + f"**Aliases:** `{', '.join(alias for alias in command.aliases)}`\n"
                await ctx.reply(content=f"**{ctx.message.author.mention} {error}**", embed=embed , view= helpCommandView())
            elif isinstance(error, discord.HTTPException) and error.status == 429:
                retry_after = int(error.response.headers.get('Retry-After', 0))
                await ctx.reply(embed=bembed(f'I am being rate limited, please after {retry_after} seconds.', discord.Color.brand_red()).set_author(ctx.author))
            else:
                return
        else:
            traceback_msg = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            invite = ctx.guild.vanity_url or (await ctx.guild.invites())[0] if ctx.guild.me.guild_permissions.manage_guild and await ctx.guild.invites() else (await next((c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)), None).create_invite() if ctx.guild.me.guild_permissions.create_instant_invite and next((c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)), None) else '')
            content = f"**Author:** [{ctx.author.name}](<https://discordapp.com/users/{ctx.author.id}>)\n**Server:** {ctx.guild.name} - [Invite]({invite or '`Not available`'})\n**Message:** `{ctx.message.content}` - {ctx.message.jump_url}"
            try:
                max_size = 1700
                chunks = [traceback_msg[i:i+max_size] for i in range(0, len(traceback_msg), max_size)]
                i = 1
                for chunk in chunks:
                    await client.error_logging_ch.send(f"{content}\n**Message no.:** {i}/{len(chunks)}\n```{chunk}```")
                    i += 1
            except Exception as e:
                await client.error_logging_ch.send(f"{content}```\nFailed to send the error in this channel due to Exception: {e}```")
                print(traceback_msg)

async def setup(client):
  await client.add_cog(ErrorLogging())