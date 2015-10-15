from clickclick import info
from pathlib import Path
import click
import yaml

from .scm import GitRepository

cli = click.Group()

BASE_DIR = Path.home() / '.ponto'

# TODO Init to create base structure
# TODO git-add to clone repository

@cli.command('clone')
#@click.argument("git_url")
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