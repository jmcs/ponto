from pathlib import Path
from subprocess import run
import os

from .paths import HOME, DRIVE_DIR


class Drive:

    def init(self, account, local_name, drive_name):
        account_dir = DRIVE_DIR / account
        origin_path = account_dir / drive_name
        if not origin_path.exists():
            origin_path.mkdir(parents = True)
            # TODO context manager
            cwd = Path.cwd()
            os.chdir(str(origin_path))
            try:
                run(['drive', 'init'])
                run(['drive', 'pull', drive_name], input=b'y\n')
            except FileNotFoundError:
                print("Drive not installed")
                return
            finally:
                os.chdir(str(cwd))

        link_path = HOME / Path(local_name)
        target_path = origin_path / drive_name
        try:
            link_path.symlink_to(target_path)
        except FileExistsError:
            print("Link already exists")