from pathlib import Path

BASE_DIR = Path.home() / '.ponto'  # type: Path
CONFIG_PATH = BASE_DIR / 'ponto.yaml'
DRIVE_DIR = BASE_DIR / 'drive'
HOME_PATH = BASE_DIR / 'home'  # path to store dotfiles

def relative_to_home(path) -> Path:
    path = Path(path).absolute()
    if Path.home() in path.parents:
        path = '~' / path.relative_to(Path.home())
    return path
