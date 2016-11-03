"""
Module just to print out current version.
That's all.
"""

VERSION = (0, 1, 0)


def get_version():
    """
    Returns version
    """
    return ".".join(map(str, VERSION))


if __name__ == '__main__':
    print(get_version())
