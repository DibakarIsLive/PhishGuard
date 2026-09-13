#!/usr/bin/env python
import os
import sys


FORCE_FLAG = "--force"


def _runserver_index(argv):
    """Return the runserver command index, or None for other commands."""
    try:
        return argv.index("runserver", 1)
    except ValueError:
        return None


def _prepare_runserver_arguments(argv):
    """Remove PhishGuard's force flag before Django parses runserver options."""
    command_index = _runserver_index(argv)
    if command_index is None:
        return list(argv), False

    force = False
    cleaned = []
    for index, argument in enumerate(argv):
        if index > command_index and argument == FORCE_FLAG:
            force = True
            continue
        cleaned.append(argument)
    return cleaned, force


def _require_mongodb(force=False):
    """Stop normal runserver startup unless the configured MongoDB is reachable."""
    if force:
        return

    from url_analysis.database import mongodb_is_reachable

    if mongodb_is_reachable():
        return

    raise SystemExit(
        "MongoDB startup check failed. Start the configured MongoDB server before "
        "running the PhishGuard API. To explicitly bypass this development check, "
        "use `python3 manage.py runserver --force` or `make dev FORCE=1`."
    )


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    argv, force = _prepare_runserver_arguments(sys.argv)
    sys.argv[:] = argv

    if _runserver_index(argv) is not None:
        _require_mongodb(force=force)

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)


if __name__ == "__main__":
    main()
