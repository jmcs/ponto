from clickclick import info
from pathlib import Path
import click

from .configuration import open_configuration, save_configuration
from .paths import BASE_DIR, CONFIG_PATH
from .scm import GitRepository

cli = click.Group()

# TODO drive support
# TODO wget support
# TODO command to add links


@cli.command('add-repo')
@click.argument('scm_url')
def add_repo(scm_url):
    config = open_configuration()
    repository = GitRepository(scm_url)
    info('Cloning {repo}'.format(repo=repository))
    repository.clone()
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

    links = config.get('ln')
    for target, link in links.items():
        link_path = Path(link).expanduser()
        target_path = Path(target).expanduser()
        info('Linking {target} to {link_path}'.format_map(locals()))
        link_path.symlink_to(target_path)


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
