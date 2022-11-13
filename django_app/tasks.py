import threading
import socket
import time
import environ
from invoke import task

env = environ.Env()


def wait_port_is_open(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print("DB connected!")
            return False
        time.sleep(1)
        print("Reconnecting...")


@task
def init_db_local(ctx):
    host = env('POSTGRES_HOST')
    port = env.int('POSTGRES_PORT')
    wait_port_is_open(host, port)
    ctx.run('python manage.py dbshell < drop_db.sql')
    ctx.run('python manage.py dbshell < dump.sql')


@task
def collect_static_element(ctx):
    ctx.run('python manage.py collectstatic --noinput')


@task
def cron(ctx):
    ctx.run(f'python manage.py cronloop')


@task
def rundev(ctx):
    init_db_local(ctx)

    collect_static_element(ctx)
    thread_cron = threading.Thread(target=cron, args=(ctx,))
    thread_cron.start()

    ctx.run('python manage.py makemigrations')
    ctx.run('python manage.py migrate')
    ctx.run('uwsgi --ini dev_uwsgi.ini')
