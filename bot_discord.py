import os
import discord
import time
from datetime import datetime
from dotenv import load_dotenv
from answerer import Answerer
from modeler import Modeler

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
active_sessions = {}
session_count = {}
target_answerers = {}
target_modelers = {}


@client.event
async def on_ready():
    guild = None
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} has connected to Discord !',
          f'{guild.name} (id: {guild.id})')


@client.event
async def on_message(message):
    bot_name = str(client.user).split("#")[0]
    target_name = str(message.author).split("#")[0]
    str_author = str(message.author)
    prefix = "user_data"

    if message.author == client.user:
        return

    if message.channel.type == discord.ChannelType.private:
        # print(message.author)
        if message.author not in active_sessions.keys():
            active_sessions[message.author] = False
            session_count[message.author] = 0

        if not active_sessions[message.author]:
            if f"Bonjour {bot_name}" in message.content:
                active_sessions[message.author] = True
                if message.author not in target_modelers.keys():
                    target_modelers[message.author] = Modeler(target_name)
                    if not os.path.exists(f"{prefix}/{str_author}"):
                        os.makedirs(f"{prefix}/{str_author}")
                    target_modelers[message.author].save_profile(f"{prefix}/{str_author}/{str_author}_profile.json")
                else:
                    target_modelers[message.author].load_profile(f"{prefix}/{str_author}/{str_author}_profile.json")

                time.sleep(1)
                await message.channel.send(f"Bonjour {target_name} !")
                session_count[message.author] += 1
                session_answerer = Answerer(session_count)
                session_answerer.load_answer_list("answer_list.csv")
                target_answerers[message.author] = session_answerer
                # TODO: Potentiellement demander si prise en compte des conversations passées si nb session > 1
                time.sleep(1.5)
                await message.channel.send(f"De quoi allons-nous parler aujourd'hui ?")
                time.sleep(.7)
                await message.channel.send(f"(Écrire 'Merci {bot_name}' pour mettre fin à la discussion)")
            else:
                await message.channel.send(f"Vous pouvez écrire 'Bonjour {bot_name}' pour lancer la discussion !")

        else:
            if message.content == f"Merci {bot_name}":
                print("end_message")
                time.sleep(1)
                await message.channel.send(f"Bonne journée {target_name} !")
                active_sessions[message.author] = False
                if not os.path.exists(f"{prefix}/{str_author}"):
                    os.makedirs(f"{prefix}/{str_author}")
                print(target_modelers[message.author].profile)
                target_answerers[message.author].save_conversation_data(
                    f"{prefix}/{str_author}/{str_author}_{datetime.now()}_{session_count[message.author]}.csv")
                target_modelers[message.author].save_profile(f"{prefix}/{str_author}/{str_author}_profile.json")
            else:
                print("normal_message")
                session_answerer = target_answerers[message.author]
                session_answerer.update_conversation(message.content)
                target_modelers[message.author] = target_modelers[message.author].update_profile(message.content)
                # TODO: update target model here
                response = session_answerer.get_answer()
                response_time = max(1.0, 0.2*len(message.content.split(" ")))
                time.sleep(response_time)
                # response += f" ({response_time} s)"
                await message.channel.send(response)
    else:
        await message.channel.send(f"Venez discutez par message privé !")

client.run(TOKEN)
