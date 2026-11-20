#!/usr/bin/env python
import os
import sys
import types
from pathlib import Path


if __name__ == '__main__':
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root.parent))
    parcial_package = types.ModuleType('parcial')
    parcial_package.__path__ = [str(project_root)]
    sys.modules.setdefault('parcial', parcial_package)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)