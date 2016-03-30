import os
import shlex
import signal
import subprocess
from _pysh.constants import CONFIG_PREFIX
from _pysh.tasks import TaskError


def create_env(opts):
    # Strip out py.sh config variables.
    env = {
        key: value
        for key, value
        in os.environ.items()
        if not key.startswith(CONFIG_PREFIX)
    }
    # Add the miniconda bin dir to the path.
    env["PATH"] = "{}:{}".format(opts.miniconda_bin_path, os.environ.get("PATH", ""))
    return env


def format_shell(command, **kwargs):
    return command.format(**{
        key: shlex.quote(value) if isinstance(value, str) else " ".join(map(shlex.quote, value))
        for key, value
        in kwargs.items()
    })


def shell(opts, command, **kwargs):
    quoted_command = format_shell(command, **kwargs)
    process = subprocess.Popen(
        quoted_command,
        env=create_env(opts),
        executable=opts.shell,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for completion.
    try:
        (stdout, stderr) = process.communicate()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGINT)
        process.communicate()
        raise
    if process.returncode != 0:
        raise TaskError("{}\n{}{}".format(
            quoted_command,
            stdout.decode(errors="ignore"),
            stderr.decode(errors="ignore"),
        ))
    return stdout


def format_shell_local(opts, command, **kwargs):
    commands = []
    # Activate conda environment.
    commands.append(format_shell(
        "source activate {conda_env} &> /dev/null",
        conda_env=opts.conda_env,
    ))
    # Activate local env file.
    env_file_path = os.path.join(opts.root_path, opts.env_file)
    if os.path.exists(env_file_path):
        commands.append(format_shell("source {env_file_path}", env_file_path=env_file_path))
    # Run the command.
    commands.append(format_shell(command, **kwargs))
    # All done!
    return " && ".join(commands)


def shell_local(opts, command, **kwargs):
    return shell(opts, format_shell_local(opts, command, **kwargs))


def shell_local_exec(opts, command, **kwargs):
    quoted_command = format_shell_local(opts, command, **kwargs)
    os.execve(opts.shell, [opts.shell, "-c", quoted_command], create_env(opts))
