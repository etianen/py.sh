class StyleMapping:

    def __init__(self, opts):
        self._opts = opts

    def __getitem__(self, key):
        return getattr(self._opts, "style_{}".format(key), "").encode().decode("unicode_escape")


def apply_styles(opts, command):
    return command.format_map(StyleMapping(opts))
