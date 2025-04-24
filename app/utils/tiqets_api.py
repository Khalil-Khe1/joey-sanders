from app.utils.fetch import fetch

async def product(product_id: str, language: str = 'fr', currency: str = 'EUR'):
    headers = {
        'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
        'User-Agent': 'FastAPI/1.0',
        'Accept': 'application/json',
    }

    params = {
        'lang': language,
        'currency': currency
    }

    url = f'https://api.tiqets.com/v2/products/{product_id}'

    return await fetch(url, headers=headers, params=params)

async def products(
    language: str = 'fr', 
    currency: str = 'EUR', 
    page_size: int = 10, 
    page: int = 1, 
    query: str = ''):
    headers = {
        'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
        'User-Agent': 'FastAPI/1.0',
        'Accept': 'application/json',
    }

    params = {
        'lang': language,
        'currency': currency,
        'page_size': page_size,
        'page': page
    }
    
    if query != '':
        params['query'] = query

    url = f'https://api.tiqets.com/v2/products'

    return await fetch(url, headers=headers, params=params)

async def variants(product_id: str, language: str = 'fr', currency: str = 'EUR'):
    headers = {
        'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
        'User-Agent': 'FastAPI/1.0',
        'Accept': 'application/json',
    }

    params = {
        'lang': language,
        'currency': currency
    }

    url = f'https://api.tiqets.com/v2/products/{product_id}/product-variants'
    
    return await fetch(url, headers=headers, params=params)

async def availability(product_id: str, language: str = 'fr', currency: str = 'EUR'):
    headers = {
        'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
        'User-Agent': 'FastAPI/1.0',
        'Accept': 'application/json',
    }

    params = {
        'lang': language,
        'currency': currency
    }

    url = f'https://api.tiqets.com/v2/products/{product_id}/availability'

    return await fetch(url, headers=headers, params=params)