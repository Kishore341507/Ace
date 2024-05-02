# Casino and PVC bot for Discord
> [!NOTE]
> The bot currently supports Python 3.11 correctly and might malfunction a bit with python 3.12.

## Key Features

- A customized shop for your server to enhance the grinding experience of Casino.
- Easy to manage with a manager supported role to setup and manage the bot.
- Minimal ping time and down time.

## Installing

### You will need to install all the required python libraries. To do so follow these steps:
In your teminal run the command mentioned below. [Make sure you have python already set up for your system.].
```sh
$ pip install -r requirements.txt
```
### You will now have to additionally install the latest version of discord.py library. Follow the upcoming steps to do so.
```sh
$ git clone https://github.com/Rapptz/discord.py
$ cd discord.py
$ python3 -m pip install -U .[voice]
```
### To set up your postgresql database environment, do the following steps. 
  1. In the parent directory open migrations folder and you will see multiple sql files.
  2. Open them in right order from V0,V1....so on and run the queries inside them in your postgresql db.Open them in right order from V0,V1....so on and run the queries inside them in your postgresql db.
  3. Now your database is all set to work with the bot. You just have to paste the DB link in .env file.

### Follow the following steps to run the main ace.py file properly
  1. In the parent directory create a file named .env
  2. Open the file and write the following contents inside to
     - TOKEN = "xyz...." [This is your discord bot application token, paste it here.]
     - DB = "abc...." [This is your Postgresql database connection url.]
     - The file should look something like this
     ```py
        TOKEN = "NzExNTIxNTg2NDMwNTIxNTc1.Xs1NTw................2aNV1eyO3s"
        DB = "postgresql://username:password@host:port/database"
     ```
  3. Now your bot environment is all set up.

## Links

- [TickAp Website](https://tickap.com/)
- [Invite me to your server](https://tickap.com/bots)
- [TickAp Support Server](https://discord.gg/KeDwvbU5Zf)
- [Discord.py documentation](https://discordpy.readthedocs.io/en/latest/index.html)