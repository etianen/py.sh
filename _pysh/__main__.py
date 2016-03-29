import sys
from _pysh.opts import parse_args
from _pysh.tasks import capture_errors


# Main method.

def main():
    opts, unknown_args = parse_args(sys.argv[1:])
    with capture_errors(opts):
        opts.func(opts, unknown_args)


if __name__ == "__main__":
    main()
