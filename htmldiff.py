#!/usr/bin/env python3
import re
import subprocess
import sys
import tempfile
import urllib.request

import yaml
from bs4 import BeautifulSoup


def init() -> None:
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    with open('basic_auth.yaml') as f:
        for auth in yaml.load(f):
            password_mgr.add_password(**auth)

    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)


def read_doc(url_or_path: str) -> str:
    try:
        f = urllib.request.urlopen(url_or_path)
    except ValueError:
        f = open(url_or_path)

    soup = BeautifulSoup(f.read(), 'html5lib')

    # Ignore insignificant whitespace differences
    for e in soup.descendants:
        if e.string and e.string.parent is e:
            e.string = re.sub(r'\s\s+', ' ', e.string)

    return soup.prettify()


def main() -> None:
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
