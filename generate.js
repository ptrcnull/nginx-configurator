const fs = require('fs')
const { spawn } = require('child_process')

const localhost = port => `http://172.16.64.1:${port}`

const handlers = {
  stat: dir => `
    ${dir ? `root /var/www/${dir};` : ''}
    try_files $uri $uri/ =403;
  `,
  proxy: port => `
    proxy_pass ${port.includes(':') ? port : localhost(port)};
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-NginX-Proxy true;
  `,
  nohostproxy: port => `proxy_pass ${port.includes(':') ? port : localhost(port)};`,
  cache: name => `
    expires 30d;
    add_header Pragma public;
    add_header Cache-Control "public";

    proxy_buffering on;
    proxy_cache /etc/nginx/cache/${name};
    proxy_cache_valid 200 1d;
    proxy_cache_use_stale error timeout invalid_header updating http_500 http_502 http_503 http_504;
  `,
  wsproxy: port => `
      try_files /nonexistent @$type;
    }

    location @ws {
      proxy_pass ${port.includes(':') ? port : localhost(port)};
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
    }

    location @web {
      proxy_pass ${port.includes(':') ? port : localhost(port)};
  `,
  redirect: url => `return 301 ${url};`,
  auth: file => `
    auth_basic "Authorization required";
    auth_basic_user_file /etc/nginx/auth/${file}; 
  `
}

const location = (path, data) => `
  location ${path} {
    ${data.map(handle).join('\n')}
  }
`

const handle = ([ type, data ]) => handlers[type](data).trim()

function generateLocations (locations) {
  if (typeof locations === 'string') return parseLocation([ '/', locations ])
  return Object.entries(locations)
    .map(parseLocation)
    .filter(e => e)
    .join('\n')
    .replace('\n\n', '\n')
}

function parseLocation ([ path, loc ]) {
  const options = loc.split(';').map(el => el.trim().split(' '))
  return location(path, options)
}

const hasStaticLocation = locations => typeof locations === 'string' ?
  locations.includes('stat') :
  Object.values(locations).some(location => location.includes('stat'))

const getCacheLocations = locations => (typeof locations === 'string' ?
  [ locations.match('cache (.*)') ] :
  Object.values(locations).map(location => location.includes('cache (.*)')))
  .filter(match => match && match[1])
  .map(match => match[1])

const config = JSON.parse(fs.readFileSync('config.json', 'utf8'))

async function main () {
  const certs = await getCertificates()
  const ssl = getCertPaths(certs)
  Object.entries(config).forEach(([host, locations]) => {
    if (host.startsWith('_')) return
    fs.writeFileSync(`${host.replace('*', 'wildcard')}.conf`, `
${getCacheLocations(locations).map(name => `proxy_cache_path /var/nginx/cache levels=1:2 keys_zone=${name}:10m inactive=48h max_size=1g;\n`)}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  
  ${ssl(host)}

  server_name ${host};
  ${hasStaticLocation(locations)
      ? `root /var/www/${host.replace('*', 'wildcard')};
  index index.html index.htm index.nginx-debian.html;`
      : ''}
  ${generateLocations(locations)}
}

`.trim(), 'utf8')
  })
}
main()

function getCertPaths (certs) {
  return domain => {
    const wildcard = [ '*', ...domain.split('.').slice(1) ].join('.')
    const cert = certs.find(cert => cert.domains.includes(domain) || cert.domains.includes(wildcard))
    if (!cert) {
      console.log(`Certificate not found for domain ${domain}!`)
      process.exit(1)
    }
    if (cert.expiryStatus.startsWith('INVALID')) console.log(`WARNING: certificate ${cert.name} is invalid! (${cert.expiryStatus})`)
    return `
    ssl_certificate ${cert.certPath};
    ssl_certificate_key ${cert.keyPath};
  `.trim()
  }
}

async function getCertificates () {
  const { stdout: certificates } = await exec('sudo certbot certificates')
  const certificateTemplate = `
  Certificate Name: (.*)
    Domains: (.*)
    Expiry Date: .*? \\((.*)\\)
    Certificate Path: (.*)
    Private Key Path: (.*)`
  return certificates.match(new RegExp(certificateTemplate, 'g'))
    .map(cert => cert.match(new RegExp(certificateTemplate)))
    .map(([ , name, domains, expiryStatus, certPath, keyPath ]) => ({
      name,
      domains: domains.split(' '),
      expiryStatus,
      certPath,
      keyPath
    }))
}

function exec (command) {
  return new Promise(resolve => {
    const child = spawn('/bin/bash', ['-c', command], { cwd: require('path').join(__dirname, '..'), env: process.env })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', data => { stdout += data })
    child.stderr.on('data', data => { stderr += data })
    child.on('error', err => {
      console.error(err)
      process.exit(1)
    })
    child.on('close', () => resolve({ stderr, stdout }))
  })
}
