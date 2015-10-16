from clickclick import info
from pathlib import Path
from subprocess import run
import click
import os
from .configuration import open_configuration, save_configuration
from .paths import BASE_DIR, CONFIG_PATH, relative_to_home
from .scm import GitRepository, ConfigRepo

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
    repo = ConfigRepo()
    repo.add('ponto.yaml')
    repo.commit('Added symlink from {target_path} to {link_path}'.format_map(locals()))


@cli.command('add-repo')
@click.argument('SCM_URL')
def add_repo(scm_url):
    config = open_configuration()
    repository = GitRepository(scm_url)
    info('Cloning {repo}'.format(repo=repository))
    repository.clone()
    config['scm'].add(scm_url)
    save_configuration(config)
    repo = ConfigRepo()
    repo.add('ponto.yaml')
    repo.commit("Added '{repository}' to the repository list".format_map(locals()))


@cli.command('clone')
# @click.argument("git_url")
def clone():
    # TODO clone git url

    pre_script = BASE_DIR / 'pre.sh'

    if pre_script.exists():
        # TODO pre by os
        info('Executing pre script')
        run(str(pre_script.absolute()))

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


@cli.command('edit-pre')
def edit_pre():
    pre_script = BASE_DIR / 'pre.sh'
    run(['vim', str(pre_script.absolute())])
    repo = ConfigRepo()
    repo.add('pre.sh')
    repo.commit("Updated pre script".format_map(locals()))


@cli.command('init')
@click.argument("GIT_URL")
def init(git_url):
    repo = ConfigRepo()
    # TODO receive remote and push

    info("Setting up git repository")
    git_folder = BASE_DIR / '.git'
    if not git_folder.exists():
        repo.init()
        # TODO context manager
        cwd = Path.cwd()
        os.chdir(str(BASE_DIR))
        run(['git', 'remote', 'add', 'origin', git_url])
        os.chdir(str(cwd))
    info("Creating directory structure")
    if not BASE_DIR.exists():
        BASE_DIR.mkdir()

    info("Creating config files")
    if not CONFIG_PATH.exists():
        empty_config = {'scm': set(), 'ln': dict()}
        save_configuration(empty_config)

    cwd = Path.cwd()
    os.chdir(str(BASE_DIR))
    repo.add('ponto.yaml')
    repo.commit('Initialization')
    repo.push()
    os.chdir(str(cwd))


@cli.command('push')
def push():
    repo = ConfigRepo()
    repo.push()


cli()
