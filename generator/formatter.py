def indented(line: str, indent: int):
    return ' ' * indent + line


def formatted(file: str):
    lines = []
    indent = 0
    for line in file.split('\n'):
        line = line.strip()
        if line == '':
            continue
        if line.endswith('{'):
            line = indented(line, indent)
            indent = indent + 4
        elif line.endswith('}'):
            indent = indent - 4
            line = indented(line, indent)
        else:
            line = indented(line, indent)
        lines.append(line)
    return '\n'.join(lines)
