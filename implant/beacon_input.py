import json
import requests
import urllib3
import api
from implant.aes import build_implant_body, decrypt_listener_json

urllib3.disable_warnings()


def main():
    if not api.implant_listener_url or not api.aes_key:
        return

    implant_host_tag = 'demo01'

    payload = {
        'option': 'input',
        'host': implant_host_tag,
        'metadata': {
            'relays': [],
            'privilege': 'default',
            'internal_ip': '192.168.15.21',
            'host': '192.168.15.21',
            'port': '9090',
        },
    }

    body = build_implant_body(api.aes_key, payload)

    response = requests.post(
        api.implant_listener_url.rstrip('/') + '/',
        data=body,
        headers={'Content-Type': 'application/octet-stream'},
        timeout=120,
        verify=False,
    )

    print(response.status_code, len(response.content))

    if response.content:
        parsed = decrypt_listener_json(
            api.aes_key,
            response.content,
            api.listener_response_template,
        )
        if parsed is not None:
            print(json.dumps(parsed, indent=2))
            return

    print(response.text[:500])


if __name__ == '__main__':
    main()
