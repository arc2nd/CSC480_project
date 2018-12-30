#!/usr/bin/python 

import os
import json
import subprocess


def encrypt(path):
    crypt_path = '{}.crypt'.format(os.path.splitext(path)[0])
    cmd = 'openssl des3 -salt -e -in {} -pass pass:{} -out {}'.format(path, crypt_path, crypt_path)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    if os.path.exists(crypt_path):
        return 0

if __name__ == '__main__':
    in_file = 'envs.json'
    encrypt(in_file)


