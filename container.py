import click 
import os
import traceback

@click.group()
def cli():
    pass

def container(command):
    os.execv(command[0], command)

@cli.command(context_settings={'ignore_unknown_options':True})
@click.argument('command', required=True, nargs=-1)
@click.option('--info', '-i', help='info of your process')
def run(command, info):
    pid = os.fork()

    if pid == 0:
        try:
            container(command)
        except Exception:
            traceback.print_exc()
            os._exit(1)
    elif pid > 0:
    	_, status = os.waitpid(pid, 0)
    	print('process (PID={}) exited with status {}'.format(pid, status))
    elif pid < 0:
    	raise Exception('fork erorr')

if __name__ == '__main__':
	cli()
