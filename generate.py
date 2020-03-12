#!/usr/bin/env python3
import os
from os import path, system, makedirs
import sys

from generator.certificates import get_certificates, issue_certificate
from generator.config import Config
from generator.subprocess import run
from generator.templates import server, server_http
import argparse


def generate(args):
    makedirs(args.out, exist_ok=True)

    certificates = get_certificates()
    config = Config('config.json')
    for domain in config.domains:
        host = domain.host.replace('*', 'wildcard')

        output = ''

        if host.startswith('http:'):
            domain.host = domain.host[5:]
            host = host[5:]
            output = server_http(domain)
        else:
            if certificates.has(domain.host):
                output = server(certificates, domain)
            else:
                print(f'Certificate not found for {domain.host}!')
                cert = issue_certificate(domain.host)
                if cert is not None:
                    print(f'Failed to issue certificate for {domain.host}!')
                    output = server(certificates, domain)
                else:
                    output = server_http(domain)

        with open(path.join(args.out, f'{host}.conf'), 'w') as f:
            f.write(output)


if __name__ == '__main__':
    workdir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(description='Generate Nginx configuration.')
    parser.add_argument('-o', '--out', default='./nginx', metavar='path',
                        help='Output directory (default: current directory)')
    parser.add_argument('--no-update', action='store_true',
                        help='Don\'t update Git repository')
    _args = parser.parse_args()

    if not _args.no_update:
        system('git pull')
        path = os.path.realpath(__file__)
        system(f'{sys.executable} {path} -o {_args.out} --no-update')
    else:
        generate(_args)
        stdout, stderr = run(['docker-compose', 'ps'])
        if 'nginx' in stdout and 'Up' in stdout:
            system('docker-compose kill -s SIGHUP nginx')
        else:
            system('docker-compose up -d')

    os.chdir(workdir)

