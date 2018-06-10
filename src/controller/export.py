import os
import subprocess
from string import Template
from operator import attrgetter

from data.model import Tournament, Round, Team, Game

_export_path = os.path.relpath('resources/export/')

def _load_template():
    template = os.path.relpath('resources/latex/template.tex')
    with open(template, 'r') as infile:
        return Template(infile.read())


def _write_export(output_file, content):
    os.makedirs(_export_path, exist_ok=True)

    with open(output_file + '.tex', 'w') as outfile:
        outfile.write(content)


def _generate_export(file):
    subprocess.run(['pdflatex', '-output-directory', _export_path, 
                    '-interaction=nonstopmode', file + '.tex'])
    # remove aux and log
    aux = os.path.relpath(file + '.aux')
    log = os.path.relpath(file + '.log')
    os.remove(aux)
    os.remove(log)


def export_round(tournament, round):
    title_str = 'Round ' + str(round + 1)
    subtitle_str = tournament.name
    columns = 'lXXc'
    header = 'Number & Team A & Team B & Result \\\\'
    content = ''
    for i, game in enumerate(tournament.rounds[round].games):
        team_a = game.team_a
        team_b = 'free' if game.team_b is None else game.team_b
        result = '$$ : $$' 
        if game.is_finished():
            result = ('$$' + str(game.points_a) + ' : ' + str(game.points_b)
                      + '$$')
        content += (str(game.id) + ' & ' + team_a + ' & ' + team_b + ' & '
                    + result + ' \\\\' + '\n' )
        if i != len(tournament.rounds[round].games) - 1:
            content += '\\midrule'
            content += '\n'
    export_template = _load_template()
    substituted_template = export_template.substitute(
                               title=title_str,
                               subtitle=subtitle_str,
                               tablecolumns=columns, 
                               tableheader=header,
                               tablecontent=content)
    file_name = os.path.relpath(_export_path + '/' + tournament.name + '-r' 
                                + str(round + 1))
    _write_export(file_name, substituted_template)
    _generate_export(file_name)


def export_standings(tournament):
    title_str = 'Standings'
    subtitle_str = tournament.name
    
    columns = 'lXcccccccccc'
    header = ('P & Team & MP & W & L & BH & '
              'FBH & SB & Koya & P & PD & FR \\\\')
    content = ''
    for i, team in enumerate(sorted(tournament.teams, 
                                    key=attrgetter('position'))):
        position = str(team.position)
        name = team.name
        matches = str(team.wins + team.losses)
        wins = str(team.wins)
        losses = str(team.losses)
        bh = str(team.bh)
        fbh = str(team.fbh)
        sb = str(team.sb)
        koya = str(team.koya)
        p = '$$ ' + str(team.points) + ':' + str(team.points_against) + ' $$'
        pd = str(team.points - team.points_against)
        fr = str(team.fl)
        pv = str(team.performance_value)
        content += (position + ' & ' + name + ' & ' + matches + ' & ' + wins
                    + ' & ' + losses + ' & ' + bh + ' & ' + fbh + ' & ' + sb
                    + ' & ' + koya + ' & ' + p + ' & ' + pd
                    + ' & ' + fr + ' \\\\' + '\n' )
        if i != len(tournament.teams) - 1:
            content += '\\midrule'
            content += '\n'
    export_template = _load_template()
    substituted_template = export_template.substitute(
                               title=title_str,
                               subtitle=subtitle_str,
                               tablecolumns=columns, 
                               tableheader=header,
                               tablecontent=content)
    file_name = os.path.relpath(_export_path + '/' + tournament.name
                                + '-standings')
    _write_export(file_name, substituted_template)
    _generate_export(file_name)
