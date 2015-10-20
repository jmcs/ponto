from pathlib import Path
from subprocess import run
import re
import os
from .paths import HOME, BASE_DIR

SSH_REGEX = re.compile(r"^(?P<user>\w+?)@(?P<host>.*):(?P<owner>.*?)\/(?P<repo>.*?)\.git")
SSH_URL_REGEX = re.compile(r"^ssh://(?P<user>\w+?)@(?P<host>.*):(?P<port>.*?)\/(?P<owner>.*?)\/(?P<repo>.*?)\.git")


class InvalidRepo(Exception):
    def __init__(self, url):
        self.url = url


class GitRepository:
    def __init__(self, url):
        self.url = url
        match = SSH_REGEX.match(url) or SSH_URL_REGEX.match(url)
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
        local_repo = HOME / 'scm' / self.host / self.owner / self.repo
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


class ConfigRepo():
    def add(self, filename):
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'add', filename])
        os.chdir(str(cwd))

    def init(self):
        run(['git', 'init', str(BASE_DIR)])

    def clone(self, repo_url):
        run(['git', 'clone', repo_url, str(BASE_DIR)])
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'branch', '--set-upstream-to=origin/master', 'master'])
        os.chdir(str(cwd))

    def commit(self, message):
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'commit', '-m', message])
        os.chdir(str(cwd))

    def pull(self):
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'pull', '--ff'])
        os.chdir(str(cwd))

    def push(self):
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'push'])
        os.chdir(str(cwd))
