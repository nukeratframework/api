import json
import requests
import urllib3
import api

urllib3.disable_warnings()


def main():
    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.post(f'{base}/api/aes/create', json={}, headers=headers, verify=False)
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
