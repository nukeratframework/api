import json
import requests
import urllib3
import api

urllib3.disable_warnings()


def main():
    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    response = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    )
    body = response.json()

    if body.get('status') == 'failure':
        print(json.dumps(body, indent=2))
        raise SystemExit(1)

    print(json.dumps({**body, 'access_token': '(hidden)'}, indent=2))


if __name__ == '__main__':
    main()
