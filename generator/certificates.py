import subprocess
import re
from .dataclasses import dataclass
from typing import List


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

    def get_for_domain(self, domain: str) -> Certificate:
        wildcard = '.'.join(['*'] + domain.split('.')[1:])
        return next(filter(
            lambda cert: domain in cert.domains or wildcard in cert.domains,
            self.certificates
        ))


def get_certificates() -> Certificates:
    try:
        result = subprocess.run(['certbot', 'certificates'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return Certificates(certificates=parse_certificates(result))
    except FileNotFoundError:
        print('Certbot was not found on your system.')
        print('You can install it using instructions from https://certbot.eff.org/')
        exit(1)


def parse_certificates(result: subprocess.CompletedProcess):
    stdout = result.stdout.decode('utf-8')
    stderr = result.stderr.decode('utf-8')
    if len(stdout) == 0:
        if '[Errno 13] Permission denied' in stderr:
            print('Insufficient permissions to run Certbot, elevating via sudo...')
            result = subprocess.run(['sudo', 'certbot', 'certificates'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
