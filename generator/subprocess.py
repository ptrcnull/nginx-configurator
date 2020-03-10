import subprocess
from typing import List, Tuple


def run(cmdline: List[str]) -> Tuple[str, str]:
    result = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
