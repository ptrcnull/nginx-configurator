#!/usr/bin/env python3
import os
from os import path

from generator.certificates import get_certificates
from generator.config import Config
from generator.templates import server
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Nginx configuration.')
    parser.add_argument('-o', '--out', default='.', metavar='path',
                        help='Output directory (default: current directory)')
    args = parser.parse_args()
    # print(args)

    os.makedirs(args.out, exist_ok=True)

    certificates = get_certificates()
    config = Config('config.json')
    for domain in config.domains:
        host = domain.host.replace('*', 'wildcard')

        try:
            certificates.get_for_domain(domain.host)
        except StopIteration:
            print(f'Certificate not found for {domain.host}!')
            continue

        with open(path.join(args.out, f'{host}.conf'), 'w') as f:
            f.write(server(certificates, domain))
