# -*- coding: utf-8 -*-
"""
Antwort

Usage:
    antwort.py [--template=<template>] [--in=INFILE] [--out=<outfile>] [--title=TITLE]

Options:
    --title=TITLE                       The title of the document
    -i INFILE, --in=INFILE              The input file written in the ANTWORT language
    -t TEMPLATE, --template=TEMPLATE    The template file that defines the transformations
    -o OUTFILE, --out=OUTFILE           Path of the file you would like to create
"""

import sys
import os
import codecs
import jinja2
from docopt import docopt


from antwort.lexer import AntwortLexer
from antwort.parser import AntwortParser
from antwort.visitor import PythonVisitor as Visitor


def parse(input):
    lexer = AntwortLexer(input)
    LOOKAHEAD = 2
    return AntwortParser(lexer, LOOKAHEAD).parse()


def read(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        return file.read()


def utf(path, content):
    with codecs.open(path, 'w', encoding='utf-8') as file:
        file.write(content)


def remove_empty_lines(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)


def render(path, title, data):
    path, filename = os.path.split(path)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename)
    template = template.render(title=title, questions=data.questions)
    template = remove_empty_lines(template)
    return template


def ast(data):
    data.walk(Visitor())


if __name__ == '__main__':
    arguments = docopt(__doc__)

    infile = arguments['--in']
    content = (read(infile) if infile else sys.stdin.read())
    data = parse(content)

    title = arguments['--title']
    title = (title if title else "Questionnaire - generated with ANTWORT")

    templatepath = arguments['--template']
    if not templatepath:
        ast(data)

    else:
        document = render(templatepath, title, data)
        outfile = arguments['--out']
        if outfile:
            utf(outfile, document)
        else:
            sys.stdout.write(document)
