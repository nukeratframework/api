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

    response = requests.get(
        f'{base}/api/iocs/',
        headers=headers,
        params={'search': 'sha256', 'hostTags': ['600d4'], 'page': 1, 'pageSize': 50},
        verify=False,
    )
    print(json.dumps(response.json(), indent=2))

    ioc_tag = '6wjMov'
    response = requests.delete(
        f'{base}/api/iocs/{ioc_tag}',
        headers=headers,
        verify=False,
    )
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
