#!/usr/bin/env python3
from configurator.certificates import get_certificates
from configurator.config import Config
from configurator.templates import server

if __name__ == '__main__':
    certificates = get_certificates()
    config = Config('config.json')
    print(config.domains)
    for domain in config.domains:
        with open('{}.conf'.format(domain.host.replace('*', 'wildcard')), 'w') as f:
            f.write(server(certificates, domain))
    # print(certificates.get_for_domain('bjorn.ml'))
    # print(get_certificates())
