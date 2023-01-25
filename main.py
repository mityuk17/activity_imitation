import asyncio
import os

from opentele.api import API, UseCurrentSession
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest


def get_phrases():
    with open('phrases.txt', 'r') as file:
        data = file.readlines()
    data = [i.strip() for i in data]
    return  data
def get_sessions():
    if not os.path.exists('sessions'):
        return False
    with os.scandir('sessions') as files:
        subdir = [file.name for file in files if file.is_dir() and os.path.exists(f'sessions/{file.name}/tdata')]
    print('Собрано сессий:', len(subdir))
    return subdir
async def get_channel(client: TelegramClient):
    with open('channel_link.txt', 'r') as file:
        data = file.readlines()[0].strip().strip('https://').strip('t.me/').strip('joinchat/')
    try:
        channel = await client.get_entity(data)
    except Exception as e:
        print(e)
        channel = None
    return [data,channel]
from opentele.td import TDesktop
async def main(post_num):

    sessions = get_sessions()
    phrases = get_phrases()
    post = int(input("Введите ссылку на пост:").split('/')[-1])

    for session in sessions:
        tdataFolder = f'sessions/{session}/tdata'
        tdesk = TDesktop(tdataFolder)
        client = await tdesk.ToTelethon(f'session_files/{session}',UseCurrentSession, api= API.TelegramAndroid.Generate(session))
        async with client:
            channel = await get_channel(client)
            try:
                await client(JoinChannelRequest(channel[1]))
            except Exception as e:
                print(e)
                try:
                    await client(ImportChatInviteRequest(channel[0]))
                except Exception as e:
                    print(e)
            msg = await client.get_messages(channel[1].id, post)
            await msg.reply(phrases.pop(), quote=True)
def start():
    while True:
        post_num = input('Введите номер поста(счёт начинается с последнего поста в канале):')
        if post_num.isdigit():
            post_num = int(post_num)
            break
        else:
            print('Некорректное значение.')
    asyncio.run(main(post_num))
