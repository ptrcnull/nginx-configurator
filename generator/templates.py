from .certificates import Certificates
from .config import Domain
from .formatter import formatted
from .handlers import handle


def cache_template(name: str):
    return f'proxy_cache_path /var/nginx/cache levels=1:2 keys_zone={name}:10m inactive=48h max_size=1g;'


def cache(domain: Domain) -> str:
    handlers = domain.find_handlers('cache')
    return '\n'.join(map(
        lambda handler: cache_template(handler.options),
        handlers
    )) if len(handlers) != 0 else ''


def static(domain: Domain) -> str:
    stat_handlers = domain.find_handlers('stat') + domain.find_handlers('webdav') + domain.find_handlers('index')
    fpm_handlers = domain.find_handlers('fpm')
    if len(stat_handlers) != 0:
        return f'''
            root /var/www/{domain.host.replace('*', 'wildcard')};
            index index.html index.htm{' index.php' if len(fpm_handlers) != 0 else ''};
        '''
    else:
        return ''


def locations(domain: Domain) -> str:
    return '\n'.join(map(
        lambda location: f'''
            location {location.path} {{
            {''.join(map(handle, location.handlers))}
            }}
        ''',
        domain.locations
    ))


def server(certificates: Certificates, domain: Domain) -> str:
    log_host = domain.host.replace('*', 'wildcard')
    rendered = f'''
        {cache(domain)}

        server {{
            listen 443 ssl http2;
            listen [::]:443 ssl http2;

            access_log /var/log/nginx/access/{log_host}.log vcombined;
            error_log /var/log/nginx/error/{log_host}.log;

            {certificates.get_for_domain(domain.host).get_paths()}

            server_name {domain.host};
            {static(domain)}
            {locations(domain)}

            include _error.conf;
        }}
    '''
    return formatted(rendered)


def server_http(domain: Domain) -> str:
    log_host = domain.host.replace('*', 'wildcard')
    rendered = f'''
        {cache(domain)}

        server {{
            listen 80;
            listen [::]:80;

            access_log /var/log/nginx/access/{log_host}.log vcombined;
            error_log /var/log/nginx/error/{log_host}.log;

            server_name {domain.host};
            {static(domain)}
            {locations(domain)}

            include _error.conf;
        }}
    '''
    return formatted(rendered)

