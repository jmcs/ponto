from subprocess import run, DEVNULL


def program_exists(program: str) -> bool:
    result = run(['which', program], stdout=DEVNULL)
    return result.returncode == 0