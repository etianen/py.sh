from contextlib import contextmanager
import sys
import traceback
from _pysh.styles import STYLES


class TaskError(Exception):

    pass


class TaskWarning(Exception):

    pass


@contextmanager
def capture_errors(opts):
    try:
        yield
    except TaskWarning as ex:
        sys.stdout.write("{YELLOW}WARNING!{PLAIN}\n".format(**STYLES))
        sys.stdout.write("* {}\n".format(ex.args[0]))
    except KeyboardInterrupt:
        sys.stdout.write("{YELLOW}ABORTED!{PLAIN}\n".format(**STYLES))
        sys.exit(1)
    except Exception as ex:
        sys.stdout.write("{RED}ERROR!{PLAIN}\n".format(**STYLES))
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
        sys.stdout.write("{GREEN}done!{PLAIN}\n".format(**STYLES))
