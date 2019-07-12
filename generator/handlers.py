from .config import Handler


def target(port: str) -> str:
    return port if ':' in port else f'http://172.16.64.1:{port}'


def handle(handler: Handler) -> str:
    options = handler.options
    if handler.name == 'stat':
        root = f'root /var/www/{options};' if options != '' else ''
        return f'''
            {root}
            try_files $uri $uri/ =403;
        '''
    if handler.name == 'proxy':
        return f'''
            proxy_pass {target(options)};
            proxy_http_version 1.1;

            # WebSocket-specific
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-NginX-Proxy true;
        '''
    if handler.name == 'nohostproxy':
        return f'proxy_pass {target(options)};'
    if handler.name == 'cache':
        return f'''
            expires 30d;
            add_header Pragma public;
            add_header Cache-Control "public";

            proxy_buffering on;
            proxy_cache {options};
            proxy_cache_valid 200 1d;
            proxy_cache_use_stale error timeout invalid_header updating http_500 http_502 http_503 http_504;
        '''
    if handler.name == 'origin-http':
        return 'proxy_set_header Origin http://$host;'
    if handler.name == 'redirect':
        return f'return 301 {options};'
    if handler.name == 'auth':
        return f'''
            auth_basic "Authorization required";
            auth_basic_user_file /etc/nginx/auth/{options};
        '''
    return f'# {handler.name} {handler.options}'
