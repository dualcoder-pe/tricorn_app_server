def get_version():
    with open("version.txt", "r") as f:
        return f.read().strip()


__version__ = get_version()
