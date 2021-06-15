#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def setup():
    """Setup environment for wahlfang"""
    if os.getenv('DJANGO_SETTINGS_MODULE') is not None:
        return

    if os.getenv('WAHLFANG_DEBUG'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'wahlfang.settings.development'
        return

    wahlfang_config = os.getenv('WAHLFANG_CONFIG', '/etc/wahlfang/settings.py')
    if not os.path.exists(wahlfang_config):
        print(f'Wahlfang configuration file at {wahlfang_config} does not exist', file=sys.stderr)
        print('Modify "WAHLFANG_CONFIG" environment variable to point at settings.py', file=sys.stderr)
        sys.exit(1)

    config_path = Path(wahlfang_config).resolve()
    sys.path.append(str(config_path.parent))

    os.environ['DJANGO_SETTINGS_MODULE'] = config_path.stem


def main():
    setup()

    try:
        from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
