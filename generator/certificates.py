import os
import subprocess
import re
from .dataclasses import dataclass
from .subprocess import run
from typing import List, Tuple


@dataclass
class Certificate:
    regex = '''Certificate Name: (.*)
    Domains: (.*)
    Expiry Date: .*? \\((.*)\\)
    Certificate Path: (.*)
    Private Key Path: (.*)'''
    name: str
    domains: List[str]
    expiry_status: str
    certificate_path: str
    private_key_path: str

    def get_paths(self):
        if self.expiry_status.startswith('INVALID'):
            print(f'WARNING: certificate {self.name} is invalid! ({self.expiry_status})')
        return f'''
            ssl_certificate {self.certificate_path};
            ssl_certificate_key {self.private_key_path};
        '''


@dataclass
class Certificates:
    certificates: List[Certificate]

    def get_for_domain(self, domain: str) -> Certificate or None:
        wildcard = '.'.join(['*'] + domain.split('.')[1:])
        try:
            return next(filter(
                lambda cert: domain in cert.domains or wildcard in cert.domains,
                self.certificates
            ))
        except StopIteration:
            return None

    def has(self, domain: str) -> bool:
        return self.get_for_domain(domain) is not None


def get_certificates() -> Certificates:
    try:
        result = run(['certbot', 'certificates'])
        return Certificates(certificates=parse_certificates(result))
    except FileNotFoundError:
        print('Certbot was not found on your system.')
        print('You can install it using instructions from https://certbot.eff.org/')
        exit(1)


def parse_certificates(result: Tuple[str, str]):
    stdout, stderr = result
    if len(stdout) == 0:
        if '[Errno 13] Permission denied' in stderr:
            print('Insufficient permissions to run Certbot, elevating via sudo...')
            result = run(['sudo', 'certbot', 'certificates'])
            return parse_certificates(result)
        else:
            print('Error occured while getting certificates from certbot:')
            print(stderr)
            exit(1)
    else:
        result = list(
            map(
                lambda data: Certificate(
                    name=data[0],
                    domains=data[1].split(' '),
                    expiry_status=data[2],
                    certificate_path=data[3],
                    private_key_path=data[4],
                ),
                re.findall(Certificate.regex, stdout)
            )
        )
        return result


def issue_certificate(domain: str) -> Certificate or None:
    domain = re.sub(r'[^a-zA-Z0-9.]*', '', domain)
    print(f'Trying to issue a certificate for domain {domain}...')
    os.system(f'certbot certonly -d {domain}')
    new_certs = get_certificates()
    if new_certs.has(domain):
        return new_certs.get_for_domain(domain)
    return None
