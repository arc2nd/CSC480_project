#!/usr/bin/env python

import os
import copy
import base64
import json
from cryptography.fernet import Fernet

def paddit(in_str):
    out_str = copy.copy(in_str)
    if len(in_str) < 32:
        delta = 32 - len(in_str)
        out_str += '7' * delta
    elif len(in_str) > 32:
        out_str = in_str[:32]
    return out_str

def rebase(in_str):
    return base64.urlsafe_b64encode(in_str)

def encrypt(key, msg):
    processed_key = rebase(paddit(key))
    cipher = Fernet(processed_key)
    return cipher.encrypt(msg)

def decrypt(key, ciphertext):
    processed_key = rebase(paddit(key))
    cipher = Fernet(processed_key)
    return cipher.decrypt(ciphertext)


def encrypt_to_file(path, in_dict):
    msg_str = json.dumps(in_dict)
    cipher_str = encrypt(os.path.basename(path), msg_str)
    with open(path, 'w') as fp:
        fp.write(cipher_str)

def decrypt_from_file(path):
    contents = None
    if os.path.exists(path):
        with open(path, 'r') as fp:
            contents = fp.read()
        if contents:
            msg = decrypt(os.path.basename(path), contents)
        if msg:
            return json.loads(msg)



