from clickclick import info
import click

from .configuration import open_configuration, save_configuration
from .paths import BASE_DIR, CONFIG_PATH
from .scm import GitRepository

cli = click.Group()


@cli.command('add-repo')
@click.argument('scm_url')
def add_repo(scm_url):
    config = open_configuration()
    repo = GitRepository(scm_url)
    repo.clone()
    config['scm'].add(scm_url)
    save_configuration(config)


@cli.command('clone')
# @click.argument("git_url")
def clone():
    # TODO clone git url

    config = open_configuration()
    scm_urls = config.get('scm', [])  # type: List[str]
    for url in scm_urls:
        repository = GitRepository(url)
        info('Cloning {repo}'.format(repo=repository))
        repository.clone()


@cli.command('init')
def init():

    # TODO receive remote and push

    info("Creating directory structure")
    if not BASE_DIR.exists():
        BASE_DIR.mkdir()

    info("Creating config files")
    if not CONFIG_PATH.exists():
        empty_config = {'scm': set()}
        save_configuration(empty_config)


cli()
