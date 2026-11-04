import json
import requests
import urllib3
import api

urllib3.disable_warnings()


def main():
    host_tag = 'm1c15a'

    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{base}/api/reports/', headers=headers, verify=False)
    print(json.dumps(response.json(), indent=2))

    demo_create_report = False
    if demo_create_report:
        response = requests.post(
            f'{base}/api/reports/',
            headers=headers,
            json={
                'name': 'Engagement Summary',
                'description': 'API demo report',
                'reportType': 'activity',
                'fileType': 'pdf',
                'hostTags': [host_tag],
                'hideCredentials': False,
            },
            verify=False,
            timeout=600,
        )
        created = response.json()
        print(json.dumps(created, indent=2))
        report_tag = (created.get('tag') or (created.get('report') or {}).get('tag') or '').strip()
        if report_tag:
            view = requests.get(
                f'{base}/api/reports/{report_tag}/view',
                headers=headers,
                verify=False,
            )
            print(json.dumps(view.json(), indent=2))


if __name__ == '__main__':
    main()
