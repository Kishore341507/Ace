import discord
from discord.ext import commands
from database import *
import random
from discord.ext.commands import BucketType, cooldown
import traceback


class BjButton(discord.ui.Button['bjview']):
    def __init__(self, x, label: str):
        super().__init__(style=x, label=label)
        if self.label == "Double Down":
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: bjview = self.view
        click = self.label

        if interaction.user != view.ctx.author:
            return

        elif click == "Hit":
            pDrawnCard = await view.take_card()
            view.pCARD.append(pDrawnCard)
            pDrawnCard = pDrawnCard.split()
            if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
                pDrawnCard[1] = "10"
            elif pDrawnCard[1] == "A":
                pDrawnCard[1] = "11"
            view.pCardNum.append(int(pDrawnCard[1]))
            pCardNum = await view.eval_ace(view.pCardNum)
            pTotal = " "
            for x in view.pCARD:
                x = x.split()
                pTotal += f"{x[0]}"
            view.embed.set_field_at(
                0, name=f"Your Hand", value=f"{pTotal}\n\nScore: {sum(pCardNum)}", inline=True)
            if (await view.is_bust(pCardNum) or await view.is_blackjack(pCardNum)):
                pass
            else:
                await interaction.response.edit_message(embed=view.embed)
                return

        elif click == "Stand":
            pass

        winner = await view.compare_between()

        for child in view.children:
            child.disabled = True

        view.stop()
        view.ctx.command.reset_cooldown(view.ctx)
        if winner == 1:
            view.embed.color = 0x47d220
            await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", 2 * view.amount, view.ctx.author.id, interaction.guild.id)
            # await view.economy.update_one({"id": view.ctx.author.id} , {"$inc" : {"cash": + ( 2 * view.amount)}})
            await interaction.response.edit_message(embed=view.embed, view=view)

        elif winner == -1:
            view.embed.color = 0xff0000
            await interaction.response.edit_message(embed=view.embed, view=view)

        else:
            await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", view.amount, view.ctx.author.id, interaction.guild.id)
            # await view.economy.update_one({"id": view.ctx.author.id} , {"$inc" : {"cash": + view.amount}})
            await interaction.response.edit_message(embed=view.embed, view=view)


class bjview(discord.ui.View):
    def __init__(self, timeout, ctx, cards, dCARD, dCardNum, pCARD, pCardNum, embed, amount):
        super().__init__(timeout=timeout)

        self.ctx = ctx

        self.cards = ['<:10C:1147776234466590810> 10', '<:10D:1147776375269380106> 10', '<:10H:1147776402050011236> 10', '<:10S:1147776426846736504> 10', '<:2C:1147776461877563412> 2', '<:2D:1147776571520864286> 2', '<:2H:1147776602919411763> 2', '<:2S:1147776656661037056> 2', '<:3C:1147776740748439662> 3', '<:3D:1147776779059212318> 3', '<:3H:1147776801624572006> 3', '<:3S:1147776840342179922> 3', '<:4C:1147776866942459964> 4', '<:4D:1147776891621757011> 4', '<:4H:1147776931887071364> 4', '<:4S:1147776969778397305> 4', '<:5C:1147777008017870889> 5', '<:5D:1147777032625852506> 5', '<:5H:1147777070542372874> 5', '<:5S:1147777094491848726> 5', '<:6C:1147777136678158406> 6', '<:6D:1147777171037896815> 6', '<:6H:1147777204651040768> 6', '<:6S:1147777234841645126> 6', '<:7C:1147777270677770321> 7', '<:7D:1147777310066479105> 7', '<:7H:1147777337673400390> 7', '<:7S:1147777379368976474> 7', '<:8C:1147777413254742077> 8', '<:8H:1147777546138693632> 8', '<:8D:1147777589793005669> 8', '<:8S:1147777642611875921> 8', '<:9C:1147777674790588508> 9', '<:9D:1147777706268831794> 9', '<:9H:1147777744302780416> 9', '<:9S:1147777779216158730> 9', '<:AC:1147777810979631125> A', '<:AD:1147777839282794576> A', '<:AH:1147777870173851688> A', '<:AS:1147777908027445330> A' , '<:JC:1147783707319615518> Jack', '<:JD:1147783757470904370> Jack', '<:JH:1147783825917743135> Jack', '<:JS:1147783870499000420> Jack', '<:KC:1147783909338259466> King', '<:KD:1147783938379616346> King', '<:KH:1147783968909963354> King', '<:KS:1147784005584961606> King', '<:QC:1147784027072372746> Queen', '<:QD:1147784060677136395> Queen', '<:QH:1147784089399722026> Queen', '<:QS:1147784116499120138> Queen']

        self.dCARD = dCARD
        self.dCardNum = dCardNum
        self.pCARD = pCARD
        self.pCardNum = pCardNum
        self.embed = embed
        self.amount = amount
        # self.economy = db[f"{self.ctx.guild.id}"]

        self.add_item(BjButton(discord.ButtonStyle.blurple, "Hit"))
        self.add_item(BjButton(discord.ButtonStyle.green,  "Stand"))
        self.add_item(BjButton(discord.ButtonStyle.gray, "Double Down"))

    async def take_card(self):

        drawnCard = self.cards.pop(random.randint(0, len(self.cards) - 1))

        if len(self.cards) == 0:
            self.cards = ['<:10C:1147776234466590810> 10', '<:10D:1147776375269380106> 10', '<:10H:1147776402050011236> 10', '<:10S:1147776426846736504> 10', '<:2C:1147776461877563412> 2', '<:2D:1147776571520864286> 2', '<:2H:1147776602919411763> 2', '<:2S:1147776656661037056> 2', '<:3C:1147776740748439662> 3', '<:3D:1147776779059212318> 3', '<:3H:1147776801624572006> 3', '<:3S:1147776840342179922> 3', '<:4C:1147776866942459964> 4', '<:4D:1147776891621757011> 4', '<:4H:1147776931887071364> 4', '<:4S:1147776969778397305> 4', '<:5C:1147777008017870889> 5', '<:5D:1147777032625852506> 5', '<:5H:1147777070542372874> 5', '<:5S:1147777094491848726> 5', '<:6C:1147777136678158406> 6', '<:6D:1147777171037896815> 6', '<:6H:1147777204651040768> 6', '<:6S:1147777234841645126> 6', '<:7C:1147777270677770321> 7', '<:7D:1147777310066479105> 7', '<:7H:1147777337673400390> 7', '<:7S:1147777379368976474> 7', '<:8C:1147777413254742077> 8', '<:8H:1147777546138693632> 8', '<:8D:1147777589793005669> 8', '<:8S:1147777642611875921> 8', '<:9C:1147777674790588508> 9', '<:9D:1147777706268831794> 9', '<:9H:1147777744302780416> 9', '<:9S:1147777779216158730> 9', '<:AC:1147777810979631125> A', '<:AD:1147777839282794576> A', '<:AH:1147777870173851688> A', '<:AS:1147777908027445330> A' , '<:JC:1147783707319615518> Jack', '<:JD:1147783757470904370> Jack', '<:JH:1147783825917743135> Jack', '<:JS:1147783870499000420> Jack', '<:KC:1147783909338259466> King', '<:KD:1147783938379616346> King', '<:KH:1147783968909963354> King', '<:KS:1147784005584961606> King', '<:QC:1147784027072372746> Queen', '<:QD:1147784060677136395> Queen', '<:QH:1147784089399722026> Queen', '<:QS:1147784116499120138> Queen']
        return drawnCard

    async def eval_ace(self, cardNum):
        total = sum(cardNum)
        for ace in cardNum:
            if ace == 11 and total > 21:
                position_ace = cardNum.index(11)
                cardNum[position_ace] = 1
        return cardNum

    async def is_bust(self, cardNum):
        total = sum(cardNum)
        if total > 21:
            return True
        return None

    async def is_blackjack(self, cardNum):
        total = sum(cardNum)
        if total == 21:
            return True
        return None

    async def compare_between(self):
        total_player = sum(self.pCardNum)
        total_dealer = sum(self.dCardNum)
        player_bust = await self.is_bust(self.pCardNum)
        dealer_bust = await self.is_bust(self.dCardNum)
        player_blackjack = await self.is_blackjack(self.pCardNum)
        dearler_blackjack = await self.is_blackjack(self.dCardNum)

        dTotal = ' '
        for x in self.dCARD:
            x = x.split()
            dTotal += f"{x[0]}"

        if player_bust:
            self.embed.description = f"Result: Dealer wins , Player BUST (- {coin(self.ctx.guild.id)} {self.amount})"
            return -1
        elif dealer_bust:
            self.embed.description = f"Result: Player wins , Dealer BUST (+ {coin(self.ctx.guild.id)} {self.amount})"
            self.embed.set_field_at(
                1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
            return 1
        elif player_blackjack and dearler_blackjack:
            self.embed.description = f"Result = Tie"
            self.embed.set_field_at(
                1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
            return 0
        elif player_blackjack:
            self.embed.description = f"Result: Player wins , its Blackjack (+ {coin(self.ctx.guild.id)} {self.amount})"
            return 1
        elif dearler_blackjack:
            self.embed.description = f"Result: Dearler wins , its Blackjack (- {coin(self.ctx.guild.id)} {self.amount})"
            self.embed.set_field_at(
                1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
            return -1
        elif total_player < 21 and total_dealer < 21:
            if total_player > total_dealer:
                self.embed.description = f"Result: Player wins (+ {coin(self.ctx.guild.id)} {self.amount})"
                self.embed.set_field_at(
                    1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
                return 1
            elif total_dealer > total_player:
                self.embed.description = f"Result: Dearler wins (- {coin(self.ctx.guild.id)} {self.amount})"
                self.embed.set_field_at(
                    1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
                return -1
            else:
                self.embed.description = f"Result: Tie"
                self.embed.set_field_at(
                    1, name=f"Dealer Hand", value=f"{dTotal}\n\nScore: {sum(self.dCardNum)}", inline=True)
                return 0


class Bj(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 60, BucketType.user)
    async def bj(self, ctx, amount: amountconverter):
        ctx.defer()
        bj_amount = 50000
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if bal is None:
            await open_account(ctx.guild.id, ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > bj_amount:
                    amount = bj_amount
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > bj_amount:
                    amount = bj_amount
        if amount > bal['cash']:
            await ctx.send('You do not have enough money to BJ that much')
            ctx.command.reset_cooldown(ctx)
            return
        elif amount <= 0 or amount > bj_amount:
            await ctx.send(f'You cannot BJ 0 , less or more then {bj_amount}')
            ctx.command.reset_cooldown(ctx)
            return

        self.cards = ['<:10C:1147776234466590810> 10', '<:10D:1147776375269380106> 10', '<:10H:1147776402050011236> 10', '<:10S:1147776426846736504> 10', '<:2C:1147776461877563412> 2', '<:2D:1147776571520864286> 2', '<:2H:1147776602919411763> 2', '<:2S:1147776656661037056> 2', '<:3C:1147776740748439662> 3', '<:3D:1147776779059212318> 3', '<:3H:1147776801624572006> 3', '<:3S:1147776840342179922> 3', '<:4C:1147776866942459964> 4', '<:4D:1147776891621757011> 4', '<:4H:1147776931887071364> 4', '<:4S:1147776969778397305> 4', '<:5C:1147777008017870889> 5', '<:5D:1147777032625852506> 5', '<:5H:1147777070542372874> 5', '<:5S:1147777094491848726> 5', '<:6C:1147777136678158406> 6', '<:6D:1147777171037896815> 6', '<:6H:1147777204651040768> 6', '<:6S:1147777234841645126> 6', '<:7C:1147777270677770321> 7', '<:7D:1147777310066479105> 7', '<:7H:1147777337673400390> 7', '<:7S:1147777379368976474> 7', '<:8C:1147777413254742077> 8', '<:8H:1147777546138693632> 8', '<:8D:1147777589793005669> 8', '<:8S:1147777642611875921> 8', '<:9C:1147777674790588508> 9', '<:9D:1147777706268831794> 9', '<:9H:1147777744302780416> 9', '<:9S:1147777779216158730> 9', '<:AC:1147777810979631125> A', '<:AD:1147777839282794576> A', '<:AH:1147777870173851688> A', '<:AS:1147777908027445330> A' , '<:JC:1147783707319615518> Jack', '<:JD:1147783757470904370> Jack', '<:JH:1147783825917743135> Jack', '<:JS:1147783870499000420> Jack', '<:KC:1147783909338259466> King', '<:KD:1147783938379616346> King', '<:KH:1147783968909963354> King', '<:KS:1147784005584961606> King', '<:QC:1147784027072372746> Queen', '<:QD:1147784060677136395> Queen', '<:QH:1147784089399722026> Queen', '<:QS:1147784116499120138> Queen']
        dCARD = []
        dCardNum = []
        dDrawnCard = await bjview.take_card(self)
        dCARD.append(dDrawnCard)
        dDrawnCard = dDrawnCard.split()
        if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
            dDrawnCard[1] = "10"
        elif dDrawnCard[1] == "A":
            dDrawnCard[1] = "11"
        dCardNum.append(int(dDrawnCard[1]))
        dCardNum = await bjview.eval_ace(self, dCardNum)

        while sum(dCardNum) <= 16:
            dDrawnCard = await bjview.take_card(self)
            dCARD.append(dDrawnCard)
            dDrawnCard = dDrawnCard.split()
            if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
                dDrawnCard[1] = "10"
            elif dDrawnCard[1] == "A":
                dDrawnCard[1] = "11"
            dCardNum.append(int(dDrawnCard[1]))
            dCardNum = await bjview.eval_ace(self, dCardNum)

        # player first turn
        pCARD = []
        pCardNum = []
        pDrawnCard = await bjview.take_card(self)
        pCARD.append(pDrawnCard)
        pDrawnCard = pDrawnCard.split()
        if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
            pDrawnCard[1] = "10"
        elif pDrawnCard[1] == "A":
            pDrawnCard[1] = "11"
        pCardNum.append(int(pDrawnCard[1]))

        # 2nd turn
        pDrawnCard = await bjview.take_card(self)
        pCARD.append(pDrawnCard)
        pDrawnCard = pDrawnCard.split()
        if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
            pDrawnCard[1] = "10"
        elif pDrawnCard[1] == "A":
            pDrawnCard[1] = "11"
        pCardNum.append(int(pDrawnCard[1]))
        pCardNum = await bjview.eval_ace(self, pCardNum)
        pTotal = " "
        dTotal = " "
        for x in pCARD:
            x = x.split()
            pTotal += f"{x[0]}"
        y = dCARD[0]
        y = y.split()

        # embed
        embed = discord.Embed(
            description="`hit` - take another card\n`stand` - end the game\n`double down` - double your bet, hit once, then stand", color=0xebd691)
        embed.set_author(
            name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name=f"**Your Hand**",
                        value=f"{pTotal}\n\nScore: {sum(pCardNum)}", inline=True)
        embed.add_field(name=f"**Dealer Hand**",
                        value=f"{y[0]} <:BACK:1147778438359429120>\n\nScore: {dCardNum[0]}\n", inline=True)
        await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, ctx.author.id, ctx.guild.id)
        view = bjview(timeout=180, ctx=ctx, cards=self.cards, dCARD=dCARD,
                      dCardNum=dCardNum, pCARD=pCARD, pCardNum=pCardNum, embed=embed, amount=amount)
        await ctx.send(embed=embed, view=view)

    @bj.error
    async def bj_error(self ,ctx ,error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention} game is already going")
        else :
            ctx.command.reset_cooldown(ctx)
            return


async def setup(client):
    await client.add_cog(Bj(client))
