import os
import shlex
import signal
import subprocess
from _pysh.config import CONFIG_PREFIX
from _pysh.tasks import TaskError
from _pysh.styles import apply_styles


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
    return format_shell(
        apply_styles(opts, (
            "if source activate {{conda_env}} &> /dev/null ; then "
            "test -f {{env_file_path}} && source {{env_file_path}} ; "
            "{{{{command}}}} ; "
            "else "
            "printf \"{error}ERROR!{plain}\\nRun ./{{script_name}} install before attempting other commands.\\n\" ; "
            "fi"
        )),
        conda_env=opts.conda_env,
        env_file_path=os.path.join(opts.root_path, opts.env_file),
        script_name=opts.script_name,
    ).format(command=format_shell(command, **kwargs))


def shell_local(opts, command, **kwargs):
    return shell(opts, format_shell_local(opts, command, **kwargs))


def shell_local_exec(opts, command, **kwargs):
    quoted_command = format_shell_local(opts, command, **kwargs)
    os.execve(opts.shell, [opts.shell, "-c", quoted_command], create_env(opts))
