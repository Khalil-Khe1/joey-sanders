import httpx

client = httpx.AsyncClient()

async def fetch(url: str, headers: dict, body:dict = {}, params: dict = {}, method:str ='GET'):
    for attempt in range(5):
        try:
            response = None
            if method == 'GET':
                response = await client.get(url, headers=headers, params=params, timeout=10.0)
            elif method == 'POST':
                response = await client.post(url, headers=headers, body=body, params=params, timeout=10.0)
            response.raise_for_status()
            response = response.json()
            return response
        except httpx.HTTPStatusError as e:
            return {'Error': f'{e.response.status_code} - {e.response.text}'}
        except httpx.TimeoutException as e:
            print('Timeout, trying again...')
    return None