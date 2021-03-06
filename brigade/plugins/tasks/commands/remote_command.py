import getpass
import logging
import shlex
import subprocess


from brigade.core.exceptions import CommandError
from brigade.core.task import Result


logger = logging.getLogger("brigade")


def remote_command(task, command, ignore_keys=True):
    """
    Executes a command on remote host via ssh.

    Arguments:
        command (``str``): command to execute

    Returns:
        :obj:`brigade.core.task.Result`:
          * result (``str``): stderr or stdout
          * stdout (``str``): stdout
          * stderr (``srr``): stderr
    Raises:
        :obj:`brigade.core.exceptions.CommandError`: when there is a command error
    """
    ip = task.host.data.get("brigade_ip", task.host.name)
    username = task.host.data.get("brigade_username", getpass.getuser())
    password = task.host.data.get("brigade_password", "")
    port = task.host.data.get("brigade_port", 22)

    options = ""

    if ignore_keys:
        options += " -o 'StrictHostKeyChecking=no' "

    command = "sshpass -p '{}' ssh {} -p {} {}@{} {}".format(password, options,
                                                             port, username, ip, command)

    logger.debug("{}:cmd:{}".format(task.host, command))
    ssh = subprocess.Popen(shlex.split(command),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=False)

    stdout, stderr = ssh.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    if ssh.poll():
        raise CommandError(command, ssh.returncode, stdout, stderr)

    result = stderr if stderr else stdout
    return Result(result=result, host=task.host, stderr=stderr, stdout=stdout)
