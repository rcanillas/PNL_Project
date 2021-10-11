import os
import discord
import time
import re
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
msg_count = {}
target_answerers = {}
target_modelers = {}
sentence_buffer = {}


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
    target_name = str(message.author.name)
    str_author = str(message.author)
    prefix = "user_data"
    if message.author == client.user:
        return
    if message.channel.type == discord.ChannelType.private:
        print(target_name)
        print(active_sessions.keys())
        if target_name not in active_sessions.keys():
            # print("session not active")
            active_sessions[target_name] = False
            session_count[target_name] = 0
            msg_count[target_name] = 0

        if not active_sessions[target_name]:
            if f"Bonjour {bot_name}" in message.content:
                active_sessions[target_name] = True
                sentence_buffer[target_name] = ""
                if target_name not in target_modelers.keys():
                    target_modelers[target_name] = Modeler(target_name)
                    if not os.path.exists(f"{prefix}/{str_author}"):
                        os.makedirs(f"{prefix}/{str_author}")
                    target_modelers[target_name].save_profile(f"{prefix}/{str_author}/{str_author}_profile.json")
                else:
                    target_modelers[target_name].load_profile(f"{prefix}/{str_author}/{str_author}_profile.json")
                time.sleep(1)
                await message.channel.send(f"Bonjour {target_name} !")
                time.sleep(.7)
                await message.channel.send(f"Je suis {bot_name}, le robot qui écoute les problèmes ! Mon rôle est de déchiffrer tes 'méta-programmes' afin d'identifier les meilleurs vecteurs d'amélioration selon ta personnalité.")
                time.sleep(1)
                await message.channel.send("Ainsi, j'aimerais que tu me parles d'un élément de ta vie que tu souhaiterais améliorer afin que l'on puisse ensemble l'analyser en profondeur. Cela peut être lié aux hobbies, au travail, aux relations ...")
                time.sleep(1.5)
                await message.channel.send("Note: je ne réponds que lorsque que ton message sera terminé par un point.")
                session_count[target_name] += 1
                session_answerer = Answerer(session_count)
                session_answerer.load_answer_list("templates/meta_answers.csv")
                target_answerers[target_name] = session_answerer
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
                active_sessions[target_name] = False
                if not os.path.exists(f"{prefix}/{str_author}"):
                    os.makedirs(f"{prefix}/{str_author}")
                print(target_modelers[target_name].profile)
                target_answerers[target_name].save_conversation_data(
                    f"{prefix}/{str_author}/{str_author}_{datetime.now()}_{session_count[target_name]}.csv")
                target_modelers[target_name].save_profile(f"{prefix}/{str_author}/{str_author}_profile.json")
            else:
                print("normal_message")
                print(sentence_buffer[target_name])
                session_answerer = target_answerers[target_name]
                session_modeler = target_modelers[target_name]
                if (" ." in message.content) or (" !" in message.content) or (" ?" in message.content):
                    sentence_list = [msg for msg in re.split('(?<=[.!?])+', message.content)]
                    if sentence_buffer[target_name] != "":
                        current_sentence = sentence_buffer[target_name] + ' ' + sentence_list[0]
                    else:
                        current_sentence = sentence_list[0]
                    session_answerer.update_conversation(current_sentence)
                    session_modeler = session_modeler.update_profile(current_sentence)
                    session_answerer.update_target_profile(session_modeler.profile)
                    sentence_buffer[target_name] = ""
                    msg_count[target_name] += len(sentence_list[:-1])
                    for current_sentence in sentence_list[1:-1]:
                        session_answerer.update_conversation(current_sentence)
                        session_modeler = session_modeler.update_profile(current_sentence)
                        session_answerer.update_target_profile(session_modeler.profile)
                    if sentence_list[-1] == "":
                        sentence_buffer[target_name] = ""
                        session_answerer.nb_answers = msg_count[target_name]
                        response = session_answerer.get_answer()
                        response_time = max(1.0, 0.2 * len(message.content.split(" ")))
                        time.sleep(response_time)
                        await message.channel.send(response)
                    else:
                        sentence_buffer[target_name] = sentence_list[-1]
                else:
                    if sentence_buffer[target_name] != "":
                        sentence_buffer[target_name] = sentence_buffer[target_name] + ' ' + message.content
                    else:
                        sentence_buffer[target_name] = message.content



    else:
        await message.channel.send(f"Venez discutez par message privé !")

client.run(TOKEN)
