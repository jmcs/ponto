from clickclick import info
from pathlib import Path
from subprocess import run
import click
import os
import platform
from .configuration import open_configuration, save_configuration
from .drive import Drive
from .paths import BASE_DIR, CONFIG_PATH, DRIVE_DIR, HOME_PATH, relative_to_home
from .scm import GitRepository, ConfigRepo

cli = click.Group()


# TODO remove support
# TODO detect dependencies
# TODO wget support

@cli.command('add-drive')
@click.argument('ACCOUNT')
@click.argument('LOCAL_NAME')
@click.argument('DRIVE_NAME')
def add_drive(account, local_name, drive_name):
    config = open_configuration()
    drive = Drive()
    drive.init(account, local_name, drive_name)
    config['drive'][local_name] = {'account': account, 'drive_name': local_name}
    save_configuration(config)
    repo = ConfigRepo()
    repo.add('ponto.yaml')
    repo.commit('Added drive from {account}/{drive_name} to ~/{local_name}'.format_map(locals()))


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
@click.argument("GIT_URL")
def clone(git_url: str):
    repo = ConfigRepo()
    info("Cloning Repository")
    repo.clone(git_url)

    pre_script = BASE_DIR / 'pre.sh'

    system_pre_script = BASE_DIR / 'pre-{system}.sh'.format(system=platform.system().lower())
    if system_pre_script.exists():
        info('Executing pre script for this OS')
        run(str(system_pre_script.absolute()))

    if pre_script.exists():
        info('Executing pre script')
        run(str(pre_script.absolute()))

    sync(pull=False)


@cli.command('edit-pre')
@click.option('--global', 'system', flag_value=None,
              default=True)
@click.option('--linux', 'system', flag_value='linux')
@click.option('--darwin', 'system', flag_value='darwin')
def edit_pre(system):
    filename = 'pre-{system}.sh'.format_map(locals()) if system else 'pre.sh'
    pre_script = BASE_DIR / filename
    run(['vim', str(pre_script.absolute())])
    pre_script.chmod(0o750)
    repo = ConfigRepo()
    repo.add(filename)
    commit_message = input('Commit message: ') or 'Updated Pre-Script'
    commit_message = '{filename}: {commit_message}'.format_map(locals())
    repo.commit(commit_message)


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

    if not DRIVE_DIR.exists():
        DRIVE_DIR.mkdir()

    gitignore_path = BASE_DIR / '.gitignore'
    if not gitignore_path.exists():
        with gitignore_path.open('w') as gitignore:
            gitignore.write(b'drive\n')

    info("Creating config files")
    if not CONFIG_PATH.exists():
        empty_config = {'drive': dict(),
                        'scm': set(),
                        'ln': dict()}
        save_configuration(empty_config)

    cwd = Path.cwd()
    os.chdir(str(BASE_DIR))
    repo.add('ponto.yaml')
    repo.add('.gitignore')
    repo.commit('Initialization')
    repo.push()
    os.chdir(str(cwd))


@cli.command('push')
def push():
    repo = ConfigRepo()
    if HOME_PATH.exists():
        repo.add('home')
        # TODO try catch error
        repo.commit('Included local changes')
    repo.push()


@cli.command('store')
@click.argument('PATH')
def store(path):
    path = Path(path)

    if path.is_symlink():
        print("{path} is already a symlink.".format(path=path))
        return

    print("Storing {path}".format(path=path))
    relative_path = path.relative_to(Path.home())

    try:
        HOME_PATH.mkdir(parents=True)
    except FileExistsError:
        pass

    destination = HOME_PATH / relative_path

    try:
        destination.parent.mkdir(parents=True)
    except FileExistsError:
        pass

    path.rename(destination)
    path.symlink_to(destination)

    repo = ConfigRepo()
    repo.add(str('home' / relative_path))
    repo.commit("Storing {path}".format(path=path))

    # TODO error if not inside home


@cli.command('sync')
def sync(pull=True):
    if pull:
        repo = ConfigRepo()
        repo.pull()

    config = open_configuration()

    drive_points = config.get('drive', {})  # type: dict[str, dict]
    drive = Drive()
    for local_name, point in drive_points.items():
        account = point['account']
        drive_name = point['drive_name']
        # TODO ignore on error
        info('Cloning {account}/{drive_name} to ~/{local_name}'.format_map(locals()))
        drive.init(account, local_name, drive_name)

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
            info('{link} already exists'.format_map(locals()))

            # TODO dotfiles

    for path in HOME_PATH.glob('**/*'):
        relative_path = path.relative_to(HOME_PATH)
        link_path = Path.home() / relative_path
        if link_path.exists():
            # TODO offer to replace
            print("~/{relative_path} already exists.".format_map(locals()))
        else:
            print("Linking ~/{relative_path}.".format_map(locals()))
            link_path.symlink_to(path)
cli()
