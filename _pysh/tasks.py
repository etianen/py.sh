from contextlib import contextmanager
import sys
import traceback
from _pysh.styles import apply_styles


class TaskError(Exception):

    pass


@contextmanager
def capture_errors(opts):
    try:
        yield
    except KeyboardInterrupt:
        sys.stdout.write(apply_styles(opts, "{warn}ABORTED!{plain}\n"))
        sys.exit(1)
    except Exception as ex:
        sys.stdout.write(apply_styles(opts, "{error}ERROR!{plain}\n"))
        sys.stdout.write("{}\n".format(ex.args[0] if isinstance(ex, TaskError) else "Unexpected error."))
        if opts.traceback:
            traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    finally:
        sys.stdout.flush()


@contextmanager
def mark_task(opts, description):
    sys.stdout.write("{}... ".format(description))
    sys.stdout.flush()
    with capture_errors(opts):
        yield
        sys.stdout.write(apply_styles(opts, "{success}done!{plain}\n"))
