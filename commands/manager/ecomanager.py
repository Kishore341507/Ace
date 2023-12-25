import discord
from discord.ext import commands
from database import *
from comp.converters import TimeConverter
import typing
from discord.ui import Button, View
from discord import app_commands


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

    # Manage settings Here !!!!!!!!!!!!!!!!!!

    # @commands.hybrid_command(aliases= ["prefix" , "config" , "start"])
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def setup(self, ctx, prefix: typing.Optional[str], coin_emoji : typing.Optional[str]):
    #     if prefix and len(prefix) != 1:
    #         await ctx.send("The length of the prefix should be equal to 1.")
    #         return

    #     if prefix and len(prefix) == 1:
    #         client.data[ctx.guild.id]["prefix"] = prefix
    #         await client.db.execute('UPDATE guilds SET prefix = $1 WHERE id = $2', prefix, ctx.guild.id)
    #     if coin_emoji:
    #         client.data[ctx.guild.id]["coin"] = coin_emoji
    #         await client.db.execute('UPDATE guilds SET coin = $1 WHERE id = $2', coin_emoji, ctx.guild.id)

    #     def setupEmbed():
    #         embed = discord.Embed(title="Bot SetUp")
    #         embed.description = f"Prefix - ` {client.data[ctx.guild.id]['prefix'] or ','} `\nCoin - {coin(ctx.guild.id)}"
    #         value = ''
    #         if client.data[ctx.guild.id]["channels"] and len(client.data[ctx.guild.id]["channels"]) > 0:
    #             for channel in list(client.data[ctx.guild.id]["channels"]):
    #                 if ctx.guild.get_channel(channel):
    #                     value += f"{ctx.guild.get_channel(channel).mention}\n"
    #                 else:
    #                     client.data[ctx.guild.id]["channels"].remove(channel)
    #         else:
    #             client.data[ctx.guild.id]["channels"] = None
    #             value = "Active In All channels"
    #         embed.add_field(name='Channel(s)', value=value, inline=False)
    #         value = ''
    #         if client.data[ctx.guild.id]["manager"] and ctx.guild.get_role(client.data[ctx.guild.id]["manager"]):
    #             value = ctx.guild.get_role(
    #                 client.data[ctx.guild.id]["manager"]).mention
    #         else:
    #             client.data[ctx.guild.id]["manager"] = None
    #             value = "No Manager Role"
    #         embed.add_field(name='Manager', value=value, inline=False)
    #         value = ''
    #         if client.data[ctx.guild.id]["am_channels"] and len(client.data[ctx.guild.id]["am_channels"]) > 0:
    #             for channel in list(client.data[ctx.guild.id]["am_channels"]):
    #                 if ctx.guild.get_channel(channel):
    #                     value += f"{ctx.guild.get_channel(channel).mention}\n"
    #                 else:
    #                     client.data[ctx.guild.id]["am_channels"].remove(
    #                         channel)
    #         else:
    #             client.data[ctx.guild.id]["am_channels"] = None
    #             value = "Active In All channels"
    #         value += f"\n\nAuto Money(AM) Cash/min : **0-{client.data[ctx.guild.id]['am_cash']}**\nAuto Money(AM) pvc/min : **0-{client.data[ctx.guild.id]['am_pvc']}**"
    #         embed.add_field(name='Auto Money Channel(s)',
    #                         value=value, inline=False)
    #         return embed

    #     view = View()

    #     async def update_channels(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = channels.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET channels = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["channels"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET channels = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
    #             client.data[ctx.guild.id]["channels"] = [
    #                 item.id for item in data]
    #         await interaction.response.edit_message(embed=setupEmbed())

    #     channels = discord.ui.ChannelSelect(channel_types=[
    #                                         discord.ChannelType.text], placeholder="Casino command channels", min_values=0, max_values=10)
    #     channels.callback = update_channels
    #     view.add_item(channels)

    #     async def update_manager(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = manager.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET manager = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["manager"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET manager = $1 WHERE id = $2', data[0].id, ctx.guild.id)
    #             client.data[ctx.guild.id]["manager"] = data[0].id
    #         await interaction.response.edit_message(embed=setupEmbed())

    #     manager = discord.ui.RoleSelect(
    #         placeholder="Casino Manager Role", min_values=0, max_values=1)
    #     manager.callback = update_manager
    #     view.add_item(manager)

    #     async def update_am_channels(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = am_channels.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET am_channels = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["am_channels"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET am_channels = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
    #             client.data[ctx.guild.id]["am_channels"] = [
    #                 item.id for item in data]
    #         await interaction.response.edit_message(embed=setupEmbed())

    #     am_channels = discord.ui.ChannelSelect(channel_types=[
    #                                            discord.ChannelType.text], placeholder="Auto Money channels", min_values=0, max_values=10)
    #     am_channels.callback = update_am_channels
    #     view.add_item(am_channels)

    #     am_cash = Button(style=discord.ButtonStyle.grey, label="AM Cash")

    #     async def update_am_cash(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Auto Money Cash !",
    #                             "Input should be in Numbers")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = int(modal.value)
    #                 client.data[ctx.guild.id]['am_cash'] = value
    #                 await client.db.execute('UPDATE guilds SET am_cash = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setupEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     am_cash.callback = update_am_cash
    #     view.add_item(am_cash)

    #     am_pvc = Button(style=discord.ButtonStyle.grey, label="AM Pvc")

    #     async def update_am_pvc(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Auto Money Pvc !",
    #                             "Input should be in Numbers")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = int(modal.value)
    #                 client.data[ctx.guild.id]['am_pvc'] = value
    #                 await client.db.execute('UPDATE guilds SET am_pvc = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setupEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     am_pvc.callback = update_am_pvc
    #     view.add_item(am_pvc)

    #     reset = Button(style=discord.ButtonStyle.blurple,
    #                    label="Reset Prefix/coin")

    #     async def update_reset(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         await client.db.execute('UPDATE guilds SET prefix = $1 , coin = $1 WHERE id = $2', None, ctx.guild.id)
    #         client.data[ctx.guild.id]["prefix"] = None
    #         client.data[ctx.guild.id]["coin"] = None

    #         await interaction.response.edit_message(embed=setupEmbed())
    #     reset.callback = update_reset
    #     view.add_item(reset)
    #     prefix1 = Button(style=discord.ButtonStyle.grey, label="Prefix", row=4)

    #     async def update_prefix1(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput(
    #             "Enter Prefix", "The length of input should be 1")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value and len(modal.value) == 1:
    #             client.data[ctx.guild.id]["prefix"] = modal.value
    #             await client.db.execute('UPDATE guilds SET prefix = $1 WHERE id = $2', modal.value, ctx.guild.id)
    #             await interaction.message.edit(embed=setupEmbed())
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     prefix1.callback = update_prefix1
    #     view.add_item(prefix1)
    #     coinx = Button(style=discord.ButtonStyle.grey, label="Coin", row=4)

    #     async def update_coinx(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Paste Coin", "Paste you coin")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             client.data[ctx.guild.id]["coin"] = modal.value
    #             await client.db.execute('UPDATE guilds SET coin = $1 WHERE id = $2', modal.value, ctx.guild.id)
    #             await interaction.message.edit(embed=setupEmbed())
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     coinx.callback = update_coinx
    #     view.add_item(coinx)
    #     done = Button(style=discord.ButtonStyle.green, label="Done",  row=4)

    #     async def update_done(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         await interaction.response.edit_message(view=None)
    #     done.callback = update_done
    #     view.add_item(done)
    #     await ctx.send(embed=setupEmbed(), view=view)

    # @commands.hybrid_command(aliases= ["pvcsetup"])
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def setuppvc(self, ctx): 

    #     def setuppvcEmbed():
    #         embed = discord.Embed(title="Pvc SetUp")
    #         embed.description = f"{'`🟢`' if client.data[ctx.guild.id]['pvc'] else '`🔴`' } : PVC Status\nCoin : {pvc_coin(ctx.guild.id)[0]}\nCoin Name : {pvc_coin(ctx.guild.id)[1]}\n\nRate/hr : **{client.data[ctx.guild.id]['rate']}**\n\nMin Time : **{client.data[ctx.guild.id]['pvc_min']}** Hrs\nMax Time : **{client.data[ctx.guild.id]['pvc_max']}** Hrs\n(0 mean No limit)"

    #         value = ''
    #         if client.data[ctx.guild.id]["pvc_channel"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_channel"]):
    #             value = ctx.guild.get_channel(
    #                 client.data[ctx.guild.id]["pvc_channel"]).mention
    #         else:
    #             client.data[ctx.guild.id]["pvc_channel"] = None
    #             value = "No seprate Channel For PVC"
    #         embed.add_field(name='PVC Channel', value=value, inline=False)
            
    #         value = ''
    #         if client.data[ctx.guild.id]["pvc_vc"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_vc"]):
    #             value = ctx.guild.get_channel(
    #                 client.data[ctx.guild.id]["pvc_vc"]).mention
    #         else:
    #             client.data[ctx.guild.id]["pvc_vc"] = None
    #             value = "No vc For PVC"
    #         embed.add_field(name='PVC vc', value=value, inline=False)

    #         value = ''
    #         if client.data[ctx.guild.id]["pvc_category"] and ctx.guild.get_channel(client.data[ctx.guild.id]["pvc_category"]):
    #             value = ctx.guild.get_channel(
    #                 client.data[ctx.guild.id]["pvc_category"]).mention
    #         else:
    #             client.data[ctx.guild.id]["pvc_category"] = None
    #             value = "No Category"

    #         embed.add_field(name='PVC Category',
    #                         value=value, inline=False)
    #         return embed

    #     view = View()

    #     async def update_pvc_channel(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = pvc_channel.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET pvc_channel = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_channel"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET pvc_channel = $1 WHERE id = $2', data[0].id, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_channel"] = data[0].id
    #         await interaction.response.edit_message(embed=setuppvcEmbed())

    #     pvc_channel = discord.ui.ChannelSelect(channel_types=[
    #         discord.ChannelType.text], placeholder="PVC command channel", min_values=0, max_values=1)
    #     pvc_channel.callback = update_pvc_channel
    #     view.add_item(pvc_channel)
        
    #     async def update_pvc_vc(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = pvc_vc.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET pvc_vc = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_vc"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET pvc_vc = $1 WHERE id = $2', data[0].id, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_vc"] = data[0].id
    #         await interaction.response.edit_message(embed=setuppvcEmbed())

    #     pvc_vc = discord.ui.ChannelSelect(channel_types=[
    #         discord.ChannelType.voice], placeholder="PVC voice channel", min_values=0, max_values=1)
    #     pvc_vc.callback = update_pvc_vc
    #     view.add_item(pvc_vc)

    #     async def update_pvc_category(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         data = pvc_category.values
    #         if len(data) == 0:
    #             await client.db.execute('UPDATE guilds SET pvc_category = $1 WHERE id = $2', None, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_category"] = None
    #         else:
    #             await client.db.execute('UPDATE guilds SET pvc_category = $1 WHERE id = $2', data[0].id, ctx.guild.id)
    #             client.data[ctx.guild.id]["pvc_category"] = data[0].id
    #         await interaction.response.edit_message(embed=setuppvcEmbed())

    #     pvc_category = discord.ui.ChannelSelect(channel_types=[
    #         discord.ChannelType.category], placeholder="PVC's Category", min_values=0, max_values=1)
    #     pvc_category.callback = update_pvc_category
    #     view.add_item(pvc_category)

    #     pvc = Button(style=discord.ButtonStyle.danger if client.data[ctx.guild.id]['pvc']
    #                  else discord.ButtonStyle.green, label=f"{'Pvc : OFF' if client.data[ctx.guild.id]['pvc'] else 'Pvc : ON'}")

    #     async def update_pvc(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         if client.data[ctx.guild.id]['pvc']:
    #             await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2', False, ctx.guild.id)
    #             client.data[ctx.guild.id]['pvc'] = False
    #             pvc.style = discord.ButtonStyle.green
    #             pvc.label = 'Pvc : ON'
    #         else:
    #             await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2', True, ctx.guild.id)
    #             client.data[ctx.guild.id]['pvc'] = True
    #             pvc.style = discord.ButtonStyle.danger
    #             pvc.label = 'Pvc : OFF'

    #         await interaction.response.edit_message(embed=setuppvcEmbed(), view=view)

    #     pvc.callback = update_pvc
    #     view.add_item(pvc)

    #     rate = Button(style=discord.ButtonStyle.grey, label="rate")
    #     async def update_rate(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Rate/hr Fro Pvc",
    #                             "Input should be in Numbers")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = int(modal.value)
    #                 client.data[ctx.guild.id]['rate'] = value
    #                 await client.db.execute('UPDATE guilds SET rate = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setuppvcEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     rate.callback = update_rate
    #     view.add_item(rate)
        
    #     pvc_coin_btn = Button(style=discord.ButtonStyle.grey, label="coin")

    #     async def update_pvc_coin(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("PVC Coin",
    #                             "Paste a emoji")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = modal.value
    #                 client.data[ctx.guild.id]['pvc_coin'] = value
    #                 await client.db.execute('UPDATE guilds SET pvc_coin = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setuppvcEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     pvc_coin_btn.callback = update_pvc_coin
    #     view.add_item(pvc_coin_btn)
        
    #     pvc_name = Button(style=discord.ButtonStyle.grey, label="Coin Name")

    #     async def update_pvc_name(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("PVC Coin Name",
    #                             "Enter The Coin Name")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = modal.value
    #                 client.data[ctx.guild.id]['pvc_name'] = value
    #                 await client.db.execute('UPDATE guilds SET pvc_name = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setuppvcEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     pvc_name.callback = update_pvc_name
    #     view.add_item(pvc_name)

    #     min_time = Button(style=discord.ButtonStyle.grey, label="Min Time")

    #     async def update_min_time(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Min Amount Of Time For PVC ? (in Hrs)",
    #                             "Input should be in Numbers")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = int(modal.value)
    #                 client.data[ctx.guild.id]['pvc_min'] = value
    #                 await client.db.execute('UPDATE guilds SET pvc_min = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setuppvcEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     min_time.callback = update_min_time
    #     view.add_item(min_time)
        
    #     max_time = Button(style=discord.ButtonStyle.grey, label="Max Time")

    #     async def update_max_time(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         modal = SingleInput("Max Amount Of Time For PVC ? (in Hrs)",
    #                             "Input should be in Numbers")
    #         await interaction.response.send_modal(modal)
    #         await modal.wait()
    #         if modal.value:
    #             try:
    #                 value = int(modal.value)
    #                 client.data[ctx.guild.id]['pvc_max'] = value
    #                 await client.db.execute('UPDATE guilds SET pvc_max = $1 WHERE id = $2', value, ctx.guild.id)
    #                 await interaction.message.edit(embed=setuppvcEmbed())
    #             except Exception as e:
    #                 await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
    #         else:
    #             await interaction.followup.send("No input", ephemeral=True)
    #     max_time.callback = update_max_time
    #     view.add_item(max_time)

    #     done = Button(style=discord.ButtonStyle.blurple, label="Done")

    #     async def update_done(interaction):
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("Not Your Interaction")
    #             return
    #         await interaction.response.edit_message(view=None)
    #     done.callback = update_done
    #     view.add_item(done)
    #     await ctx.send(embed=setuppvcEmbed(), view=view)

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
                ecoembed.description += f"{ctx.guild.get_role(x['role_id']).mention}" + (f'| {int(x["cooldown"]/(60*60))} hr\n')  + (f'bank : {x["bank"]} |' if x["bank"] != 0 else '') + (f'cash : {x["cash"]} |' if x["cash"] != 0 else '') + (f'pvc : {x["pvc"]} |' if x["pvc"] != 0 else '') + "\n"
        if ecoembed.description == '' :
            ecoembed.description = "No Income Role"
        await ctx.send(embed=ecoembed)

    @roleincome.error
    async def roleincome_error(self, ctx, error):
        await ctx.send(f'{error}')
        print(error)
        return
    
async def setup(client):
    await client.add_cog(EcoManager(client))
