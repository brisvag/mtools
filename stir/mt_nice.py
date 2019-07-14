# Copyright 2019-2019 the stir authors. See copying.md for legal info.

from pymol import cmd, stored
import random
import re


def nice_settings():
    """
    sets up a series of settings and stores in pymol.stored to be used at later points by stir

    parts:
    - a set of nicely distinguishable colors for mt_color
    - a dictionary of selection expressions for mt_sele
    - a dictionary of representation information for mt_nice
    """
    # colors are based on this SO answer:
    # https://graphicdesign.stackexchange.com/questions/3682/
    # where-can-i-find-a-large-palette-set-of-contrasting-colors-for-coloring-many-d
    colors = [
        (240, 163, 255),
        (0, 117, 220),
        (153, 63, 0),
        (76, 0, 92),
        (25, 25, 25),
        (0, 92, 49),
        (43, 206, 72),
        (255, 204, 153),
        (128, 128, 128),
        (148, 255, 181),
        (143, 124, 0),
        (157, 204, 0),
        (194, 0, 136),
        (0, 51, 128),
        (255, 164, 5),
        (255, 168, 187),
        (66, 102, 0),
        (255, 0, 16),
        (94, 241, 242),
        (0, 153, 143),
        (224, 255, 102),
        (116, 10, 255),
        (153, 0, 0),
        (255, 255, 128),
        (255, 255, 0),
        (255, 80, 5),
    ]

    mt_colors = {}
    for i, rgb in enumerate(colors):
        col_name = f'mt_color_{i}'
        cmd.set_color(col_name, rgb)
        mt_colors[col_name] = rgb

    # store color ids in a list to be used by mt_color
    stored.mt_colors = []
    for color in mt_colors:
        idx = cmd.get_color_index(color)
        stored.mt_colors.append(idx)

    # selection expressions
    stored.mt_selectors = {
        'prot': 'polymer.protein',
        'BB': 'polymer.protein and name BB',
        'SC': 'polymer.protein and name SC*',
        'solv': 'resn W or resn WN or resn ION',
        'ions': 'resn ION',
        'lip': 'organic and not ions',
        'nucl': 'polymer.nucleic'
    }

    # settings to be used by mt_nice. Values are lists with a function as first element and
    # its arguments following
    stored.mt_nice_set = {
        'clean': {
            'prot': {
                'color_method': None,
                'style': None,
            },
            'BB': {
                'color_method': [mt_color, 'chain'],
                'style': [cmd.show_as, 'sticks'],
            },
            'SC': {
                'color_method': None,
                'style': [cmd.hide, 'everything'],
            },
            'solv': {
                'color_method': None,
                'style': [cmd.hide, 'everything'],
            },
            'ions': {
                'color_method': None,
                'style': [cmd.hide, 'everything'],
            },
            'lip': {
                'color_method': [mt_color, 'resn'],
                'style': [cmd.show_as, 'sticks'],
            },
            'nucl': {
                'color_method': [mt_color, 'resi'],
                'style': [cmd.show_as, 'sticks'],
            },
        },
        'rainbow': {
            'prot': {
                'color_method': None,
                'style': None,
            },
            'BB': {
                'color_method': [mt_color, 'chain'],
                'style': [cmd.show_as, 'sticks'],
            },
            'SC': {
                'color_method': [mt_color, 'resn'],
                'style': [cmd.show_as, 'sticks'],
            },
            'solv': {
                'color_method': [cmd.color, 'blue'],
                'style': [cmd.show_as, 'nb_spheres'],
            },
            'ions': {
                'color_method': [mt_color, 'name'],
                'style': [cmd.show_as, 'nb_spheres'],
            },
            'lip': {
                'color_method': [mt_color, 'resi'],
                'style': [cmd.show_as, 'sticks'],
            },
            'nucl': {
                'color_method': [mt_color, 'resn'],
                'style': [cmd.show_as, 'sticks'],
            },
        },
        'balls': {
            'prot': {
                'color_method': None,
                'style': None,
            },
            'BB': {
                'color_method': [cmd.color, 'purple'],
                'style': [cmd.show_as, 'spheres'],
            },
            'SC': {
                'color_method': [cmd.color, 'red'],
                'style': [cmd.show_as, 'spheres'],
            },
            'solv': {
                'color_method': [cmd.color, 'blue'],
                'style': [cmd.show_as, 'nb_spheres'],
            },
            'ions': {
                'color_method': [mt_color, 'resn'],
                'style': [cmd.show_as, 'nb_spheres'],
            },
            'lip': {
                'color_method': [mt_color, 'resn'],
                'style': [cmd.show_as, 'spheres'],
            },
            'nucl': {
                'color_method': [mt_color, 'resi'],
                'style': [cmd.show_as, 'spheres'],
            },
        },
    }


def mt_sele(delete=None):
    """
DESCRIPTION

    easily select relevant groups of atoms in a martini system

USAGE

    mt_sele [delete]

ARGUMENTS

    delete = if set, will delete the selections instead of creating them
    """
    if delete:
        if delete == 'delete':
            for sel in stored.mt_selectors:
                cmd.delete(sel)
        else:
            print('Unknown option. Type `mt_sele delete` to delete all the mt selections')
    else:
        for sel, logic in stored.mt_selectors.items():
            cmd.select(sel, logic)
    cmd.sync()
    # disable last selection to avoid accidental modifications to it
    cmd.deselect()
    cmd.sync()


def mt_color(method, selection='all'):
    """
DESCRIPTION

    color a selection with unique colors based on atom properties exposed by iterate

USAGE

    mt_color method [, selection]

ARGUMENTS

    method = property that will be used as a method for coloring (e.g.: "resi")
    selection = selection to act upon
    """
    stored.tmp_dict = {}
    stored.r_choice = random.choice
    cmd.iterate(selection, f'stored.tmp_dict[{method}] = stored.r_choice(stored.mt_colors)')
    cmd.alter(selection, f'color = stored.tmp_dict[{method}]')
    cmd.sync()
    stored.tmp_dict = {}
    cmd.recolor()
    cmd.sync()


def set_vdw(selection='all'):
    """
    alters vdw radii based on bead type provided by garnish
    """
    def alter_vdw(elem, vdw):
        vdw_patterns = {
            re.compile('[QPNCX][\w\d]|W'): 2.35,
            re.compile('S([QPNCX][\w\d]|W)'): 2.00,
            re.compile('T([QPNCX][\w\d]|W)'): 1.65,
        }
        for pattern, radius in vdw_patterns.items():
            if pattern.match(elem):
                return radius
        # TODO: if anything goes wrong, just return the original vdw for now
        return vdw

    stored.alter_vdw = alter_vdw

    cmd.alter(selection, 'vdw=stored.alter_vdw(elem, vdw)')
    cmd.sync()


def mt_nice(style='clean', selection='all'):
    """
DESCRIPTION

    apply a nice preset for the visualization of a martini molecular system

USAGE

    mt_nice [, style [, selection]]

ARGUMENTS

    style = one of clean|rainbow|balls (default='clean')
    selection (default='all')
    """
    # sanitize input
    if style not in ['clean', 'rainbow', 'balls']:
        print(f'Error: {style} is not a valid option. See help mt_nice')
        return

    mt_sele()

    cmd.set('stick_radius', 0.7)
    cmd.sync()
    # set correct vdw radii
    set_vdw(selection)
    cmd.sync()

    settings = stored.mt_nice_set[style]
    for sel_type, commands in settings.items():
        for command in commands.values():
            if command:
                # run function with its arguments. All functions must have `selection` as
                # valid argument for this to work!
                command[0](*command[1:], selection=f'{selection} and {sel_type}')
            else:
                continue


def load():
    nice_settings()
    cmd.extend('mt_sele', mt_sele)
    cmd.extend('mt_color', mt_color)
    cmd.extend('mt_nice', mt_nice)