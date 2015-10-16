from clickclick import info
from pathlib import Path
import click
import yaml

from .scm import GitRepository

cli = click.Group()

BASE_DIR = Path.home() / '.ponto'  # type: Path


# TODO Init to create base structure
# TODO git-add to clone repository

@cli.command('init')
def init():
    info("Creating directory structure")
    if not BASE_DIR.exists():
        BASE_DIR.mkdir()

    config_path = BASE_DIR / 'ponto.yaml'

    info("Creating config files")
    if not config_path.exists():
        empty_config = {'SCM': set()}
        with config_path.open('w') as config_file:
            yaml.safe_dump(empty_config, config_file, default_flow_style=False)


@cli.command('clone')
# @click.argument("git_url")
def clone():
    # TODO clone git url

    config_path = BASE_DIR / 'ponto.yaml'
    with config_path.open() as config_file:
        config = yaml.load(config_file)
    scm_urls = config.get('scm', [])  # type: List[str]
    for url in scm_urls:
        repository = GitRepository(url)
        info('Cloning {repo}'.format(repo=repository))
        repository.clone()


cli()
