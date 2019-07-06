#!/usr/bin/env python3
from generator.certificates import get_certificates
from generator.config import Config
from generator.templates import server

if __name__ == '__main__':
    certificates = get_certificates()
    config = Config('config.json')
    for domain in config.domains:
        host = domain.host.replace('*', 'wildcard')
        with open(f'{host}.conf', 'w') as f:
            f.write(server(certificates, domain))
