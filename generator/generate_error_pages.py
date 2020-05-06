from http import HTTPStatus
from pathlib import Path


def generate_error_pages():
    from .subprocess import run
    hostname = run(['hostname'])[0]

    if Path('../html/400.html').exists():
        return

    with open('../html/template.html') as tmpl:
        tmpllines = tmpl.readlines()
        for status in HTTPStatus:
            code = status.value
            desc = status.phrase

            if code < 400:
                continue

            def replace(line: str) -> str:
                return (line
                        .replace('{{ title }}', f'{code} {desc}')
                        .replace('{{ code }}', str(code))
                        .replace('{{ description }}', desc)
                        .replace('{{ server }}', hostname))

            with open(f'../html/{code}.html', 'w') as out:
                out.writelines(map(replace, tmpllines))


if __name__ == '__main__':
    generate_error_pages()
