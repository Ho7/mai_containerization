import os
import tarfile
import uuid

import click
import traceback

import linux


def _get_image_path(image_name, image_dir, image_suffix='tar'):
    return os.path.join(image_dir, os.extsep.join([image_name, image_suffix]))


def _get_container_path(container_id, container_dir, *subdir_names):
    return os.path.join(container_dir, container_id, *subdir_names)


def create_container_root(image_name, image_dir, container_id, container_dir):
    """Create a container root by extracting an image into a new directory
    Usage:
    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)
    @param image_name: the image name to extract
    @param image_dir: the directory to lookup image tarballs in
    @param container_id: the unique container id
    @param container_dir: the base directory of newly generated container
                          directories
    @retrun: new container root directory
    @rtype: str
    """
    image_path = _get_image_path(image_name, image_dir)
    container_root = _get_container_path(container_id, container_dir, 'rootfs')

    assert os.path.exists(image_path), "unable to locate image %s" % image_name

    if not os.path.exists(container_root):
        os.makedirs(container_root)

    with tarfile.open(image_path) as t:
        # Fun fact: tar files may contain *nix devices! *facepalm*
        members = [m for m in t.getmembers()
                   if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
        t.extractall(container_root, members=members)

    return container_root

#123
@click.group()
def cli():
    pass


def container(command):
    os.execv(command[0], command)


def get_info(info):
    print(info)


@cli.command(context_settings={'ignore_unknown_options': True})
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
        if info:
            message = 'process pid={}'.format(pid)
            get_info(message)
    elif pid > 0:
        _, status = os.waitpid(pid, 0)
        print('process (PID={}) exited with status {}'.format(pid, status))
    elif pid < 0:
        raise Exception('fork erorr')


if __name__ == '__main__':
    cli()
