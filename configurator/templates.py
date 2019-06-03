from typing import List

from configurator.certificates import Certificates
from configurator.config import Domain
from configurator.formatter import formatted

cache_template = 'proxy_cache_path /var/nginx/cache levels=1:2 keys_zone=${name}:10m inactive=48h max_size=1g;'


def cache(domain: Domain):
    handlers = domain.find_handlers('cache')
    return '\n'.join(map(
        lambda handler: cache_template.format(name=handler.options),
        handlers
    )) if len(handlers) != 0 else ''


def static(domain: Domain):
    handlers = domain.find_handlers('cache')
    if handlers != 0:
        return '''
            root /var/www/{};
            index index.html index.htm;
        '''.format(domain.host.replace('*', 'wildcard'))


def locations(domain: Domain):
    return ''


def server(certificates: Certificates, domain: Domain):
    rendered = '''
        {cache}
        
        server {{
            listen 443 ssl http2;
            listen [::]:443 ssl http2;
            
            {ssl}
            
            server_name {host};
            {static}
            {locations}
        }}
    '''.format(
        cache=cache(domain),
        ssl=certificates.get_for_domain(domain.host).get_paths(),
        host=domain.host,
        static=static(domain),
        locations=locations(domain)
    )
    return formatted(rendered)
