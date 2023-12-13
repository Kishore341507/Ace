# from enum import _EnumMemberT
from operator import truediv
import discord
from discord.ext import commands
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing
from easy_pil import Editor, Canvas, load_image_async, Font
from numerize import numerize
from discord.ui import Button, View, Select, TextInput
import re
from discord import app_commands
from easy_pil import Editor, Canvas, load_image_async, Font

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time = time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))       
        return time , argument

class SingleInput(discord.ui.Modal, title='...'):
    def __init__(self, question, placeholder):
        super().__init__()
        self.question = question
        self.placeholder = placeholder
        self.value = None
        self.input = discord.ui.TextInput(
            label=self.question, placeholder=self.placeholder)
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.input.value
        await interaction.response.defer()

class SingleInputLong(discord.ui.Modal, title='...'):
    def __init__(self, question, placeholder):
        super().__init__()
        self.question = question
        self.placeholder = placeholder
        self.value = None
        self.input = discord.ui.TextInput(
            label=self.question, placeholder=self.placeholder , style = discord.TextStyle.long)  
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.input.value
        await interaction.response.defer()


class EcoManager(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.emoji = ["\U0001f1e6", "\U0001f1e7", "\U0001f1e8", "\U0001f1e9", "\U0001f1ea", "\U0001f1eb", "\U0001f1ec", "\U0001f1ed", "\U0001f1ee", "\U0001f1ef",
                      "\U0001f1f0", "\U0001f1f1", "\U0001f1f2", "\U0001f1f3", "\U0001f1f4", "\U0001f1f5", "\U0001f1f6", "\U0001f1f7", "\U0001f1f8", "\U0001f1f9"]

    


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def guess(self,ctx, question : str,word:str , hint : str = None):
 
        word = word.lower()
        embed = bembed()
        embed.title = question
        # embed = discord.Embed( color= discord.Color.blue()  , title= question )
        embed.set_author( name= ctx.guild.name , icon_url = ctx.guild.icon.url )
        # embed.set_thumbnail( url= "https://cdn.discordapp.com/attachments/1055175132085223484/1076941636845707435/iqoo_11_neo7_iqoo_iqoo_smartphones_1.png" )
        if hint : 
            embed.set_footer( text= f"Hint : {hint}" )
        await ctx.interaction.response.send_message( "done" , ephemeral = True)
        await ctx.channel.send(embed = embed)
        def check(m):
            return (m.content).lower() == str(word) and m.channel == ctx.channel
        
        msg = await client.wait_for("message",check = check)
        await ctx.send (f"{msg.author.mention} Guessed the right answer, The answer is **{word}**")

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def drop(self , ctx, name:str , code : typing.Optional[str] = "claim" , channel : typing.Optional[discord.TextChannel] = None , role : typing.Optional[discord.Role] = None , thumbnail_url : str = None ):
    #   embed = discord.Embed(color= 0x , title = name )
    #   embed.set_author(name = "Server Wars" , icon_url= ctx.guild.icon)
      if ctx.guild.id != 753505988417683558 :
          return
      embed = bembed()
      embed.title = name
      embed.set_thumbnail(url= thumbnail_url)
      embed.set_footer( text = "Be quick, Write the code in the image above before someone else does!" )
      channel = channel or ctx.channel
      role = role

      background = Editor("CODE.png")
      poppins = Font.montserrat(size=80 , variant = "bold")
      background.text(
            (40, 20),
            f"{code}",
            font=poppins,
            color="white",
            )
      file = discord.File(fp=background.image_bytes, filename="code.png")  
      embed.set_image(url = "attachment://code.png")

      await channel.send(file = file , embed = embed)
      await ctx.send("done" , ephemeral = True)
      def check(m):
        if role :
            return (m.content == code ) and (role in m.author.roles )
        else :
            return (m.content == code )

  
      msg1 = await client.wait_for('message', check=check , timeout = 120)
      await msg1.reply("Congratulations! 🎉  You have claimed a 🍰 Successfully.")
      if ctx.guild.id == 753505988417683558 :
          send_channel = ctx.guild.get_channel(1150393364110376970)
          try :
                await send_channel.send(f"[{msg1.author} winner]({msg1.jump_url})")
          except :
                await ctx.author.send(f"[{msg1.author} winner]({msg1.jump_url})")
              
      else :  
        await ctx.author.send(f"[{msg1.author} winner]({msg1.jump_url})")

    @commands.hybrid_command(aliases = ['enable' , 'disable' , 'disable-command' , 'enable-command' , 'disablecommand' , 'enablecommand' ])
    @commands.guild_only()
    @commands.check(check_perms)
    async def command( self , ctx , * , command_name = None ) :
        
        if command_name :
            command = client.get_command(command_name)
        embed = bembed()
        if command_name is None :
            pass
        elif command is None :
            embed.description = "Command Not Found"
        elif command.cog_name == "EcoManager" :
            embed.description = "You Can't Disable Manager Commands"
        elif client.data[ctx.guild.id]['disabled'] and command.name in client.data[ctx.guild.id]['disabled'] :
            view = Confirm(ctx.author)
            await ctx.send(f'**{command.name}** is disable , Want to enable it ?' , view = view)
            await view.wait() 
            if view.value :
                await client.db.execute("UPDATE guilds SET disabled = ARRAY_REMOVE( disabled , $1) WHERE id = $2",command.name ,ctx.guild.id)
                client.data[ctx.guild.id]['disabled'].remove(command.name)
                embed.description = f"**{command.name} is now Enabled**"
            else :
                return
        else :
            view = Confirm(ctx.author)
            await ctx.send(f'**{command.name}** is Enable , Want to disable it ?' , view = view)
            await view.wait()
            if view.value :
                await client.db.execute("UPDATE guilds SET disabled = ARRAY_APPEND( disabled , $1) WHERE id = $2",command.name ,ctx.guild.id)
                try :
                    client.data[ctx.guild.id]['disabled'].append(command.name)
                except :
                    client.data[ctx.guild.id]['disabled'] = [command.name]
                embed.description = f"**{command.name} is now Disabled**"
            else :
                return
        
        if client.data[ctx.guild.id]['disabled'] is None :
            client.data[ctx.guild.id]['disabled'] = []
        embed.add_field( name= 'Enable Commands' , value = f"```{ ' , '.join([command.name for command in client.commands if command.name not in client.data[ctx.guild.id]['disabled'] ])}```" , inline = False)
        embed.add_field( name= 'Disable Commands' , value = f"```{ ' , '.join([command for command in client.data[ctx.guild.id]['disabled']]) or 'None' }```")
        
        await ctx.send(embed = embed)
        
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def addmoney(self, ctx, target: typing.Union[discord.Member, discord.Role],  amount: amountconverter,  location: typing.Literal['bank', 'cash', 'pvc'] = "bank"):
        try:
            amount = int(amount)
        except ValueError:
            await ctx.send(discord.Embed(description="Not a valid amount input!"), delete_after=5)
            return

        if type(target) == discord.Member:

            member = target

            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, ctx.guild.id)
            if bal is None:
                await open_account(ctx.guild.id, member.id)

            if location == "cash":
                await client.db.execute("UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **Cash** coins added in {member.name}'s account")
            elif location == "pvc":
                await client.db.execute("UPDATE users SET pvc = pvc + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **pvc** coins added in {member.name}'s account")
            else:
                await client.db.execute("UPDATE users SET bank = bank + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **bank** coins added in {member.name}'s account")

        elif type(target) == discord.Role:
            role = target
            await ctx.channel.typing()
            await ctx.defer()

            if target == ctx.guild.default_role :
                if location == "cash":
                    await client.db.execute("UPDATE users SET cash = cash + $1  WHERE  guild_id = $2", amount, ctx.guild.id)
                elif location == "pvc":
                    await client.db.execute("UPDATE users SET pvc = pvc + $1  WHERE guild_id = $2", amount, ctx.guild.id)
                else:
                    await client.db.execute("UPDATE users SET bank = bank + $1  WHERE guild_id = $2", amount, ctx.guild.id)
            else : 
                for member in role.members:
                    if member.bot:
                        continue
                    bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, ctx.guild.id)
                    if bal is None:
                        await open_account(ctx.guild.id, member.id)
                    if location == "cash":
                        await client.db.execute("UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                    elif location == "pvc":
                        await client.db.execute("UPDATE users SET pvc = pvc + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                    else:
                        await client.db.execute("UPDATE users SET bank = bank + $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
            await ctx.send(embed=discord.Embed(description=f"**{amount}** **{location}** coins added in {len(role.members)} accounts"))


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def removemoney(self, ctx, target: typing.Union[discord.Member, discord.Role],  amount: amountconverter,  location: typing.Literal['bank', 'cash', 'pvc'] = "bank"):
        try:
            amount = int(amount)
        except ValueError:
            await ctx.send(discord.Embed(description="Not a valid amount input!"), delete_after=5)
            return

        if type(target) == discord.Member:

            member = target

            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, ctx.guild.id)
            if bal is None:
                await open_account(ctx.guild.id, member.id)

            if location == "cash":
                await client.db.execute("UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **Cash** coins removed from {member.name}'s account")
            elif location == "pvc":
                await client.db.execute("UPDATE users SET pvc = pvc - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **pvc** coins removed from {member.name}'s account")
            else:
                await client.db.execute("UPDATE users SET bank = bank - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                await ctx.send(f"**{amount}** **bank** coins removed from {member.name}'s account")

        elif type(target) == discord.Role:
            role = target
            await ctx.channel.typing()
            await ctx.defer()


            if target == ctx.guild.default_role :
                if location == "cash":
                    await client.db.execute("UPDATE users SET cash = cash - $1  WHERE  guild_id = $2", amount, ctx.guild.id)
                elif location == "pvc":
                    await client.db.execute("UPDATE users SET pvc = pvc - $1  WHERE guild_id = $2", amount, ctx.guild.id)
                else:
                    await client.db.execute("UPDATE users SET bank = bank - $1  WHERE guild_id = $2", amount, ctx.guild.id)
            else : 
                for member in role.members:
                    if member.bot:
                        continue
                    bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, ctx.guild.id)
                    if bal is None:
                        await open_account(ctx.guild.id, member.id)
                    if location == "cash":
                        await client.db.execute("UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                    elif location == "pvc":
                        await client.db.execute("UPDATE users SET pvc = pvc - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
                    else:
                        await client.db.execute("UPDATE users SET bank = bank - $1  WHERE id = $2 AND guild_id = $3", amount, member.id, ctx.guild.id)
            
            await ctx.send(embed=discord.Embed(description=f"**{amount}** **{location}** coins removed from {len(role.members)} accounts"))

    # @commands.hybrid_command(aliases=["createitem"])
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def additem(self, ctx, *, name: str):

    #     ecoembed = discord.Embed(color=0xF7C906)
    #     ecoembed.set_author(name=ctx.author, url=None,
    #                         icon_url=ctx.author.display_avatar.url)
    #     ecoembed.title = f'Item Info'
    #     ecoembed.add_field(name="Name", value=name)
    #     # ecoembed.add_field(name="item_id", value=item_id)
    #     await ctx.send("**Enter the price of item !!!**", embed=ecoembed)
    #     await asyncio.sleep(1)

    #     def check1(m):
    #         try:
    #             return int(m.content) > 0 and m.author == ctx.author
    #         except ValueError:
    #             return 0

    #     msg1 = await client.wait_for('message', check=check1, timeout=120)
    #     price = int(msg1.content)
    #     ecoembed.add_field(name="Price", value=f"{coin(ctx.guild.id)} {price}")

    #     await ctx.send("**Enter the selling price of item , 0 for skip !!!**", embed=ecoembed)

    #     def check2(m):
        #     try:
        #         x = int(m.content)
        #         return int(m.content) >= 0 and m.author == ctx.author
        #     except ValueError:
        #         return 0
        # msg2 = await client.wait_for('message', check=check2, timeout=120)
        # sell_price = int(msg2.content)
        # ecoembed.add_field(name="Sell Price", value=f"{coin(ctx.guild.id)} {sell_price}")

        # await ctx.send("*Enter the **reward role id*** (example - 1010837286184812646)", embed=ecoembed)

        # def check3(m):
        #     try:
        #         x = int(m.content)
        #         role = m.guild.get_role(x)
        #         return 1 and m.author == ctx.author
        #     except ValueError:
        #         return 0
        # msg3 = await client.wait_for('message', check=check3, timeout=120)
        # role = msg3.guild.get_role(int(msg3.content))

        # ecoembed.add_field(name="Role given", value=f"{role.mention}")

        # await ctx.send("*Enter the **required role id*** (example - 1010837286184812646) , 0 for skip", embed=ecoembed)

        # def check4(m):
        #     try:
        #         x = int(m.content)
        #         if x == 0:
        #             r_role = None
        #         else:
        #             r_role = m.guild.get_role(x)
        #         return 1 and m.author == ctx.author
        #     except ValueError:
        #         return 0
        # msg4 = await client.wait_for('message', check=check4, timeout=120)
        # if int(msg4.content) == 0:
        #     r_role = msg4.guild.default_role
        # else:
        #     r_role = msg4.guild.get_role(int(msg4.content))
        # ecoembed.add_field(name="Role required", value=f"{r_role.mention}")

        # await ctx.send("Write description about item", embed=ecoembed)

    #     def check5(m):
    #         return m.author == ctx.author
    #     msg5 = await client.wait_for('message', check=check5, timeout=120)
    #     info = msg5.content
    #     ecoembed.add_field(name="Description", value=info, inline=False)

    #     await self.client.db.execute('INSERT INTO store(guild_id , name , price , sell , role , rrole , info ) VALUES ($1 , $2 ,$3 , $4 , $5 ,$6 ,$7)', ctx.guild.id , name, price, sell_price, role.id, r_role.id if r_role else None, info)
    #     await ctx.send("**Done** , you can also edit item vai /edititem command", embed=ecoembed)

    # @additem.error
    # async def additem_error(self, ctx, error):
    #     await ctx.send(f'`!additem <name>` , {error}')

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def edititem(self, ctx, item_id: int, attribute: typing.Literal['name', 'price', 'sell', 'role', 'req_role', 'info', 'limit'], *, value):

    #     item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1', item_id)
    #     if item is None:
    #         await ctx.send("No ITEM with this id")
        # else:
        #     if attribute == "name":
        #         await client.db.execute("UPDATE store SET name = $1 WHERE id = $2", value, item_id)
        #         await ctx.send(f"name : **{value}** updated for item id : **{item_id}** ")
        #     elif attribute == "price":
        #         await client.db.execute("UPDATE store SET price = $1 WHERE id = $2", int(value), item_id)
        #         await ctx.send(f"price : **{int(value)}** updated for item id : **{item_id}** ")
        #     elif attribute == "sell":
        #         await client.db.execute("UPDATE store SET sell = $1 WHERE id = $2", int(value), item_id)
        #         await ctx.send(f"sell : **{int(value)}** updated for item id : **{item_id}** ")
        #     elif attribute == "role":
        #         temp = ctx.guild.get_role(int(value))
        #         await client.db.execute("UPDATE store SET role = $1 WHERE id = $2", temp.id, item_id)
        #         await ctx.send(f"role : **{temp.name}** updated for item id : **{item_id}** ")
        #     elif attribute == "req_role":
        #         temp = ctx.guild.get_role(int(value))
        #         await client.db.execute("UPDATE store SET rrole = $1 WHERE id = $2", temp.id, item_id)
        #         await ctx.send(f"rrole : **{temp.name}** updated for item id : {item_id} ")
        #     elif attribute == "info":
        #         await client.db.execute("UPDATE store SET info = $1 WHERE id = $2", value, item_id)
        #         await ctx.send(f"info : **{value}** updated for item id : **{item_id}** ")
        #     elif attribute == "limit":
        #         await client.db.execute('UPDATE store SET "limit" = $1 WHERE id = $2', int(value), item_id)
        #         await ctx.send(f"limit : **{value}** updated for item id : **{item_id}** ")
        #     else:
        #         await ctx.send("Not a valid attribute\n`/edititem <item_id> <attribute> <details>`\n```name(item name) : Text\nprice(item price) : Number\nsell(item selling price) : Number\nrole(reward role) : role_id(Number)\nr role: role_id(Number)\ninfo(Dis.) : Text```")

    # @edititem.error
    # async def edititem_error(self, ctx, error):
    #     await ctx.send(f"{error} Not a valid attribute\n`/edititem <item_id> <attribute> <details>`\n```name(item name) : Text\nprice(item price) : Number\nsell(item selling price) : Number\nrole(reward role) : role_id(Number)\nr role: role_id(Number)\ninfo(Dis.) : Text```")
    #     return

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def removeitem(self, ctx, item_id: int):
    #     item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1', item_id)
    #     if item is None:
    #         await ctx.send("No ITEM with this id")
    #     else:
    #         itemname = item["name"]
    #         await client.db.execute('DELETE FROM store WHERE id = $1', item_id)
            # await ctx.send(f"***{itemname}*** Is Removed From Store")


    async def edit_item(self ,ctx , id) :

        item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1' , id)
        if not item :
            return await ctx.send( embed = bembed('No item Found'))
        
        async def item_embed() :
            i = await client.db.fetchrow('SELECT * FROM store WHERE id = $1' , id)
            embed = bembed()
            embed.title = f"{i['name']} ({id})"
            embed.add_field(name = 'Price' , value = f"{pvc_coin(ctx.guild.id)[0] if i['currency'] == 2 else coin(ctx.guild.id)} {i['price']}")
            
            reward = (" ,".join([ (ctx.guild.get_role(role_id)).mention for role_id in i['roles'] if (ctx.guild.get_role(role_id)) ]) if i['roles'] else "") + "\n" + (f"- {pvc_coin(ctx.guild.id)[0]} {i['pvc']}" if i['pvc'] != 0 else "") + "\n" + (f"- {coin(ctx.guild.id)} {i['cash']} cash" if i['cash'] != 0 else "") + "\n" + (f"- {coin(ctx.guild.id)} {i['bank']} bank" if i['bank'] != 0 else ""  ) 
            embed.add_field(name = 'Reward(s)' , value = reward)

            embed.add_field(name = 'Requirement(s)' , value = " ,".join([ (ctx.guild.get_role(role_id)).mention for role_id in i['rroles'] if (ctx.guild.get_role(role_id)) ]) if i['rroles'] else "None" )

            embed.add_field( name = 'Discription' , value = str(i['info']))
            embed.add_field( name = 'limit' , value = f"{i['limit']}") 
            return embed

        view = View()

        name = discord.ui.Button(label = 'Name' )
        async def update_name(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Item Name ?",
                                "Type Item Name")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = (modal.value)
                    await client.db.execute('UPDATE store SET name = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        name.callback = update_name
        view.add_item(name)
        
        price = discord.ui.Button(label = 'Price' )
        async def update_price(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Item Price ?",
                                "Type Item Price")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    await client.db.execute('UPDATE store SET price = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        price.callback = update_price
        view.add_item(price)
        
        currency = discord.ui.Button(label = 'Currency' )
        
        async def update_currency(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            temp_view = Confirm()
            await interaction.response.send_message("Want to Switch Currency ?" , view = temp_view , ephemeral = True)
            await temp_view.wait()
            if temp_view.value :
                i = await client.db.fetchrow('SELECT currency FROM store WHERE id = $1' , id)
                if i['currency'] == 1 :
                    await client.db.execute('UPDATE store SET currency = $1 WHERE id = $2', 2 , id)
                elif i['currency'] == 2 :
                    await client.db.execute('UPDATE store SET currency = $1 WHERE id = $2', 1 , id)
                await interaction.message.edit(embed= await item_embed())
            
        currency.callback = update_currency
        view.add_item(currency)


        limit = discord.ui.Button(label = 'Limit' )
        async def update_limit(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Item Limit ? (non-no for None)",
                                "Type Item Limit")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    await client.db.execute('UPDATE store SET "limit" = $1 WHERE id = $2', value , id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await client.db.execute('UPDATE store SET "limit" = $1 WHERE id = $2', None , id)
                    await interaction.message.edit(embed= await item_embed())
            else:
                await interaction.followup.send("No input", ephemeral=True)
        limit.callback = update_limit
        view.add_item(limit)

        info = discord.ui.Button(label = 'Discription' )
        async def update_info(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInputLong("Item Discription ?",
                                "Type Item Discription")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = (modal.value)
                    await client.db.execute('UPDATE store SET info = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        info.callback = update_info
        view.add_item(info)

        cash = discord.ui.Button(label = 'Reward Cash' )
        async def update_cash(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Reward Cash ?",
                                "Type cash amount")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    await client.db.execute('UPDATE store SET cash = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        cash.callback = update_cash
        view.add_item(cash)

        bank = discord.ui.Button(label = 'Reward Bank' )
        async def update_bank(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Reward Bnak ?",
                                "Type Bank amount")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    await client.db.execute('UPDATE store SET bank = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        bank.callback = update_bank
        view.add_item(bank) 

        pvc = discord.ui.Button(label = f'Reward {pvc_coin(ctx.guild.id)[1]}' )
        async def update_pvc(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput(f"Reward {pvc_coin(ctx.guild.id)[1]} ?",
                                f"Type {pvc_coin(ctx.guild.id)[1]} amount")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    await client.db.execute('UPDATE store SET pvc = $1 WHERE id = $2', value, id)
                    await interaction.message.edit(embed= await item_embed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        pvc.callback = update_pvc
        view.add_item(pvc)

        async def update_roles(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            data = roles.values
            if len(data) == 0:
                await client.db.execute('UPDATE store SET roles = $1 WHERE id = $2', None, id)
            else:
                await client.db.execute('UPDATE store SET roles = $1 WHERE id = $2',  [item.id for item in data], id)
            await interaction.response.edit_message(embed= await item_embed() )

        roles = discord.ui.RoleSelect( placeholder="Select Reward Roles", min_values=0, max_values=10)
        roles.callback = update_roles
        view.add_item(roles)
        
        async def update_rroles(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            data = rroles.values
            if len(data) == 0:
                await client.db.execute('UPDATE store SET rroles = $1 WHERE id = $2', None, id)
            else:
                await client.db.execute('UPDATE store SET rroles = $1 WHERE id = $2',  [item.id for item in data], id)
            await interaction.response.edit_message(embed= await item_embed() )

        rroles = discord.ui.RoleSelect( placeholder="Select Require Roles", min_values=0, max_values=10)
        rroles.callback = update_rroles
        view.add_item(rroles)

        async def delete_item(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            temp_view = Confirm()
            await interaction.response.send_message("Want to DELETE this Item ?" , view = temp_view , ephemeral = True)
            await temp_view.wait()
            if temp_view.value :
                await client.db.execute('DELETE FROM store WHERE id = $1' , id)
                await interaction.message.delete()

        delete = discord.ui.Button( emoji = "🗑️" ) 
        delete.callback = delete_item
        view.add_item(delete)
    
        await ctx.send(embed = await item_embed() , view = view)

    @commands.hybrid_command(aliases=["createitem"])
    @commands.guild_only()
    @commands.check(check_perms)
    async def additem(self, ctx, *, name: str , price : int , currency : str ):
        if currency == 'cash' :
            t = 1
        elif currency.lower() == pvc_coin(ctx.guild.id)[1].lower() :
            t = 2
        else :
            return await ctx.send( bembed('⚠️ Invalid Currency') )
        
        await client.db.execute('INSERT INTO store(guild_id , name , price , currency ) VALUES ($1 , $2 ,$3 , $4 )', ctx.guild.id , name, price, t)
        item = await client.db.fetchrow('SELECT * FROM store WHERE name = $1 AND price = $2 AND guild_id = $3 ' , name , price , ctx.guild.id)
        await self.edit_item( ctx , item['id'])


    @additem.autocomplete('currency')
    async def additem_auto( self, ctx  , current : str )-> list[app_commands.Choice[str]]:
        lis = [ 'cash' , pvc_coin(ctx.guild.id)[1].lower() ]
        return [
        app_commands.Choice(name=space, value=space)
        for space in lis if current.lower() in space.lower()
        ]

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def edititem(self, ctx, id: int):
        try :
            await self.edit_item(ctx , id)
        except Exception as e :
            await ctx.send(e)
 
    @edititem.error
    async def edititem_error(self, ctx, error):
        await ctx.send(error)
        return

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def removeitem(self, ctx, item_id: int):
        await self.edit_item(ctx , id)
 

    @commands.hybrid_command()
    @commands.check(check_perms)
    async def reseteconomy(self, ctx , cash : typing.Optional[bool] = True , bank : typing.Optional[bool] = True , pvc : typing.Optional[bool] = True):
        view = Confirm(ctx.author)
        await ctx.send(embed = bembed("Do You Really want To reset Economy ?") , view = view )
        await view.wait()
        if view.value :
            view1 = Confirm(ctx.author)
            await ctx.send(embed = bembed("Are You Sure ?") , view = view1 )
            await view1.wait()
            if view1.value :
                if cash :
                    await self.client.db.execute('UPDATE users SET cash = 0 WHERE guild_id = $1'  , ctx.guild.id) 
                if bank :
                    await self.client.db.execute('UPDATE users SET bank = 0 WHERE guild_id = $1'  , ctx.guild.id) 
                if pvc :
                    await self.client.db.execute('UPDATE users SET pvc = 0 WHERE guild_id = $1'  , ctx.guild.id) 
                
                await ctx.send( embed = bembed(f"Economy Reset\n{'✅' if cash else '❌'} Cash\n{'✅' if bank else '❌'} Bank\n{'✅' if pvc else '❌'} PVC"))

        # def check(m):
        #     return m.author == ctx.author and m.content == "YES"
        # await ctx.send("ARE YOU SURE ? , type `YES` to continue")
        # await client.wait_for('message', check=check, timeout=120)
        # await client.db.execute('DELETE FROM users WHERE guild_id = $1', ctx.guild.id)
        # await ctx.send('**DONE** , Economy = 0')

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def addpet(self , ctx , emoji: str):
    #     storedata = db[f"{ctx.guild.id}"]
    #     ecoembed = discord.Embed(color= 0xF7C906)
    #     ecoembed.set_author(name = ctx.author , url = None , icon_url= ctx.author.display_avatar.url)
    #     ecoembed.title = f'Pet Info'
    #     ecoembed.add_field(name="Pet" , value= emoji )
    #     await ctx.send("are you sure the pet is an emoji if yes **Enter the price of Pet !!!** else ignore input will expire in 45sec." , embed =ecoembed)
    #     await asyncio.sleep(1)
    #     def check1(m):
    #         try :
    #             return int(m.content ) > 0 and m.author == ctx.author
    #         except ValueError:
    #             return 0
    #     msg1 = await client.wait_for('message', check=check1 , timeout = 45)
    #     price = int(msg1.content)
    #     ecoembed.add_field(name="Price" , value= f"{coin1} {price}" )
    #     await ctx.send("Write description about item" , embed=ecoembed)
    #     def check2(m):
    #         return m.author == ctx.author
    #     msg5 = await client.wait_for('message', check=check2 , timeout = 120)
    #     info = msg5.content
    #     ecoembed.add_field(name="Description" , value= info , inline= False)
    #     await storedata.insert_one({ "category" : "pet_store" ,"pet" : emoji , "price" : price  ,  "info" : info})
    #     await ctx.send("**Done** , seen in pet shop" , embed=ecoembed)

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def removepet(self , ctx , emoji: str):
    #     storedata = db[f"{ctx.guild.id}"]
    #     ecoembed = discord.Embed(color= discord.Color.red())
    #     ecoembed.set_author(name = ctx.author , url = None , icon_url= ctx.author.display_avatar.url)
    #     pet = await storedata.find_one({"category" : "pet_store" , "pet" : emoji})
    #     if pet is None :
    #         ecoembed.description = "No such pet in pet shop!!"
    #         await ctx.send( embed=ecoembed)
    #     else :
    #         await storedata.delete_one({"category" : "pet_store" , "pet" : emoji})
    #         ecoembed.description = f"{pet['pet']} REMOVED"
    #         await ctx.send( embed=ecoembed)

    # Manage settings Here !!!!!!!!!!!!!!!!!!

    @commands.hybrid_command(aliases= ["prefix" , "config" , "start"])
    @commands.guild_only()
    @commands.check(check_perms)
    async def setup(self, ctx, prefix: typing.Optional[str], coin_emoji : typing.Optional[str]):
        if prefix and len(prefix) != 1:
            await ctx.send("The length of the prefix should be equal to 1.")
            return

        if prefix and len(prefix) == 1:
            client.data[ctx.guild.id]["prefix"] = prefix
            await client.db.execute('UPDATE guilds SET prefix = $1 WHERE id = $2', prefix, ctx.guild.id)
        if coin_emoji:
            client.data[ctx.guild.id]["coin"] = coin_emoji
            await client.db.execute('UPDATE guilds SET coin = $1 WHERE id = $2', coin_emoji, ctx.guild.id)

        def setupEmbed():
            embed = discord.Embed(title="Bot SetUp")
            embed.description = f"Prefix - ` {client.data[ctx.guild.id]['prefix'] or ','} `\nCoin - {coin(ctx.guild.id)}"
            value = ''
            if client.data[ctx.guild.id]["channels"] and len(client.data[ctx.guild.id]["channels"]) > 0:
                for channel in list(client.data[ctx.guild.id]["channels"]):
                    if ctx.guild.get_channel(channel):
                        value += f"{ctx.guild.get_channel(channel).mention}\n"
                    else:
                        client.data[ctx.guild.id]["channels"].remove(channel)
            else:
                client.data[ctx.guild.id]["channels"] = None
                value = "Active In All channels"
            embed.add_field(name='Channel(s)', value=value, inline=False)
            value = ''
            if client.data[ctx.guild.id]["manager"] and ctx.guild.get_role(client.data[ctx.guild.id]["manager"]):
                value = ctx.guild.get_role(
                    client.data[ctx.guild.id]["manager"]).mention
            else:
                client.data[ctx.guild.id]["manager"] = None
                value = "No Manager Role"
            embed.add_field(name='Manager', value=value, inline=False)
            value = ''
            if client.data[ctx.guild.id]["am_channels"] and len(client.data[ctx.guild.id]["am_channels"]) > 0:
                for channel in list(client.data[ctx.guild.id]["am_channels"]):
                    if ctx.guild.get_channel(channel):
                        value += f"{ctx.guild.get_channel(channel).mention}\n"
                    else:
                        client.data[ctx.guild.id]["am_channels"].remove(
                            channel)
            else:
                client.data[ctx.guild.id]["am_channels"] = None
                value = "Active In All channels"
            value += f"\n\nAuto Money(AM) Cash/min : **0-{client.data[ctx.guild.id]['am_cash']}**\nAuto Money(AM) pvc/min : **0-{client.data[ctx.guild.id]['am_pvc']}**"
            embed.add_field(name='Auto Money Channel(s)',
                            value=value, inline=False)
            return embed

        view = View()

        async def update_channels(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = channels.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET channels = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["channels"] = None
            else:
                await client.db.execute('UPDATE guilds SET channels = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
                client.data[ctx.guild.id]["channels"] = [
                    item.id for item in data]
            await interaction.response.edit_message(embed=setupEmbed())

        channels = discord.ui.ChannelSelect(channel_types=[
                                            discord.ChannelType.text], placeholder="Casino command channels", min_values=0, max_values=10)
        channels.callback = update_channels
        view.add_item(channels)

        async def update_manager(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = manager.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET manager = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["manager"] = None
            else:
                await client.db.execute('UPDATE guilds SET manager = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["manager"] = data[0].id
            await interaction.response.edit_message(embed=setupEmbed())

        manager = discord.ui.RoleSelect(
            placeholder="Casino Manager Role", min_values=0, max_values=1)
        manager.callback = update_manager
        view.add_item(manager)

        async def update_am_channels(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = am_channels.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET am_channels = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["am_channels"] = None
            else:
                await client.db.execute('UPDATE guilds SET am_channels = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
                client.data[ctx.guild.id]["am_channels"] = [
                    item.id for item in data]
            await interaction.response.edit_message(embed=setupEmbed())

        am_channels = discord.ui.ChannelSelect(channel_types=[
                                               discord.ChannelType.text], placeholder="Auto Money channels", min_values=0, max_values=10)
        am_channels.callback = update_am_channels
        view.add_item(am_channels)

        am_cash = Button(style=discord.ButtonStyle.grey, label="AM Cash")

        async def update_am_cash(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Auto Money Cash !",
                                "Input should be in Numbers")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    client.data[ctx.guild.id]['am_cash'] = value
                    await client.db.execute('UPDATE guilds SET am_cash = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setupEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        am_cash.callback = update_am_cash
        view.add_item(am_cash)

        am_pvc = Button(style=discord.ButtonStyle.grey, label="AM Pvc")

        async def update_am_pvc(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Auto Money Pvc !",
                                "Input should be in Numbers")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    client.data[ctx.guild.id]['am_pvc'] = value
                    await client.db.execute('UPDATE guilds SET am_pvc = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setupEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        am_pvc.callback = update_am_pvc
        view.add_item(am_pvc)

        reset = Button(style=discord.ButtonStyle.blurple,
                       label="Reset Prefix/coin")

        async def update_reset(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            await client.db.execute('UPDATE guilds SET prefix = $1 , coin = $1 WHERE id = $2', None, ctx.guild.id)
            client.data[ctx.guild.id]["prefix"] = None
            client.data[ctx.guild.id]["coin"] = None

            await interaction.response.edit_message(embed=setupEmbed())
        reset.callback = update_reset
        view.add_item(reset)
        prefix1 = Button(style=discord.ButtonStyle.grey, label="Prefix", row=4)

        async def update_prefix1(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput(
                "Enter Prefix", "The length of input should be 1")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value and len(modal.value) == 1:
                client.data[ctx.guild.id]["prefix"] = modal.value
                await client.db.execute('UPDATE guilds SET prefix = $1 WHERE id = $2', modal.value, ctx.guild.id)
                await interaction.message.edit(embed=setupEmbed())
            else:
                await interaction.followup.send("No input", ephemeral=True)
        prefix1.callback = update_prefix1
        view.add_item(prefix1)
        coinx = Button(style=discord.ButtonStyle.grey, label="Coin", row=4)

        async def update_coinx(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Paste Coin", "Paste you coin")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                client.data[ctx.guild.id]["coin"] = modal.value
                await client.db.execute('UPDATE guilds SET coin = $1 WHERE id = $2', modal.value, ctx.guild.id)
                await interaction.message.edit(embed=setupEmbed())
            else:
                await interaction.followup.send("No input", ephemeral=True)
        coinx.callback = update_coinx
        view.add_item(coinx)
        done = Button(style=discord.ButtonStyle.green, label="Done",  row=4)

        async def update_done(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            await interaction.response.edit_message(view=None)
        done.callback = update_done
        view.add_item(done)
        await ctx.send(embed=setupEmbed(), view=view)

    @commands.hybrid_command(aliases= ["pvcsetup"])
    @commands.guild_only()
    @commands.check(check_perms)
    async def setuppvc(self, ctx): 

        def setuppvcEmbed():
            embed = discord.Embed(title="Pvc SetUp")
            embed.description = f"{'`🟢`' if client.data[ctx.guild.id]['pvc'] else '`🔴`' } : PVC Status\nCoin : {pvc_coin(ctx.guild.id)[0]}\nCoin Name : {pvc_coin(ctx.guild.id)[1]}\n\nRate/hr : **{client.data[ctx.guild.id]['rate']}**\n\nMin Time : **{client.data[ctx.guild.id]['pvc_min']}** Hrs\nMax Time : **{client.data[ctx.guild.id]['pvc_max']}** Hrs\n(0 mean No limit)"

            value = ''
            if client.data[ctx.guild.id]["pvc_channel"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_channel"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["pvc_channel"]).mention
            else:
                client.data[ctx.guild.id]["pvc_channel"] = None
                value = "No seprate Channel For PVC"
            embed.add_field(name='PVC Channel', value=value, inline=False)
            
            value = ''
            if client.data[ctx.guild.id]["pvc_vc"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_vc"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["pvc_vc"]).mention
            else:
                client.data[ctx.guild.id]["pvc_vc"] = None
                value = "No vc For PVC"
            embed.add_field(name='PVC vc', value=value, inline=False)

            value = ''
            if client.data[ctx.guild.id]["pvc_category"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_category"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["pvc_category"]).mention
            else:
                client.data[ctx.guild.id]["pvc_category"] = None
                value = "No Category"

            embed.add_field(name='PVC Category',
                            value=value, inline=False)
            return embed

        view = View()

        async def update_pvc_channel(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = pvc_channel.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET pvc_channel = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_channel"] = None
            else:
                await client.db.execute('UPDATE guilds SET pvc_channel = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_channel"] = data[0].id
            await interaction.response.edit_message(embed=setuppvcEmbed())

        pvc_channel = discord.ui.ChannelSelect(channel_types=[
            discord.ChannelType.text], placeholder="PVC command channel", min_values=0, max_values=1)
        pvc_channel.callback = update_pvc_channel
        view.add_item(pvc_channel)
        
        async def update_pvc_vc(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = pvc_vc.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET pvc_vc = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_vc"] = None
            else:
                await client.db.execute('UPDATE guilds SET pvc_vc = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_vc"] = data[0].id
            await interaction.response.edit_message(embed=setuppvcEmbed())

        pvc_vc = discord.ui.ChannelSelect(channel_types=[
            discord.ChannelType.voice], placeholder="PVC voice channel", min_values=0, max_values=1)
        pvc_vc.callback = update_pvc_vc
        view.add_item(pvc_vc)

        async def update_pvc_category(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = pvc_category.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET pvc_category = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_category"] = None
            else:
                await client.db.execute('UPDATE guilds SET pvc_category = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["pvc_category"] = data[0].id
            await interaction.response.edit_message(embed=setuppvcEmbed())

        pvc_category = discord.ui.ChannelSelect(channel_types=[
            discord.ChannelType.category], placeholder="PVC's Category", min_values=0, max_values=1)
        pvc_category.callback = update_pvc_category
        view.add_item(pvc_category)

        pvc = Button(style=discord.ButtonStyle.danger if client.data[ctx.guild.id]['pvc']
                     else discord.ButtonStyle.green, label=f"{'Pvc : OFF' if client.data[ctx.guild.id]['pvc'] else 'Pvc : ON'}")

        async def update_pvc(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            if client.data[ctx.guild.id]['pvc']:
                await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2', False, ctx.guild.id)
                client.data[ctx.guild.id]['pvc'] = False
                pvc.style = discord.ButtonStyle.green
                pvc.label = 'Pvc : ON'
            else:
                await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2', True, ctx.guild.id)
                client.data[ctx.guild.id]['pvc'] = True
                pvc.style = discord.ButtonStyle.danger
                pvc.label = 'Pvc : OFF'

            await interaction.response.edit_message(embed=setuppvcEmbed(), view=view)

        pvc.callback = update_pvc
        view.add_item(pvc)

        rate = Button(style=discord.ButtonStyle.grey, label="rate")
        async def update_rate(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Rate/hr Fro Pvc",
                                "Input should be in Numbers")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    client.data[ctx.guild.id]['rate'] = value
                    await client.db.execute('UPDATE guilds SET rate = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setuppvcEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        rate.callback = update_rate
        view.add_item(rate)
        
        pvc_coin_btn = Button(style=discord.ButtonStyle.grey, label="coin")

        async def update_pvc_coin(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("PVC Coin",
                                "Paste a emoji")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = modal.value
                    client.data[ctx.guild.id]['pvc_coin'] = value
                    await client.db.execute('UPDATE guilds SET pvc_coin = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setuppvcEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        pvc_coin_btn.callback = update_pvc_coin
        view.add_item(pvc_coin_btn)
        
        pvc_name = Button(style=discord.ButtonStyle.grey, label="Coin Name")

        async def update_pvc_name(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("PVC Coin Name",
                                "Enter The Coin Name")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = modal.value
                    client.data[ctx.guild.id]['pvc_name'] = value
                    await client.db.execute('UPDATE guilds SET pvc_name = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setuppvcEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        pvc_name.callback = update_pvc_name
        view.add_item(pvc_name)

        min_time = Button(style=discord.ButtonStyle.grey, label="Min Time")

        async def update_min_time(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Min Amount Of Time For PVC ? (in Hrs)",
                                "Input should be in Numbers")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    client.data[ctx.guild.id]['pvc_min'] = value
                    await client.db.execute('UPDATE guilds SET pvc_min = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setuppvcEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        min_time.callback = update_min_time
        view.add_item(min_time)
        
        max_time = Button(style=discord.ButtonStyle.grey, label="Max Time")

        async def update_max_time(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            modal = SingleInput("Max Amount Of Time For PVC ? (in Hrs)",
                                "Input should be in Numbers")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = int(modal.value)
                    client.data[ctx.guild.id]['pvc_max'] = value
                    await client.db.execute('UPDATE guilds SET pvc_max = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setuppvcEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        max_time.callback = update_max_time
        view.add_item(max_time)

        done = Button(style=discord.ButtonStyle.blurple, label="Done")

        async def update_done(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            await interaction.response.edit_message(view=None)
        done.callback = update_done
        view.add_item(done)
        await ctx.send(embed=setuppvcEmbed(), view=view)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def roleincome(self, ctx, role : typing.Optional[discord.Role] , bank : typing.Optional[int] , cash : typing.Optional[int] , pvc : typing.Optional[int] , cooldown : typing.Optional[TimeConverter] ):
        ecoembed = discord.Embed(color=discord.Color.blue())
        ecoembed.set_author(
            name=ctx.guild.name, icon_url=ctx.guild.icon.url)
    
        if role :
            data = await client.db.fetchrow("SELECT * FROM income WHERE guild_id = $1 AND role_id = $2" , ctx.guild.id , role.id)
            if data is None and ( cash or pvc or bank ) :
                await client.db.execute('INSERT INTO income(role_id , guild_id , bank , cash , pvc , cooldown ) VALUES ($1 , $2 ,$3,$4 , $5 , $6)', role.id, ctx.guild.id, bank or 0 , cash or 0 , pvc or 0 , cooldown[0] if cooldown else 43200 )
            elif data :
                if bank :
                    await client.db.execute('UPDATE income SET bank = $1 WHERE role_id =$2 AND guild_id = $3', bank , role.id, ctx.guild.id)
                if cash :
                    await client.db.execute('UPDATE income SET cash = $1 WHERE role_id =$2 AND guild_id = $3', cash , role.id, ctx.guild.id)
                if pvc :
                    await client.db.execute('UPDATE income SET pvc = $1 WHERE role_id =$2 AND guild_id = $3', pvc , role.id, ctx.guild.id)
                if cooldown :
                    await client.db.execute('UPDATE income SET cooldown = $1 WHERE role_id =$2 AND guild_id = $3', cooldown[0] , role.id, ctx.guild.id)
                if pvc is None and cash is None and bank is None :
                    view = Confirm(ctx.author)
                    await ctx.send(f"Do You Want To Delete Role Income For {role.name}" , view= view)
                    await view.wait()
                    if view.value :
                        await client.db.execute('DELETE FROM income WHERE role_id =$1 AND guild_id = $2',  role.id, ctx.guild.id)
                    else :
                        pass
                    
        docs = await client.db.fetch('SELECT role_id , cash , pvc , bank, cooldown FROM income WHERE guild_id = $1 ORDER BY cash DESC' , ctx.guild.id)
        ecoembed.description = ''
        for x in docs:
            if ctx.guild.get_role(x['role_id']) :
                # value = (f"{ctx.guild.get_role(x['role_id']).mention}\n") + (f'Cash : {x["bank"]}\n' if x["bank"] != 0 else '') + (f'Cash : {x["cash"]}\n' if x["cash"] != 0 else '') + (f'Pvc : {x["pvc"]}' if x["pvc"] != 0 else '') + (f'Cooldown : **{int(x["cooldown"]/(60*60))} hr**')
                # ecoembed.add_field(name=ctx.guild.get_role(x['role_id']).name , value= value )
                ecoembed.description += f"{ctx.guild.get_role(x['role_id']).mention}" + (f'| {int(x["cooldown"]/(60*60))} hr\n')  + (f'bank : {x["bank"]} |' if x["bank"] != 0 else '') + (f'cash : {x["cash"]} |' if x["cash"] != 0 else '') + (f'pvc : {x["pvc"]} |' if x["pvc"] != 0 else '') + "\n"
        # if len(ecoembed.fields) == 0 :
        #     ecoembed.description = "No Income Role"
        if ecoembed.description == '' :
            ecoembed.description = "No Income Role"
        await ctx.send(embed=ecoembed)

    @roleincome.error
    async def roleincome_error(self, ctx, error):
        await ctx.send(f'{error}')
        print(error)
        return
    
    

#     @commands.command()
#     @commands.has_permissions( administrator =True)
#     @commands.guild_only()
#     async def dreampg(self , ctx , * , pollinfo :str):
#         options = pollinfo.splitlines()
#         description = " "
#         for i in range(len(options)):
#             if i == 0 :
#                 pass
#             else:
#                 description = description + f"{self.emoji[i-1]} : {options[i]}\n"

#         embed = discord.Embed(
#                 title=f"{options[0]}",
#                 color= 0x0847F7,
#                 description= description
#             )
#         embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/966022737367814156/966412820898000936/PAOD_logo-03.jpg")
#         embed.set_author(
#                     name=f"PLAYGROUND VOTING", icon_url="https://cdn.discordapp.com/attachments/966022737367814156/966412820898000936/PAOD_logo-03.jpg")
#         view = NormalView(timeout=432000 , count = (len(options)-1))
#         await ctx.send(embed = embed , view = view)

#     @commands.hybrid_command()
#     @commands.has_permissions( administrator =True)
#     @commands.guild_only()
#     async def dreampgresult(self , ctx , pollid :str , option : str , multiplay : int):
#         try :
#             pollid = int(pollid)
#         except ValueError:
#             await ctx.send("invalid pollid")
#             return
#         coll = db[f"{ctx.guild.id}"]
#         polldata = db['dream11']
#         vote_data = polldata.find({ "pollid"  : pollid ,"vote": option})
#         voters = await vote_data.to_list(length = 1000)
#         dis = "winner list \n\n"
#         for voter in voters :
#             await coll.update_one({"id" : voter['id'] } , {"$inc": {"bank" : +(multiplay * voter['amount']) }})
#             user = ctx.guild.get_member(voter['id'])
#             dis = dis + f"{user} : +{( multiplay * voter['amount'])}\n"
#         embed = discord.Embed(description= dis)
#         await ctx.send(  embed = embed)


# class NormalView(discord.ui.View):
#     def __init__(self , timeout , count):
#         super().__init__(timeout= timeout)
#         self.count = count
#         self.emoji = ["\U0001f1e6", "\U0001f1e7" ,"\U0001f1e8" ,"\U0001f1e9", "\U0001f1ea" ,"\U0001f1eb", "\U0001f1ec", "\U0001f1ed", "\U0001f1ee" ,"\U0001f1ef", "\U0001f1f0", "\U0001f1f1" ,"\U0001f1f2" ,"\U0001f1f3" ,"\U0001f1f4" ,"\U0001f1f5" ,"\U0001f1f6" ,"\U0001f1f7", "\U0001f1f8", "\U0001f1f9" ]
#         self.alpha = ["A","B", "C" , "D" , "E","F", "G","H" , "I" , "J" , "K" , "L" , "M" , "N" , "O" , "P" , "Q" , "R" , "S" , "T" ]

#         if (self.count )%5 == 0 :
#             z = 5
#         elif (self.count)%4 == 0:
#             z = 4
#         elif  (self.count) == 9 or (self.count) == 6 :
#             z = 3
#         else :
#             z = 5

#         for x in range(self.count):
#             y = int(x/z)
#             self.add_item(PollButton(x, y , self.emoji[x] , self.alpha[x]))

# class PollButton(discord.ui.Button['NormalView']):
#     def __init__(self, x: int, y: int , emoji : str , custom_id : str):
#         super().__init__(style=discord.ButtonStyle.blurple , emoji= emoji,custom_id= custom_id,  row=y)
#         self.x = x
#         self.y = y


#     async def callback(self, interaction: discord.Interaction):
#         assert self.view is not None
#         view: NormalView = self.view
#         x = self.custom_id
#         y = self.emoji
#         polldata = db['dream11']
#         data = await polldata.find_one({"id": interaction.user.id , "pollid" : interaction.message.id})
#         role = interaction.guild.get_role(1056287025889804369)
#         # if data is None and role in interaction.user.roles :
#         await interaction.response.send_modal(Feedback(vote = x))
#         # else :
#             # await interaction.response.send_message(f"you already select a player or you are in in discord playground ,join next time :) " , ephemeral = True)

# class Feedback(discord.ui.Modal, title='Rumbles'):

#     def __init__(self , vote):
#         self.vote = vote
#         super().__init__()

#     data = discord.ui.TextInput(
#         label="type amount",
#         style=discord.TextStyle.short,
#         placeholder='...',
#     )

#     async def on_submit(self, interaction: discord.Interaction):
#         try:
#             amount = int(self.data.value)
#         except ValueError:
#             await interaction.response.send_message("invalid input , try again" , ephemeral= True)
#             return
#         coll = db[f"{interaction.guild.id}"]
#         polldata = db['dream11']
#         bal = await coll.find_one({"id": interaction.user.id})
#         if 0 < amount <= bal['bank'] :
#             await coll.update_one({"id" : interaction.user.id } , {"$inc": {"bank" : -amount}})
#             await polldata.insert_one({ "pollid" : interaction.message.id,"id":interaction.user.id , "vote": self.vote , 'amount' : amount})
#             await interaction.response.send_message(f"your bet registered on {self.vote} of amount {amount}" , ephemeral= True)
#         else :
#             await interaction.response.send_message(f"error with the amount , check your balance , current bal is {bal['bank']}" , ephemeral= True)

#     async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
#         await interaction.response.send_message(f'Oops! Something went wrong.{error}', ephemeral=True)

async def setup(client):
    await client.add_cog(EcoManager(client))
