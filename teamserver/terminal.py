import json
import uuid
from urllib.parse import quote

import requests
import urllib3
import api

urllib3.disable_warnings()


def print_terminal_response(response):
    content_type = (response.headers.get('Content-Type') or '').split(';')[0].strip().lower()
    if content_type == 'application/x-ndjson':
        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            text = str(line).strip()
            if text:
                print(text)
        return
    print(json.dumps(response.json(), indent=2))


def summarize_terminal_ndjson(response):
    events = []
    for line in response.iter_lines():
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({'status': 'chunk', 'binary_bytes': len(line)})
    return events


def main():
    host_tag = 'm1c15a'
    terminal_command = 'whoami'
    terminal_source_id = 'demo-terminal-1'

    user, password, secret = api.operator_key.split(':', 2)
    base = api.team_server_url.rstrip('/')

    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}
    source = terminal_source_id or f'demo-{uuid.uuid4().hex[:8]}'

    response = requests.post(
        f'{base}/api/terminal/',
        headers=headers,
        json={
            'command': terminal_command,
            'source_terminal': source,
            'host_tag': host_tag,
        },
        verify=False,
        timeout=120,
    )
    print_terminal_response(response)

    demo_file_upload = False
    if demo_file_upload:
        upload_meta = {
            'command': 'upload -f payload.exe -o C:/Temp/payload.exe',
            'host_tag': host_tag,
            'source_terminal': source,
        }
        upload_headers = {
            **headers,
            'x-terminal-meta': quote(json.dumps(upload_meta), safe=''),
        }
        upload_response = requests.post(
            f'{base}/api/terminal/',
            headers=upload_headers,
            data=b'MZ',
            verify=False,
            timeout=120,
        )
        print_terminal_response(upload_response)

    demo_download = False
    if demo_download:
        download_response = requests.post(
            f'{base}/api/terminal/',
            headers=headers,
            json={
                'command': 'download C:/Temp/sample.txt /tmp/sample.txt',
                'host_tag': host_tag,
                'source_terminal': source,
                'download_id': 'demo-download-1',
                'download_file': 'sample.txt',
            },
            verify=False,
            timeout=600,
            stream=True,
        )
        print(json.dumps(summarize_terminal_ndjson(download_response), indent=2))


if __name__ == '__main__':
    main()
