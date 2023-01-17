#!/usr/bin/env python3
import pathlib
import shutil
import subprocess
import sys
import zipfile


SELF_DIR = pathlib.Path(__file__).parent
LIB_DIR = SELF_DIR / 'lib'
REQUIREMENTS_PATH = SELF_DIR / 'requirements.txt'
PACKAGE_PATH = SELF_DIR / 'Totp.keypirinha-package'

PACKAGE_FILES = [
    'totp.py',
    'totp.ini',
    'LICENSE',
]


def main():
    shutil.rmtree(LIB_DIR, ignore_errors=True)

    print('Installing requirements')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--target', str(LIB_DIR), '-r', str(REQUIREMENTS_PATH)])

    print(f'Creating {PACKAGE_PATH.name}')
    with zipfile.ZipFile(PACKAGE_PATH, 'w', zipfile.ZIP_DEFLATED) as package:
        for fn in PACKAGE_FILES:
            print(f'Adding {fn}')
            package.write(SELF_DIR.joinpath(fn), fn)

        todo = [LIB_DIR]

        while todo:
            fn = todo.pop(0)
            if fn.is_dir():
                if any(map(fn.match, ('bin', 'share', 'tests', '__pycache__', '*.dist-info'))):
                    continue

                todo.extend(fn.iterdir())

            rel = fn.relative_to(SELF_DIR)
            print(f'Adding {rel}')
            package.write(fn, rel)

    print('Done')


if __name__ == "__main__":
    main()
