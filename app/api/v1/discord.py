from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import httpx

from app.config import settings
from app.database import get_db

from sqlalchemy.orm import Session

from collections import namedtuple

router = APIRouter()
client = httpx.AsyncClient()

@router.get('/messages')
async def get_messages(token : str, channel : str):
    conversation = []
    response = ['s']
    last_msg_id = ''

    while len(response) != 0:
        headers = {
            'Authorization': token,
            'User-Agent': 'FastAPI/1.0',
            'Accept': 'application/json',
        }

        query_params = {}

        response = await client.get(
            f'https://discord.com/api/channels/{channel}/messages', 
            headers=headers, 
            params=query_params
        )
        response.raise_for_status()
        response = response.json()

        for message in response:
            author = message['author']['global_name']
            content = 'image' if message['content'] == '' else message['content']
            conversation.append({
                'id': message['id'],
                'content': f"{author}: {content}"
            })
    
    return list(reversed(conversation))