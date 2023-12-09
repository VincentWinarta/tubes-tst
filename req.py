import requests, json

url = 'http://40.119.238.184/'


def get_token():
    token_url = url+'token'
    token_response = requests.post(token_url, data={'username': 'hilmi', 'password': 'secret'})
    token = token_response.json().get('access_token')
    return token

def get_reservations():
    headers = {'Authorization': f'Bearer {get_token()}'}
    reservations = requests.get(url+'reservations', headers=headers)
    return reservations.json()
