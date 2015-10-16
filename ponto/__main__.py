from clickclick import info
from pathlib import Path
import click

from .configuration import open_configuration, save_configuration
from .paths import BASE_DIR, CONFIG_PATH, relative_to_home
from .scm import GitRepository

cli = click.Group()

# TODO drive support
# TODO wget support
# TODO command to add links


@cli.command('add-link')
@click.argument('TARGET')
@click.argument('LINK_NAME')
def add_link(target, link_name):
    config = open_configuration()
    link_path = relative_to_home(link_name)
    target_path = relative_to_home(target)
    info('Linking {target_path} to {link_path}'.format_map(locals()))
    link_path.expanduser().symlink_to(target_path.expanduser())
    config['ln'][str(target_path)] = str(link_path)
    save_configuration(config)


@cli.command('add-repo')
@click.argument('SCM_URL')
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
        if not link_path.exists():
            info('Linking {target_path} to {link_path}'.format_map(locals()))
            link_path.symlink_to(target_path)
        else:
            info('{target} already exists'.format_map(locals()))


@cli.command('init')
def init():

    # TODO receive remote and push

    info("Creating directory structure")
    if not BASE_DIR.exists():
        BASE_DIR.mkdir()

    info("Creating config files")
    if not CONFIG_PATH.exists():
        empty_config = {'scm': set(), 'ln': dict()}
        save_configuration(empty_config)


cli()
