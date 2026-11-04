import json
import requests
import urllib3
import api

urllib3.disable_warnings()

minimal_stageless = {
    'type': 'build',
    'implant_base': 'stageless',
    'config': {
        'operational_system': 'windows',
        'cpu': 'amd',
        'arch': 'x64',
        'format': 'exe',
        'protocol': 'http',
        'servers': {'0': '127.0.0.1:8080'},
    },
}


def main():
    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.post(
        f'{base}/api/implants/',
        headers=headers,
        json=minimal_stageless,
        verify=False,
        timeout=600,
    )
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
