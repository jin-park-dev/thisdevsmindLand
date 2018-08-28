import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = 'git@github.com:k-oneGene/thisdevsmindLand.git'

env.hosts = ['www.jinis.online']
env.user = 'jin'


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _stash_git()
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()
        _restart_gunicorn()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    # Get local machine's latest commit
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('venv/bin/pip'):
        run(f'python3.7 -m venv venv')

    run('./venv/bin/pip install --upgrade pip')
    run('./venv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv():
    append('.env', f'ENV_IS_FOR=production')
    append('.env', f'ALLOWED_HOSTS={env.hosts[0]}')
    append('.env', f'SITENAME={env.hosts[0]}')
    current_contents = run('cat .env')
    if 'SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'SECRET_KEY={new_secret}')


def _update_static_files():
    run('./venv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./venv/bin/python manage.py migrate --noinput')


def _restart_gunicorn():
    run('sudo systemctl restart gunicorn_test_server.service')


def _stash_git():
    run('git stash')
