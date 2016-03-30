from contextlib import contextmanager
import sys
import traceback


class TaskError(Exception):

    pass


class TaskWarning(Exception):

    pass


@contextmanager
def capture_errors(opts):
    try:
        yield
    except TaskWarning as ex:
        sys.stdout.write("\033[33mWARNING!\033[0m\n")
        sys.stdout.write("* {}\n".format(ex.args[0]))
    except KeyboardInterrupt:
        sys.stdout.write("\033[33mABORTED!\033[0m\n")
        sys.exit(1)
    except Exception as ex:
        sys.stdout.write("\033[31mERROR!\033[0m\n")
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
        sys.stdout.write("\033[32mdone!\033[0m\n")
