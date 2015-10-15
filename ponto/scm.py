from pathlib import Path
from subprocess import run
import re

SSH_REGEX = re.compile(r"git@(?P<host>.*):(?P<owner>.*?)\/(?P<repo>.*?)\.git")

class InvalidRepo(Exception):

    def __init__(self, url):
        self.url = url

class GitRepository:

    def __init__(self, url):
        self.url = url
        match = SSH_REGEX.match(url)
        if not match:
            raise InvalidRepo(url)
        self.host = match.group('host')  # type: str
        self.owner = match.group('owner')  # type: str
        self.repo = match.group('repo')  # type: str
        # TODO https

    def __str__(self):
        return '{host}/{owner}/{repo}'.format_map(vars(self))

    @property
    def local_path(self) -> Path:
        local_repo = Path.home() / 'scm' / self.host / self.owner / self.repo
        return local_repo

    def clone(self):
        try:
            self.local_path.mkdir(parents=True)
        except FileExistsError:
            pass
        git_folder = self.local_path / '.git'
        if not git_folder.exists():
            run(['git', 'clone', self.url, str(self.local_path)])
        else:
            print('Git repository {repo} already exists'.format(repo=self))
