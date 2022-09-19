#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

for path in sys.path:
    if path.endswith('crawler_studio'):
        sys.path.remove(path)


def manage():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawler_studio.crawler_studio.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    manage()
