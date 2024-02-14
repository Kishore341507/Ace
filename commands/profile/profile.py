import io
import random

import discord
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from database import bembed, check_channel, check_perms, client


############################### FETCH USER'S LEVEL ###############################
def get_level(xp):
  levels = [
      0, 100, 150, 200, 300, 400, 500, 600, 700, 850, 1000, 1200, 1400, 1600,
      1800, 2000, 2200, 2400, 2600, 2850, 3100, 3350, 3600, 3900, 4200, 4500,
      4800, 5100, 5400, 5750, 6100, 6450, 6800, 7200, 7600, 8000, 8400, 8800,
      9200, 9600, 10000, 10500, 11000, 11500, 12000, 12500, 13000, 13500,
      14000, 14550, 15100, 15650, 16200, 16750, 17300, 17900, 18500, 19150,
      19800, 20450, 21100, 21750, 22400, 23100, 23800, 24500, 25200, 25900,
      26600, 27300, 28000, 28800, 29600, 30400, 31200, 32000, 32800, 33600,
      34400, 35200, 36000, 36900, 37800, 38700, 39600, 40500, 41400, 42300,
      43200, 44100, 45000, 46000, 47000, 48000, 49000, 50000, 52000, 54000,
      56000, 58000, 60000
  ]

  # In case the user is maxed out
  level = 100
  current_xp = xp - sum(levels)
  next_xp = current_xp + 1

  accumulated_xp = 0
  for i in range(1, len(levels)):
    if xp >= (accumulated_xp + levels[i]):
      accumulated_xp += levels[i]
    else:
      level = i - 1
      current_xp = xp - accumulated_xp
      next_xp = levels[i]
      break
  return level, current_xp, next_xp


############################### FETCH AN IMAGE FROM URL(BG) ############################
def fetch_image_from_url(url):
  try:
    response = requests.get(url)

    # Open the image using Pillow
    image = Image.open(io.BytesIO(response.content))
    image = image.resize(size=(800, 600))
    return image

  except:
    return None


############################### THE 3 CARDS IN PROFILE  ###############################
def fetch_empty_card():
  image_size = (150, 150)
  image = Image.new('RGB', image_size, (51, 51, 51))
  image = ImageOps.expand(image, border=5,
                          fill='white')  # Added white border
  return image

def fetch_level_card(level, current_xp, required_xp):
  try:
    border_width = 3

    # Calculate the percentage of completion
    percentage = min(100, (current_xp / required_xp) * 100)

    # Create a new image with a desired background
    image = fetch_empty_card()
    image_size = (150, 150)
    draw = ImageDraw.Draw(image)

    # Draw the outer circle
    draw.ellipse(
        [(border_width + 10, border_width + 10),
         (image_size[0] - border_width, image_size[1] - border_width)],
        width=border_width,
        outline=(74, 74, 74))

    # Calculate the angle based on the percentage
    angle = 360 * (percentage / 100)

    # Draw the gradient progress arc
    draw.arc([(border_width + 10, border_width + 10),
              (image_size[0] - border_width, image_size[1] - border_width)],
             start=90,
             end=90 + angle,
             width=border_width,
             fill=(255, 192, 30))

    # Draw the text
    font_30 = ImageFont.truetype('./profile_files/fonts/arial.ttf', size=30)
    font_20 = ImageFont.truetype('./profile_files/fonts/arial.ttf', size=20)

    # To center the level text in card
    x_level_text, y_level_text = 80, 40
    x_level_value, y_level_value = 80, 70
    x1_line, y1_line, x2_line, y2_line = 60, 91, 100, 91
    x_exp, y_exp = 80, 100

    # Calculate the size of the text
    left_level_text, top_level_text, right_level_text, bottom_level_text = font_20.getbbox(
        "Level")
    width_level_text = right_level_text - left_level_text
    height_level_text = bottom_level_text - top_level_text

    left_level_value, top_level_value, right_level_value, bottom_level_value = font_30.getbbox(
        str(level))
    width_level_value = right_level_value - left_level_value
    height_level_value = bottom_level_value - top_level_value

    left_exp, top_exp, right_exp, bottom_exp = font_20.getbbox(
        f"{current_xp}/{required_xp}")
    width_exp = right_exp - left_exp
    height_exp = bottom_exp - top_exp

    # Calculate the position to center the text
    x_level_text = x_level_text - (width_level_text // 2)
    y_level_text = y_level_text - (height_level_text // 2)

    x_level_value = x_level_value - (width_level_value // 2)
    y_level_value = y_level_value - (height_level_value // 2)

    x_exp = x_exp - (width_exp // 2)
    y_exp = y_exp - (height_exp // 2)

    draw.text((x_level_text, y_level_text),
              f"Level",
              fill=(121, 149, 164),
              font=font_20)
    draw.text((x_level_value, y_level_value),
              str(level),
              fill=(255, 255, 255),
              font=font_30)
    draw.line((x1_line, y1_line, x2_line, y2_line), fill=(75, 75, 76), width=2)
    draw.text((x_exp, y_exp),
              f"{current_xp}/{required_xp}",
              fill=(121, 149, 164),
              font=font_20)

    return image
  except Exception as e:
    print(e)
    return None


def fetch_role_card(item_name="Amatuer Gambler", role: discord.role = None):
  try:
    # Create a new image with a desired background
    image = fetch_empty_card()
    draw = ImageDraw.Draw(image)
    text = item_name
    if  role is not None:
      text_color = (role.color.r, role.color.g, role.color.b)
    else:
      text_color = (255, 255, 255)

    if not role:
      icon_img = Image.open('./profile_files/role_icons/no_role.png').convert(
          "RGBA")
      icon_img = icon_img.resize(size=(100, 100))
      image.paste(icon_img, (32, 10), icon_img)
    else:
      try:
        icon_img = fetch_image_from_url(role.icon.url)
        icon_img = icon_img.convert("RGBA")
        icon_img = icon_img.resize(size=(100, 100))
        image.paste(icon_img, (32, 10), icon_img)
      except:
        icon_img = Image.open(
            './profile_files/role_icons/no_role_icon.png').convert("RGBA")
        icon_img = icon_img.resize(size=(100, 100))
        image.paste(icon_img, (32, 10), icon_img)

    # Draw the text
    words = text.split()
    word_lenghts = [len(word) for word in words]
    word_count = len(words)
    text_lenght = len(text)
    font = ImageFont.truetype('./profile_files/fonts/arial.ttf', size=18)
    # To center the text in card
    x_text, y_text = 82, 125

    # Convert the text into box to get its size
    left_text, top_text, right_text, bottom_text = font.getbbox(text)
    width_text = right_text - left_text
    height_text = bottom_text - top_text

    # Calculate the position to center the text
    x_text = x_text - (width_text // 2)
    y_text = y_text - (height_text // 2)

    draw.text((x_text, y_text), text, fill=text_color, font=font)

    return image

  except Exception as e:
    print(e)
    return None


def fetch_lb_card(rank):
  try:

    # Create a new image with a desired background
    image = fetch_empty_card()
    draw = ImageDraw.Draw(image)

    if rank == 1:
      icon_name = "1"
      text_fill = (81, 80, 212)
    elif rank == 2:
      icon_name = "2"
      text_fill = (139, 33, 0)
    elif rank == 3:
      icon_name = "3"
      text_fill = (177, 254, 245)
    elif rank >= 4 and rank <= 10:
      icon_name = "4-10"
      text_fill = (189, 237, 254)
    elif rank >= 11 and rank <= 99:
      icon_name = "11-99"
      text_fill = (189, 237, 254)
    elif rank >= 100 and rank <= 399:
      icon_name = "100-399"
      text_fill = (189, 237, 254)
    elif rank >= 400 and rank <= 699:
      icon_name = "400-699"
      text_fill = (189, 237, 254)
    elif rank >= 700 and rank <= 999:
      icon_name = "700-999"
      text_fill = (240, 206, 28)
    else:
      icon_name = "1000"
      text_fill = (128, 65, 36)

    icon_img = Image.open(f"./profile_files/lb_icons/{icon_name}.png").convert(
        "RGBA")
    image.paste(icon_img, (32, 10), icon_img)

    # Draw the text
    font_30 = ImageFont.truetype('./profile_files/fonts/arial.ttf', size=30)

    # To center the level text in card
    rank_value = f"#{rank}" if rank < 1000 else f"#999+"
    x_rank_value, y_rank_value = 80, 120

    # Convert the text into box to get its size
    left_rank_value, top_rank_value, right_rank_value, bottom_rank_value = font_30.getbbox(
        rank_value)
    width_rank_value = right_rank_value - left_rank_value
    height_rank_value = bottom_rank_value - top_rank_value

    # Calculate the position to center the text
    x_rank_value = x_rank_value - (width_rank_value // 2)
    y_rank_value = y_rank_value - (height_rank_value // 2)

    draw.text((x_rank_value, y_rank_value),
              rank_value,
              fill=text_fill,
              font=font_30)

    return image
  except Exception as e:
    print(e)
    return None


############################### HELPER MODAL INPUTS ###############################
class singleInputModal(discord.ui.Modal, title='...'):

  def __init__(self,
               question,
               placeholder,
               min=None,
               max=None,
               defult=None,
               required=True):
    super().__init__()
    self.question = question
    self.placeholder = placeholder
    self.min = min
    self.max = max
    self.value = None
    self.defult = defult
    self.required = required
    self.input = discord.ui.TextInput(label=self.question,
                                      placeholder=self.placeholder,
                                      min_length=self.min,
                                      max_length=self.max,
                                      default=self.defult,
                                      required=self.required)

    self.add_item(self.input)

  async def on_submit(self, interaction: discord.Interaction):
    self.value = self.input.value
    await interaction.response.defer()


class multiInputModal(discord.ui.Modal, title='...'):

  def __init__(self,
               questions: list,
               placeholders: list,
               min: list,
               max: list,
               defults: list = None,
               required: list = None):
    super().__init__()
    self.questions = questions
    self.placeholders = placeholders
    self.defults = defults
    if not defults:
      self.defults = [None] * len(questions)
    if not required:
      self.required = [None] * len(questions)
    self.required = required
    self.values = []
    for i in range(len(questions)):
      self.input = discord.ui.TextInput(label=self.questions[i],
                                        placeholder=self.placeholders[i],
                                        default=self.defults[i],
                                        min_length=min[i],
                                        max_length=max[i],
                                        required=self.required[i])
      self.add_item(self.input)

  async def on_submit(self, interaction: discord.Interaction):
    for item in self.children:
      self.values.append(item.value)
    await interaction.response.defer()


############################### PROFILE CUSTOMIZATION VIEWS ###############################

class EditProfileButton(discord.ui.View):
  def  __init__(self, user_id):
    super().__init__(timeout=180)
    self.user_id = user_id
    self.message = None

  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if interaction.user.id != self.user_id:
      await interaction.response.send_message(embed=bembed("<:pixel_error:1187995377891278919> Not your interaction.", discord.Color.brand_red()), ephemeral=True)
    return interaction.user.id == self.user_id

  async def on_timeout(self) -> None:
    try:
      await self.message.edit(view=None)
    except Exception as e:
      pass

  @discord.ui.button(label="Customize", style=discord.ButtonStyle.blurple, emoji="🛠️", custom_id="customize_button")
  async def customize_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    data = await client.db.fetchrow("SELECT * FROM profiles WHERE user_id = $1", interaction.user.id)
    modal = multiInputModal(["Enter a new nickname.", "Enter a new description.", "Enter a new Backgroud URL.", "Enter a blur value for BG."], ["Text Input.", "Text Input.", "Must be valid URL.", "Must be a number in range 1-10."],[1, 1, 1, 1], [30, 135, 250, 2], [data['nick'], data['description'], data['bg_url'], data['bg_blur']], [True, True, True, True])
    modal.title = f"{interaction.user.display_name}'s Profile Settings"
    modal.color = discord.Color.blurple()
    await interaction.response.send_modal(modal)
    await modal.wait()
    if modal.values:
      name = modal.values[0]
      description = modal.values[1]
      bg_url = modal.values[2]
      bg_blur = modal.values[3]

      error = "⚠️ Following errors occured during execution:\n"
      if bg_url:
        image = fetch_image_from_url(bg_url)
        if image:
          bg_url = bg_url
        else:
          bg_url = data['bg_url']
          error = error + "- Invalid URL for background.\n"
      if modal.values[1]:
        validValue = True
        try:
          blur = int(bg_blur)
        except:
          blur=data["blur"]
          error = error + "- Blur value must be an Integer.\n"
          validValue = False
        if validValue is True:
          if blur >= 1 and blur <= 10:
            bg_blur = blur
          else:
            error = error + "- Blur value must be an Integer between 1-10.\n"
      if error != "⚠️ Following errors occured during execution:\n":
        await interaction.followup.send(error, ephemeral=True)

      result = await client.db.execute(
        "UPDATE profiles SET nick = $1, description = $2, bg_url = $3, bg_blur = $4 WHERE user_id = $5",
        name, description, bg_url, bg_blur, interaction.user.id)
      if result != "UPDATE 1":
        await interaction.followup.send("done", ephemeral=True)
        await interaction.followup.send_message(
            "⚠️ An error occured. You may report this in our support server.",
            ephemeral=True)
      else:
        await interaction.followup.send(embed=bembed(
          f"[**__{interaction.user.display_name}__**]\n\n- **Nickname**: {name}\n- **Description**: {description}\n- **Backgroud**: {bg_url}\n- **Blur**: {bg_blur}"
      ).set_author(name="Current Settings", icon_url=interaction.user.display_avatar), ephemeral=True)
      return






"""
class editProfileView(discord.ui.View):

  def __init__(self, nickname, description, bg_url, bg_blur):
    super().__init__(timeout=180)
    self.nickname = nickname
    self.description = description
    self.bg_url = bg_url
    self.bg_blur = bg_blur

  @discord.ui.button(label="Edit Nickname",
                     style=discord.ButtonStyle.blurple,
                     custom_id="edit_nickname_button")
  async def edit_nickname_button(self, interaction: discord.Interaction,
                                 button: discord.ui.Button):
    modal = singleInputModal("Enter a new nickname?",
                             "Enter your new nickname", 1, 30, self.nickname,
                             True)
    modal.title = "Edit Nickname"
    await interaction.response.send_modal(modal)
    await modal.wait()
    if modal.value:
      self.nickname = modal.value
      return

  @discord.ui.button(label="Edit Description",
                     style=discord.ButtonStyle.blurple,
                     custom_id="edit_description_button")
  async def edit_description_button(self, interaction: discord.Interaction,
                                    button: discord.ui.Button):
    modal = singleInputModal("Enter a new description?",
                             "Enter your new description", 1, 140,
                             self.description, True)
    modal.title = "Edit Description"
    await interaction.response.send_modal(modal)
    await modal.wait()
    if modal.value:
      self.description = modal.value
      return
    else:
      print("Something went wrong")

  @discord.ui.button(label="Customize Background",
                     style=discord.ButtonStyle.blurple,
                     custom_id="customize_background_button")
  async def customize_background_button(self, interaction: discord.Interaction,
                                        button: discord.ui.Button):
    modal = multiInputModal([
        "Enter a new background URL.", "Enter the blur value for background."
    ], ["https://", "Must be an Integer between 1-10"], [1, 1], [200, 2],
                            [self.bg_url, self.bg_blur], [True, True])
    modal.title = "Customize Background"
    await interaction.response.send_modal(modal)
    await modal.wait()
    error = "⚠️ Following errors occured during execution:\n"
    if modal.values[0]:
      image = fetch_image_from_url(modal.values[0])
      if image:
        self.bg_url = modal.values[0]
      else:
        error = error + "- Invalid URL for background.\n"
    if modal.values[1]:
      validValue = True
      try:
        blur = int(modal.values[1])
      except:
        error = error + "- Blur value must be an Integer.\n"
        validValue = False
      if validValue is True:
        if blur >= 1 and blur <= 10:
          self.bg_blur = blur
        else:
          error = error + "- Blur value must be an Integer between 1-10.\n"
    if error != "⚠️ Following errors occured during execution:\n":
      await interaction.followup.send(error, ephemeral=True)
    return

  @discord.ui.button(label="Save Changes",
                     style=discord.ButtonStyle.green,
                     custom_id="commit_changes_button")
  async def commit_changes_button(self, interaction: discord.Interaction,
                                  button: discord.ui.Button):
    result = await client.db.execute(
        "UPDATE profiles SET nick = $1, description = $2, bg_url = $3, bg_blur = $4 WHERE user_id = $5",
        self.nickname, self.description, self.bg_url, self.bg_blur,
        interaction.user.id)
    if result == "UPDATE 1":
      avatar = interaction.user.display_avatar.url if interaction.user.display_avatar else interaction.user.avatar.url
      if avatar is None:
        avatar = interaction.user.default_avatar.url
      await interaction.response.edit_message(embed=bembed(
          f"**__Current Settings__**\n\n- **Nickname**: {self.nickname}\n- **Description**: {self.description}\n- **Backgroud**: {self.bg}\n- **Blur**: {self.bg_blur}"
      ).set_author(name="Edit Profile", icon_url=avatar))
    else:
      await interaction.response.send_message(
          "⚠️ An error occured. You may report this in our support server.",
          ephemeral=True)


class editProfileButton(discord.ui.View):

  def __init__(self, user_id, nickname, description, bg_url, bg_blur):
    super().__init__(timeout=60)
    self.user_id = user_id
    self.nickname = nickname
    self.description = description
    self.bg_url = bg_url
    self.bg_blur = bg_blur
    self.msg = None

  async def on_timeout(self):
    for child in self.children:
      child.disabled = True
    await self.msg.edit(view=self)

  async def interaction_check(self, interaction: discord.Interaction):
    if interaction.user.id != self.user_id:
      await interaction.response.send_message(embed=bembed(
          "<:pixel_error:1187995377891278919> Failed: Not your interaction."),
                                              ephemeral=True)
      return False
    else:
      return True

  @discord.ui.button(label='Edit Profile',
                     style=discord.ButtonStyle.blurple,
                     custom_id="edit_profile")
  async def edit_profile(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
    avatar = interaction.user.display_avatar.url if interaction.user.display_avatar else interaction.user.avatar.url
    if avatar is None:
      avatar = interaction.user.default_avatar.url
    await interaction.response.send_message(embed=bembed(
        f"**__Current Settings__**\n\n- **Nickname**: {self.nickname}\n- **Description**: {self.description}\n- **Backgroud**: {self.bg}\n- **Blur**: {self.bg_blur}"
    ).set_author(name="Edit Profile", icon_url=avatar),
                                            view=editProfileView(
                                                self.nickname,
                                                self.description, self.bg_url,
                                                self.bg_blur),
                                            ephemeral=True)
    return
  """

############################### THE PROFILE COG STARTS ###############################
class profile(commands.Cog):

  def __init__(self, client):
    self.client = client
    # Created a cooldown mapping with a BucketType.user and added 60-second cooldown to add the xp
    self.cooldown_mapping = commands.CooldownMapping.from_cooldown(
        1, 60, commands.BucketType.user)

  # Adding random 15-25 xp when a command is run with the declared cooldown
  @commands.Cog.listener()
  async def on_command(self, ctx):
    # Check if the xp addition is on cooldown for the user
    cooldown = self.cooldown_mapping.get_bucket(ctx.message)
    retry_after = cooldown.update_rate_limit()

    # If the user is on cooldown then return
    if retry_after:
      return
    else:
      xp_amount = random.randint(15, 25)
      #
      # Add the xp to the user
      result = await client.db.execute(
          "UPDATE profiles SET xp = xp + $1 WHERE user_id = $2", xp_amount,
          ctx.author.id)
      if result == "UPDATE 0":
        await client.db.execute(
            "INSERT INTO profiles (user_id, xp) VALUES ($1, $2) ON CONFLICT (user_id) DO NOTHING",
            ctx.author.id, xp_amount)

  ############################### MAIN COMMAND ###############################
  @commands.hybrid_command(name="profile", aliases=["p"])
  @commands.check(check_perms)
  @commands.check(check_channel)
  async def profile(self, ctx, user: discord.Member = None):
    fetch_view = 0
    user = user or ctx.author
    if user.bot:
      return
    if user.id == ctx.author.id:
      fetch_view = 1

    data = await client.db.fetchrow(
        "SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY xp DESC) AS rank, user_id, xp, nick, description, bg_blur, bg_url FROM profiles) as profiles WHERE user_id = $1", user.id)
    if data is None:
      await client.db.execute(
          "INSERT INTO profiles (user_id, xp) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
          user.id)
      data = await client.db.fetchrow(
          "SELECT * FROM profiles WHERE user_id = $1", user.id)
    default_bg = "https://images.wallpapersden.com/image/download/3d-photoshop-nature_aGZoapSZmpqtpaSklG1lZa1rZWU.jpg"

    bg = fetch_image_from_url(data["bg_url"] if data['bg_url'] else default_bg)
    if bg:
      bg = bg.convert("RGBA")
    else:
      bg = fetch_image_from_url(default_bg)
      bg = bg.convert("RGBA")
    bg = bg.filter(
        ImageFilter.GaussianBlur(
            radius=data['bg_blur'] if data['bg_blur'] else 5))
    ui = Image.open("./profile_files/ui_image.jpg").convert("RGBA")

    avatar = user.display_avatar if user.display_avatar else user.avatar
    pfp = avatar if user.avatar else user.default_avatar
    pfp = Image.open(io.BytesIO(await pfp.read())).convert("RGBA")
    pfp = pfp.resize((140, 140))

    ui.paste(pfp, (15, 60), pfp)

    # Fetching the user's info to show in the profile
    name = user.nick if user.nick else user.display_name
    name = name[:20] + "..." if len(name) > 20 else name
    rank = data["rank"]
    level, exp, exp_next = get_level(int(data['xp']))
    nickname = data['nick'] if data['nick'] else "Ace Aspirant"
    nickname = nickname[:30] + "..." if len(nickname) > 30 else nickname
    description = data['description'] if data[
        'description'] else "Seizing the title of Novice Nettler and conquering the casino challenges. With each bet aiming for triumph in gambling arena."

    if fetch_view == 1:
      view = EditProfileButton(user.id)
    else:
      view = None

    current_length = 0
    new_description = ""
    for word in description.split():
      current_length += len(word) + 1  # Add 1 for the space between words
      if current_length > 40:
        new_description += "\n" + word + " "
        current_length = len(
            word) + 1  # Reset the current length for the next line
      else:
        new_description += word + " "
    description = new_description[:135] + "..." if len(
        new_description) > 139 else new_description

    draw = ImageDraw.Draw(ui)
    font_30 = ImageFont.truetype("./profile_files/fonts/arial.ttf", size=30)
    font_24 = ImageFont.truetype("./profile_files/fonts/arial.ttf", size=24)
    font_20 = ImageFont.truetype("./profile_files/fonts/arial.ttf", size=20)
    font_16 = ImageFont.truetype("./profile_files/fonts/arial.ttf", size=16)

    draw.text((15, 10),
              f"{name}'s Profile Card",
              fill=(255, 255, 255),
              font=font_30)
    draw.text((15, 200), f"Rank: {rank}", fill=(255, 255, 255), font=font_30)
    draw.text((175, 60), f"{nickname}", fill=(255, 255, 255), font=font_24)
    draw.text((175, 90), f"{description}", fill=(255, 255, 255), font=font_20)
    # draw.multiline_textbbox((175, 90), description, font=font_24)

    # draw.text((175, 200), f"Xp: ", fill=(255, 255, 255), font=font_30)
    # draw.text((225, 190),
    #           f"exp",
    #           fill=(255, 255, 255),
    #           font=font_16)
    # draw.text((490, 190),
    #           f"{exp_next}",
    #           fill=(255, 255, 255),
    #           font=font_16)

    # bar = {"x": 225, "y": 212, "width": 300, "height": 16}

    # draw.rectangle((bar['x'], bar['y'], bar['x'] + bar['width'],
    #                 bar['y'] + bar['height']),
    #                fill=(0, 0, 0))  # draw background
    # draw.rectangle(
    #     (bar['x'], bar['y'], bar['x'] +
    #     ((exp / exp_next) * bar['width']), bar['y'] + bar['height']),
    #     fill=(255, 255, 255))  # draw progress bar

    ############ Perperations for fetching the 3 profile cards ############
    store_docs = await client.db.fetch(
        "SELECT * FROM store WHERE guild_id = $1 ORDER BY id DESC",
        ctx.guild.id)
    store_docs = {item['id']: dict(item)
                  for item in store_docs} if store_docs else {}

    highest_bought_item = None
    highest_id = 0
    topmost_role = None
    roles = None
    # Fetching the topmost item bought by the user in the server (determined through item id) [To display in second card]
    for item in store_docs:
      if store_docs[item]['buyers'] and user.id in store_docs[item]['buyers'] and store_docs[item]['id'] > highest_id:
        highest_bought_item = store_docs[item]['name']
        roles = store_docs[item]['roles'] if store_docs[item]['roles'] else None
        highest_id = store_docs[item]['id']

    # Fetching the topmost role in the rewards of the topmost item bought by the user in the server (To display in second card)
    if roles:
      for role_id in roles:
        role = ctx.guild.get_role(role_id)
        if role and (topmost_role is None
                     or role.position > topmost_role.position):
          topmost_role = role

    # Fetching the leaderboard rank of the user in the server (determined by total bank and cash held by him)
    lb_rank = await client.db.fetchval(
        "SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (bank + cash) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2",
        user.guild.id, user.id)

    ############ FETCHING THE 3 DISPLAY CARDS ############
    title_empty = fetch_empty_card()
    card1 = fetch_level_card(level, exp, exp_next)
    card2 = fetch_role_card(
        highest_bought_item if highest_bought_item else "Amatuer Gambler",
        topmost_role if topmost_role else None)
    card3 = fetch_lb_card(int(lb_rank))

    card1 = card1.convert("RGBA") if card1 else title_empty
    card2 = card2.convert("RGBA") if card2 else title_empty
    card3 = card3.convert("RGBA") if card3 else title_empty

    ui.paste(card1, (25, 260), card1)
    ui.paste(card2, (203, 260), card2)
    ui.paste(card3, (383, 260), card3)

    bg.paste(ui, (120, 80), ui)

    card = io.BytesIO()
    bg.save(card, format='png')
    card.seek(0)

    # Sending the profile card
    file = discord.File(card, filename="profile.png")
    msg = await ctx.send(file=file, view=view)
    view.message = msg

  ############################### DELETE THESE LATER ###############################

  @commands.hybrid_command(name="set_bg", aliases=["setbg"])
  @commands.check(check_channel)
  async def set_bg(self, ctx, bg_url: str):
    if not bg_url.startswith("https://"):
      await ctx.send(
          "Invalid URL. Please provide a valid URL starting with `https://`.")
      return
    await client.db.execute("UPDATE profiles SET bg_url = $1 WHERE user_id = $2",
                            bg_url, ctx.author.id)
    await ctx.send("Background set successfully!")

  @commands.hybrid_command(name="set_blur", aliases=["setbl"])
  @commands.check(check_channel)
  async def set_blur(self, ctx, blur):
    blur = int(blur)
    if blur < 1 or blur > 10:
      await ctx.send("Blur value must be between 1 and 10.")
      return
    await client.db.execute(
        "UPDATE profiles SET bg_blur = $1 WHERE user_id = $2", blur,
        ctx.author.id)
    await ctx.send("Blur set successfully!")

  @commands.hybrid_command(name="card", aliases=["c", "gen"])
  @commands.check(check_channel)
  @commands.check(check_perms)
  async def gen_card(self,
                       ctx,
                       card,
                       input1: str = "1",
                       input2: str = "2",
                       input3: str = "3"):
    try:
      if card in ["level", "lvl"]:
        level = int(input1)
        current_xp = int(input2)
        required_xp = int(input3)
        image = fetch_level_card(int(level), int(current_xp), int(required_xp))
      elif card in ["lb", "leaderboard"]:
        rank = int(input1)
        image = fetch_lb_card(int(rank))
      elif card in ["role", "rl"]:
        item_name = input1
        if item_name == "1":
          item_name = "Amatuer Gambler"
        role: discord.Role = ctx.guild.get_role(int(input2))
        image = fetch_role_card(item_name, role)
        if not image:
          image = fetch_role_card(item_name)
      else:
        raise Exception

      if image:
        image = image.convert("RGBA")
      else:
        raise Exception("No image found.")

      card = io.BytesIO()
      image.save(card, format='png')
      card.seek(0)

      file = discord.File(card, filename="card.png")
      await ctx.send(file=file)
    except Exception as e:
      print(e)
      await ctx.send("⚠️ Uh oh! Something went wrong. Please try again later.")


async def setup(client):
  await client.add_cog(profile(client))
