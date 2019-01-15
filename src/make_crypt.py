#!/usr/bin/python 

import os
import json
import my_crypto as mc


def encrypt(path):
    ret_val = -1
    if os.path.exists(path):
        with open(path, 'r') as fp:
            in_dict = json.load(fp)
        if in_dict:
            crypt_path = '{}.crypt'.format(os.path.splitext(path)[0])
            mc.encrypt_to_file(crypt_path, in_dict)
        if os.path.exists(crypt_path):
            ret_val = 0
    return ret_val

if __name__ == '__main__':
    in_file = 'envs.json'
    encrypt(in_file)


