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
    implant_task_tag = 't4sk8x1q'

    payload = [
        {
            'option': 'output',
            'type': 'terminal',
            'task_tag': implant_task_tag,
            'host': implant_host_tag,
            'output': 'demo output from implant/beacon_output.py\n',
        }
    ]

    body = build_implant_body(api.aes_key, payload)

    response = requests.post(
        api.implant_listener_url.rstrip('/') + '/',
        data=body,
        headers={'Content-Type': 'application/octet-stream'},
        timeout=60,
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
