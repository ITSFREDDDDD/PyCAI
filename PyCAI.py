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

# ███████             ██████      ██     ██  ████
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
# CODE  BY @ITSFRED9999 (https://github.com/fred)
# When making a pull request, please put your information here
# =============================================================
# Need support? Open a discord ticket at (discord: tokaifalco_)
# =============================================================

__all__ = ['PyCAI', 'PySyncCAI']

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

class PySynCAI:
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
    # was there a constructor here?
    
    # I'm pretty sure this was the chat constructor but should double check. This constructor likely needs to be present in the new classes I created.
    def __init__(
      self, token: str,
      ws: websockets.WebSocketClientProtocol,
      session: Session
      ):
      self.token = token
      self.session = session
      self.ws = ws
    async def get_history(self, char: str, *, token: str = None):
      json_out = await PyAsyncCAI2.request(f'chats/recent/{char}', self.session, token=token, method='GET', neo=True)
      chat_id = json_out['chats'][0]['chat_id']
      r = await PyAsyncCAI2.request(f'turns/{chat_id}/', self.session, token=token, neo=True)
      turn_out = [{"turn_id": turn['turn_key']['turn_id'], "raw_content": turn['candidates'][0]['raw_content']} for turn in r['turns']]
      output = [f'["{turn["turn_id"]}", "{turn["raw_content"]}"]' for turn in turn_out]
      return output
     # Gets a specific history from histories json object or from the chat object
     #default gets the next chat in sequence, if defined takes number parameter. Not yet defined
     #creates a new chat. might only be in v1
     # pulls the chat
  class message:
    
    # I'm pretty sure this was the chat constructor but should double check. This constructor likely needs to be present in the new classes I created.
    def __init__(
      self, token: str,
      ws: websockets.WebSocketClientProtocol,
      session: Session
      ):
      self.token = token
      self.session = session
      self.ws = ws # same constructor as chat
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
    
    
    
    
                                
     # these are indented
     # these are indented
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
                        else: return response #R# default gets the next message in sequence, if defined takes number parameter 
     # Assigns message value
     # needs to be in another program, not cai specific
  class imagen:
    
    # I'm pretty sure this was the chat constructor but should double check. This constructor likely needs to be present in the new classes I created.
    def __init__(
      self, token: str,
      ws: websockets.WebSocketClientProtocol,
      session: Session
      ):
      self.token = token
      self.session = session
      self.ws = ws # same constructor as chat
    async def generate(
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

    async def request(
        url: str, session: Session,
        *, token: str = None, method: str = 'GET',
        data: dict = None, split: bool = False,
        split2: bool = False, neo: bool = False
    ):

        if neo:
            link = f'https://neo.character.ai/{url}'
        else:
            link = f'{session.url}{url}'

        if token == None:
            key = session.token
        else:
            key = token

        headers = {
            'Authorization': f'Token {key}',
        }

        if method == 'GET':
            response = session.get(
                link, headers=headers
            )

        elif method == 'POST':
            response = session.post(
                link, headers=headers, json=data
            )

        elif method == 'PUT':
            response = session.put(
                link, headers=headers, json=data
            )
            
        if split:
            data = json.loads(response.text.split('\n')[-2])
        elif split2:
            lines = response.text.strip().split('\n')
            data = [json.loads(line) for line in lines if line.strip()] # List
        else:
            data = response.json()

        if str(data).startswith("{'command': 'neo_error'"):
            raise ServerError(data['comment'])
        elif str(data).startswith("{'detail': 'Auth"):
            raise AuthError('Invalid token')
        elif str(data).startswith("{'status': 'Error"):
            raise ServerError(data['status'])
        elif str(data).startswith("{'error'"):
            raise ServerError(data['error'])
        else:
            return data
