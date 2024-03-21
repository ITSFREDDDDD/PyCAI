from contextlib import asynccontextmanager
import websockets
import json
import base64
import os
import shutil
from curl_cffi.requests import Session
from pydub import AudioSegment
from io import BytesIO
from easygoogletranslate import EasyGoogleTranslate as esgt

#███████             ██████      ██     ██  ████
#░██░░░░██  ██   ██  ██░░░░██    ████   ░██ █░░░ █
#░██   ░██ ░░██ ██  ██    ░░    ██░░██  ░██░    ░█
#░███████   ░░███  ░██         ██  ░░██ ░██   ███
#░██░░░░     ░██   ░██        ██████████░██  █░░
#░██         ██    ░░██    ██░██░░░░░░██░██ █
#░██        ██      ░░██████ ░██     ░██░██░██████
#░░        ░░        ░░░░░░  ░░      ░░ ░░ ░░░░░░
# BUILD BY @Falco_TK    (https://github.com/FalcoTK)
# CODE  BY @kramcat     (https://github.com/kramcat)
# CODE  BY @background  (https://github.com/backaround)

# PLEASE IF YOU HAVE SOMTING WRONG DM ME IN DISCORD ASAP! (discord: tokaifalco_)
# ==================================================

__all__ = ['PyCAI2', 'PyAsyncCAI2']


class PyCAI2EX(Exception):
    pass

class ServerError(PyCAI2EX):
    pass

class LabelError(PyCAI2EX):
    pass

class AuthError(PyCAI2EX):
    pass

class PostTypeError(PyCAI2EX):
    pass

class PyAsyncCAI2:
    def __init__(
        self, token: str = None, plus: bool = False
    ):
        self.token = token
        self.plus = plus
        if plus: sub = 'plus'
        else: sub = 'beta'

        self.session = Session(
            headers={
                'User-Agent': 'okhttp/5.0.0-SNAPSHOT'
            }
        )

        setattr(self.session, 'url', f'https://{sub}.character.ai/')
        setattr(self.session, 'token', token)

        self.chat = self.chat(token, self.session)
        self.chat2 = self.chat2(token, None, self.session)



    async def ping(self):
        return self.session.get(
            'https://neo.character.ai/ping/'
        ).json()

    @asynccontextmanager
    async def connect(self, token: str = None):
        try:
            if token == None: key = self.token
            else: key = token

            setattr(self.session, 'token', key)

            try:
                self.ws = await websockets.connect(
                    'wss://neo.character.ai/ws/',
                     extra_headers = {
                        'Cookie': f'HTTP_AUTHORIZATION="Token {key}"',
                    }
                )
            except websockets.exceptions.InvalidStatusCode:
                raise AuthError('Invalid token')

            yield PyAsyncCAI2.chat2(key, self.ws, self.session)
        finally:
            await self.ws.close()

    class chat:
        """Managing a chat2 with a character

        chat.next_message('CHAR', 'CHAT_ID', 'PARENT_ID')
        chat.send_message('CHAR', 'CHAT_ID', 'TEXT', {AUTHOR})
        chat.next_message('CHAR', 'MESSAGE')
        chat.new_chat('CHAR', 'CHAT_ID', 'CREATOR_ID')
        chat.get_histories('CHAR')
        chat.get_chat('CHAR')
        chat.get_history('CHAT_ID')
        chat.rate(RATE, 'CHAT_ID', 'TURN_ID', 'CANDIDATE_ID')
        chat.delete_message('CHAT_ID', 'TURN_ID')

        """
        def __init__(
            self, token: str,
            ws: websockets.WebSocketClientProtocol,
            session: Session
        ):
            self.token = token
            self.session = session
            self.ws = ws


        async def transl(text:str, target:str, source:str):
            translator = esgt(
            source_language=source,
            target_language=target)

            resoult = translator.translate(text)

            return resoult

        async def next_message(
            self, char: str, parent_msg_uuid: str,token:str = None
        ):
            setup = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session,token=token,method='GET',neo=True)
            chat_id = setup['chats'][0]['chat_id']
            await self.ws.send(json.dumps({
                'command': 'generate_turn_candidate',
                'payload': {
                    'character_id': char,
                    'turn_key': {
                        'turn_id': parent_msg_uuid,
                        'chat_id': chat_id
                    }
                }
            }))

            while True:
                response = json.loads(await self.ws.recv())
                try: response['turn']
                except: raise ServerError(response['comment'])

                if not response['turn']['author']['author_id'].isdigit():
                    try: is_final = response['turn']['candidates'][0]['is_final']
                    except: pass
                    else: return response

        async def create_img(
            self, char: str, chat_id: str, text: str,
            author_name:str, Return_img: bool = True, Return_all: bool = False, *, turn_id: str = None, candidate_id: str = None, token:str = None
        ):
            json_out = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session,token=token,method='GET',neo=True)
            chat_id = json_out['chats'][0]['chat_id']
            creator_id = json_out['chats'][0]['creator_id']

            if turn_id != None and candidate_id != None:
                message['update_primary_candidate'] = {
                    'candidate_id': candidate_id,
                    'turn_key': {
                        'turn_id': turn_id,
                        'chat_id': chat_id
                    }
                }

            message = {
                'command': 'create_and_generate_turn',
                'payload': {
                    'character_id': char,
                    'turn': {
                        'turn_key': {'chat_id': chat_id},
                        "author": {
                                "author_id": creator_id,
                                "is_human": True,
                                "name   ": author_name},
                        'candidates': [{'raw_content': text}]
                    }
                }
            }

            await self.ws.send(json.dumps(message))

            while True:
                response = json.loads(await self.ws.recv())
                try: response['turn']
                except: raise ServerError(response['comment'])

                if not response['turn']['author']['author_id'].isdigit():
                    try: is_final = response['turn']['candidates'][0]['is_final']
                    except: pass
                    else:
                        if Return_all:
                            r_in = response['turn']['candidates'][0]['raw_content']
                            img_in = response['turn']['candidates'][0]['tti_image_rel_path']  # Perhatikan perubahan indeks ke 0 di sini
                            results = f"{r_in}\n{img_in}"
                            return results
                        if Return_img:
                            r = response['turn']['candidates'][0]['tti_image_rel_path']
                            return r

        async def send_message(
            self, char: str,
            text: str, author_name:str,
            *, turn_id: str = None,token:str = None,
            candidate_id: str = None, Return_name: bool = False
        ):

            json_out = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session,token=token,method='GET',neo=True)
            chat_id = json_out['chats'][0]['chat_id']
            creator_id = json_out['chats'][0]['creator_id']

            message = {
                'command': 'create_and_generate_turn',
                'payload': {
                    'character_id': char,
                    'turn': {
                        'turn_key': {'chat_id': chat_id},
                         "author": {
                                "author_id": creator_id,
                                "is_human": True,
                                "name   ": author_name},
                        'candidates': [{'raw_content': text}]
                    }
                }
            }

            if turn_id != None and candidate_id != None:
                message['update_primary_candidate'] = {
                    'candidate_id': candidate_id,
                    'turn_key': {
                        'turn_id': turn_id,
                        'chat_id': chat_id
                    }
                }

            await self.ws.send(json.dumps(message))

            while True:
                response = json.loads(await self.ws.recv())
                try: response['turn']
                except: raise ServerError(response['comment'])

                if not response['turn']['author']['author_id'].isdigit():
                    try: is_final = response['turn']['candidates'][0]['is_final']
                    except: pass
                    else:
                        if Return_name:
                            r_in = response['turn']['candidates'][0]['raw_content']
                            n_in = response['turn']['author']["name"]
                            r = f"({n_in}) {r_in}"
                            return r
                        else:
                            r = response['turn']['candidates'][0]['raw_content']
                            return r






        async def delete_message(
            self, char: str, turn_ids: list,
            *, token: str = None, **kwargs
        ):
            json_out = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session, token=token, method='GET', neo=True)
            chat_id = json_out['chats'][0]['chat_id']
            payload = {
                'command':'remove_turns',
                'payload': {
                    'chat_id': chat_id,
                    'turn_ids': turn_ids
                }
            }
            await self.ws.send(json.dumps(payload))
            return json.loads(await self.ws.recv())

        async def get_avatar(self, char:str,*, token:str = None):
            json_out = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session, token=token, method='GET', neo=True)
            avatar_url = json_out["chats"][0]["character_avatar_uri"]
            full_link = f"https://characterai.io/i/80/static/avatars/{avatar_url}"
            return full_link


