#!/usr/bin/env python
import os
import sys

import dotenv

try:
    dotenv.read_dotenv()
except:
    pass

if __name__ == "__main__":
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT').title()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "casp.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", ENVIRONMENT)

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
