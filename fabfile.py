# -*- coding: utf-8 -*-
import os
from fabric.api import local, env

# Get current Git branch
current_git_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)


def development():
    env.env = 'development'
    _set_env(env.env)
    env.domain = 'localhost:8000'


def staging():
    env.env = 'staging'
    _set_env(env.env)
    env.remote = 'heroku-staging {}:master'.format(current_git_branch)
    env.heroku_app = 'casp-staging'
    env.domain = '{}.herokuapp.com'.format(env.heroku_app)


def production():
    env.env = 'production'
    _set_env(env.env)
    env.remote = 'heroku-production {}:master'.format(current_git_branch)
    env.heroku_app = 'casp-production'
    env.domain = '{}.herokuapp.com'.format(env.heroku_app)


def _set_env(env):
    """Sets the env var variable"""
    os.environ['ENVIRONMENT'] = env


# === Deployment ===
def deploy():
    local('git push {remote} --force'.format(**env))


# === Static ===
def collectstatic():
    # move contents of static/ to a dir named HEAD_COMMIT_ID
    local('./manage.py collectstatic')
    if env.env != 'development':
        commit_id = local('git rev-parse HEAD', capture=True)
        _config_set(key='HEAD_COMMIT_ID', value=commit_id)


# === DB ===
def migrate():
    if env.env == 'development':
        local('./manage.py migrate')
    else:

        if raw_input('\nDo you really want to MIGRATE DATABASE of \
            {heroku_app}? YES or [NO]: '.format(**env)) == 'YES':
            local('heroku run python manage.py migrate \
                --app {heroku_app}'.format(**env))
        else:
            print('\nMIGRATE DATABASE aborted')


# === DB ===
def syncdb():
    if env.env == 'development':
        local('./manage.py syncdb'.format(**env))
    else:
        if raw_input('\nDo you really want to SYNCDB DATABASE of \
            {heroku_app}? YES or [NO]: '.format(**env)) == 'YES':
            local('heroku run python manage.py syncdb \
                --app {heroku_app}'.format(**env))
        else:
            print('\nSYNCDB DATABASE aborted')


def graph():
    local('./manage.py graph_models -a -g -o ~/Desktop/models.png')
    local('./manage.py graph_transitions -o ~/Desktop/transitions.png')


# === Heroku ===
def ps():
    local('heroku ps --app {heroku_app}'.format(**env))


def restart():
    if raw_input('\nDo you really want to RESTART (web/worker) \
        {heroku_app}? YES or [NO]: '.format(**env)) == 'YES':
        local('heroku ps:restart web --app {heroku_app}'.format(**env))
    else:
        print('\nRESTART aborted')


def tail():
    local('heroku logs --tail --app {heroku_app}'.format(**env))


def shell():
    if env.env == 'development':
        local('./manage.py shell_plus --use-pythonrc')
    else:
        local('heroku run python manage.py shell \
              --app {heroku_app}'.format(**env))


def bash():
    local('heroku run bash --app {heroku_app}'.format(**env))


def config():
    local('heroku config --app {heroku_app}'.format(**env))


def _config_set(key=None, value=None):
    if key and value:
        local('heroku config:set {}={} \
            --app {heroku_app}'.format(key, value, **env))
    else:
        print('\nErr!')


def maintenance(mode='on'):
    local('heroku maintenance:{} --app {heroku_app}'.format(mode, **env))


# === Utils ===
def generatesecret():
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    key = get_random_string(50, chars)
    print('key: {}'.format(key))

def initialsetup():
    local('python manage.py syncdb --noinput')
    local('python manage.py migrate apps.profiles')
    local('python manage.py migrate apps.contacts')
    local('python manage.py migrate')
    local('python manage.py update_permissions')
