# Copyright 2019-2019 the stir authors. See copying.md for legal info.

from pymol import cmd
from pymol.setting import get_setting, set, name_list
import os


def store_settings(filename='/tmp/pymol_settings.py'):
    """
DESCRIPTION

    Saves all current settings to a file
    """
    if not os.path.splitext(filename)[1] == '.py':
        raise TypeError(f'{filename} must be a .py file')

    settings_dict = {}
    for setting in name_list:
        settings_dict[setting] = get_setting(setting)

    with open(filename, 'w+') as f:
        print('# pymol settings file autogenerated by stir\n', file=f)
        for setting, value in settings_dict:
            if isinstance(value, str):
                print(f'cmd.set("{setting}", "{value}")', file=f)
            elif isinstance(value, int):
                print(f'cmd.set("{setting}", {value})', file=f)
            else:
                raise ValueError(f'{value} is neither a string nor an int')


def load():
    cmd.extend('store_settings', store_settings)


if __name__ == 'pymol':
    load()