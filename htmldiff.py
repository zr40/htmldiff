#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from urllib.error import URLError

import yaml
from bs4 import BeautifulSoup


def init() -> None:
    basic_auth_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic_auth.yaml')

    if os.path.exists(basic_auth_path):
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        with open(basic_auth_path) as f:
            for auth in yaml.load(f):
                password_mgr.add_password(**auth)

        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)


def read_doc(url_or_path: str) -> str:
    try:
        f = urllib.request.urlopen(url_or_path)
    except URLError as e:
        print('Could not open "{}": {}'.format(url_or_path, e.reason))
        exit(1)
    except ValueError:
        try:
            f = open(url_or_path)
        except FileNotFoundError as e:
            print('Could not open "{}": {}'.format(url_or_path, e.args[1]))
            exit(1)

    soup = BeautifulSoup(f.read(), 'html5lib')

    # Ignore insignificant whitespace differences
    for e in soup.descendants:
        if e.string and e.string.parent is e:
            e.string = re.sub(r'\s\s+', ' ', e.string)

    return soup.prettify()


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: {} [url-or-path] [url-or-path]".format(sys.argv[0]))
        exit(1)

    init()

    doc_a = read_doc(sys.argv[1])
    doc_b = read_doc(sys.argv[2])

    with tempfile.NamedTemporaryFile(mode='w') as file_a, tempfile.NamedTemporaryFile(mode='w') as file_b:
        file_a.write(doc_a)
        file_a.flush()
        file_b.write(doc_b)
        file_b.flush()

        subprocess.call(['git', 'diff', file_a.name, file_b.name])


if __name__ == '__main__':
    main()
