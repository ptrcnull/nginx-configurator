from .config import Handler


def target(port: str) -> str:
    return port if ':' in port else f'http://127.0.0.1:{port}'


def handle(handler: Handler) -> str:
    options = handler.options
    if handler.name == 'stat':
        root = f'root /var/www/{options};' if options != '' else ''
        return f'''
            {root}
            try_files $uri $uri/ =403;
        '''
    if handler.name == 'index':
        root = f'root /var/www/{options};' if options != '' else ''
        return f'''
            {root}
            try_files $uri $uri/ =403;
            
            autoindex on;
            autoindex_exact_size off;
            charset utf-8;
        '''
    if handler.name == 'angular':
        root = f'root /var/www/{options};' if options != '' else ''
        return f'''
            {root}
            try_files $uri $uri/ /index.html =403;
        '''
    if handler.name == 'webdav':
        root = f'root /var/www/{options};' if options != '' else ''
        return f'''
            {root}
            dav_methods PUT DELETE MKCOL COPY MOVE;
            dav_ext_methods PROPFIND OPTIONS;
            create_full_put_path on;
            dav_access user:rw group:rw all:r;
            autoindex on;
            allow all;
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
    if handler.name == 'fpm':
        host = options if ':' in options else f'127.0.0.1:{options}'
        # https://www.pascallandau.com/blog/php-php-fpm-and-nginx-on-docker-in-windows-10/
        return f'''
            }}

            location ~ [^/]\\.php(/|$) {{
                fastcgi_split_path_info ^(.+?\\.php)(/.*)$;
                if (!-f $document_root$fastcgi_script_name) {{
                    return 404;
                }}
        
                include fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                fastcgi_param PATH_INFO       $fastcgi_path_info;
                fastcgi_param PATH_TRANSLATED $document_root$fastcgi_path_info;
            
                fastcgi_pass   {host};
                fastcgi_index  index.php;
      '''
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
    if handler.name == 'custom':
        with open(options) as file:
            return file.read()
    return f'# {handler.name} {handler.options}'
