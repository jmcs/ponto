from pathlib import Path
from os.path import expanduser

HOME = Path(expanduser("~"))
BASE_DIR = HOME / '.ponto'  # type: Path
CONFIG_PATH = BASE_DIR / 'ponto.yaml'
DRIVE_DIR = BASE_DIR / 'drive'
DOTFILES_PATH = BASE_DIR / 'home'  # path to store dotfiles

def relative_to_home(path) -> Path:
    path = Path(path).absolute()
    if HOME in path.parents:
        path = '~' / path.relative_to(Path.home())
    return path
