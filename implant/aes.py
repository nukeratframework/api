import base64
import json
import os
import re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

aes_nonce_size = 12
aes_tag_size = 16
aes_probe_plain_len = 9
aes_probe_wire_len = aes_nonce_size + aes_probe_plain_len + aes_tag_size


def encrypt_bytes(key_b64, data):
    raw_key = base64.b64decode(key_b64)
    nonce = os.urandom(aes_nonce_size)
    return nonce + AESGCM(raw_key).encrypt(nonce, data, None)


def build_implant_body(key_b64, payload):
    probe_plain = os.urandom(aes_probe_plain_len)
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode()
    return encrypt_bytes(key_b64, probe_plain) + encrypt_bytes(key_b64, payload_bytes)


def decrypt_bytes(key_b64, blob):
    if len(blob) < aes_nonce_size + aes_tag_size:
        return None

    raw_key = base64.b64decode(key_b64)

    try:
        return AESGCM(raw_key).decrypt(blob[:aes_nonce_size], blob[aes_nonce_size:], None)
    except Exception:
        return None


def extract_listener_content(raw, template=''):
    template = (template or '').strip()
    if not template or template == '§content§':
        return raw
    parts = template.split('§content§')
    pattern = b''
    for i, part in enumerate(parts):
        pattern += re.escape(part.encode('utf-8'))
        if i < len(parts) - 1:
            pattern += b'(.+?)'
    match = re.compile(pattern, re.DOTALL).search(raw)
    if not match:
        return None
    return match.group(1)


def decrypt_listener_json(key_b64, raw, template=''):
    blob = extract_listener_content(raw, template)
    if blob is None:
        return None
    plain = decrypt_bytes(key_b64, blob)
    if not plain:
        return None
    try:
        return json.loads(plain.decode())
    except Exception:
        return None


def main():
    import api

    if not api.aes_key:
        return

    sample = {'option': 'input', 'host': 'demo', 'metadata': {}}
    body = build_implant_body(api.aes_key, sample)

    print(
        json.dumps(
            {
                'total': len(body),
                'probe_wire_len': aes_probe_wire_len,
                'payload_cipher_len': len(body) - aes_probe_wire_len,
            },
            indent=2,
        )
    )


if __name__ == '__main__':
    main()
