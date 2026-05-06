from dotenv import load_dotenv

import requests
import os

load_dotenv()

def verify_recaptcha(token: str) -> bool:
    secret=os.getenv('RECAPTCHA_SECRET_KEY')
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        'secret': secret,
        'response': token
    })
    result = response.json()
    return result.get('success', False)