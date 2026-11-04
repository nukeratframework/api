import json
import requests
import urllib3
import api

urllib3.disable_warnings()

sample_script = (
    'def handler(ctx):\n'
    '    pass\n\n'
    'event.new_queue_line: handler()'
)


def main():
    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{base}/api/scripts/', headers=headers, verify=False)
    print(json.dumps(response.json(), indent=2))

    demo_mutate_script = False
    if demo_mutate_script:
        response = requests.post(
            f'{base}/api/scripts/',
            headers=headers,
            json={
                'name': 'Auto approve',
                'description': 'Approve safe commands',
                'content': sample_script,
            },
            verify=False,
        )
        created = response.json()
        print(json.dumps(created, indent=2))
        script_tag = (created.get('tag') or '').strip()
        if script_tag:
            response = requests.patch(
                f'{base}/api/scripts/{script_tag}',
                headers=headers,
                json={'status': 1},
                verify=False,
            )
            print(json.dumps(response.json(), indent=2))
            response = requests.delete(
                f'{base}/api/scripts/{script_tag}',
                headers=headers,
                json={'content': sample_script},
                verify=False,
            )
            print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
