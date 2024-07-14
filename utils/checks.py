from database import client
from discord.ext import commands

def check_perms(ctx) -> bool:
    return client.data[ctx.guild.id]['manager'] in [role.id for role in ctx.author.roles] or ctx.author.guild_permissions.manage_guild

def check_channel(ctx) ->bool : 
    if client.data[ctx.guild.id]['disabled'] and ctx.command.name in client.data[ctx.guild.id]['disabled'] :
        raise commands.DisabledCommand("Command disabled in Server")
    return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels']