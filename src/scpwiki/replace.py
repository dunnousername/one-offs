#!/usr/bin/python3
# converts a folder of text files from a wdotcrawl backup of the SCP Wiki to Latex PDFs.
# ./replace.py [folder of text files]
# tested on windows 10

import glob
import io
import itertools
import os
import re
import sys

from multiprocessing import Pool

class LatexConverter:
    ALLOW_INTERNET = True

    HEADER = """
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{ulem}
\\usepackage{enumitem}
\\usepackage{fdsymbol}
\\usepackage{newunicodechar}
\\usepackage{hyperref}
\\usepackage[margin=0.7in]{geometry}
\\newunicodechar{█}{\\ensuremath{\\largeblacksquare}}
\n"""

    POSTHEADER = """
\\begin{document}
\\maketitle
\\setlist[enumerate]{label=\\arabic*.}
\n"""

    FOOTER = """\n
\\end{document}
    """
    #ESCAPE = r'\@\@(.*?)\@\@'
    APPLY_ONCE = [
        (r'\@\@(.*?)\@\@', r'\\begin{verbatim} \1 \\end{verbatim}'),
        (r'\{\{(.*?)\}\}', r'\\texttt{\1}'),
    ]

    REGEXES = [
        # (r'\@\@(.*?)\@\@', r'\\begin\{verbatim\} \1 \\end\{verbatim\}')
        (r'\*\*(.*?)\*\*', r'\\textbf{\1}'),
        (r'\\_\\_(.*?)\\_\\_', r'\\underline{\1}'),
        (r'\-\-(.*?)\-\-', r'\\sout{\1}'),
        (r'\/\/(.*?)\/\/', r'\\textit{\1}'),
        # (r'\{\{(.*?)\}\}', r'\\texttt\{\1\}'),
        (r'\[\[\/[ \t]*collapsible[ \t]*\]\]', r'\\end{quote}'),
        (r'\[\[[ \t]*collapsible (?:.*? )?(?:show\=\"(.*?)\")(?:.*?)\]\]', r'\\subsection{\1}\n\\begin{quote}'),
        (r'\[\[[ \t]*collapsible(?:.*?)\]\]', r'\\begin{quote}'),
        (r'((?:(?:^>(?:[^\n]*)$)\n?)+)', r'\\begin{quote}\n\1\\end{quote}\n'),
        (r'^> ?([^\n]*)$', r'\1')
    ]

    if ALLOW_INTERNET:
        REGEXES.extend([
            (r'\[[ \t]*\*?((?:https?|ftp)\://[^ \t\n\]]+)[ \t]*\]', r'\\url{\1}'),
            (r'\[[ \t]*\*?((?:https?|ftp)\://[^ \t\n\]]+)[ \t]+([^\]\n]+)\]', r'\\href{\1}{\2}'),
            (r'\[\[\[[ \t]*\*?((?:https?|ftp)\://[^ \t\n\]]+)[ \t]*\|[ \t]*([^\]\n]+)\]\]\]', r'\\href{\1}{\2}')
        ])

    ESCAPE = [
        (r'\\', r'\\textbackslash'),
        (r'\^', r'\\textasciicircum'),
        (r'~', r'\\textasciitilde'),
        (r'\{', r'\\{'),
        (r'\}', r'\\}'),
        (r'#', r'\\#'),
        (r'&', r'\\&'),
        (r'\$', r'\\$'),
        (r'_', r'\\_'),
    ]

    PREPROCESS = [
        #(r'^(\s*)\* ', r' \1* '),
        #(r'^(\s*)\\# ', r' \1\\# '),
        (r'\[/?footnote[^\]\n]*\]', r'')
    ]

    LOOPED = [
        #(r'^\s(\s*)\* ([^\n]*)$', r'\\begin{itemize}\n\1* \2\n\\end{itemize}'),
        #(r'^\s(\s*)\\# ([^\n]*)$', r'\\begin{enumerate}\n\1\\# \2\n\\end{enumerate}')
    ]

    LOOPED2 = [
        #(r'^\\end\{itemize\}\n\\begin\{itemize\}$', r''),
        #(r'^\\end\{enumerate\}\n\\begin\{enumerate\}$', r'')
    ]

    POSTPROCESS = [
        #(r'^\* ', r'\\item '),
        #(r'^\\# ', r'\\item '),
        #(r'(?<!\\begin\{enumerate\}\n)\\begin\{enumerate\}\n\\begin\{enumerate\}\n', r'\\begin{enumerate}\n'),
        #(r'(?<!\\begin\{itemize\}\n)\\begin\{itemize\}\n\\begin\{itemize\}\n', r'\\begin{itemize}\n'),
        #(r'\n\\end\{enumerate\}\n\\end\{enumerate\}(?!\n\\end\{enumerate\})', r'\\end{enumerate}\n'),
        #(r'\n\\end\{itemize\}\n\\end\{itemize\}(?!\n\\end\{itemize\})', r'\\end{itemize}\n'),
        (r'\[\[\[(?:[^\[\]\n\|]+)\|([^\[\]\n\|]+)\]\]\]', r'\1'),
        (r'\[\[\[([^\[\]\n]+)\]\]\]', r'\1'),
        (r'\[\[[^\[\]\n]+\]\]', r''),
        #(r'[^a-z0-9]\[', r'\\lbrack{}'),
        #(r'\][^a-z0-9]', r'\\rbrack{}')
        
    ]

    TITLE_REPLACE = [
        ('-', ' '),
        ('__q__', '?'),
        ('__p__', '%'),
        ('__', ':'),
    ]

    CAPITALIZATION = [
        r'(?:^| )((?:dr|mrs?|ms)\.? [a-z]+)(?: |$)',
        r'(?:^| )(scp-[0-9]+(?:-?J)?)(?: |$)',
        r'(?:^| )(site-(?:[0-9a-z]+-?)+)(?: |$)'
    ]

    PROPER_NOUNS = [
        'SCP',
        'Foundation'
    ]

    TITLE_REGEXES = [
        (r'(^| )(dr|mrs?|ms)( |$)', r'\1\2.\3')
    ]

    SCP_REGEX = re.compile(r'^SCP\-[0-9]+(?:\-?J)?$', re.I | re.M)

    SHIELD = '%%SHIELD%%'

    def _compile(self, entry):
        return (re.compile(entry[0], re.M), entry[1])
    
    def compile(self, arr):
        return [self._compile(entry) for entry in arr]

    def __init__(self):
        self.APPLY_ONCE = self.compile(self.APPLY_ONCE)
        self.REGEXES = self.compile(self.REGEXES)
        self.ESCAPE = self.compile(self.ESCAPE)
        self.PREPROCESS = self.compile(self.PREPROCESS)
        self.LOOPED = self.compile(self.LOOPED)
        self.LOOPED2 = self.compile(self.LOOPED2)
        self.POSTPROCESS = self.compile(self.POSTPROCESS)
        self.TITLE_REGEXES = self.compile(self.TITLE_REGEXES)
        self.CAPITALIZATION = [re.compile(r, re.M) for r in self.CAPITALIZATION]

    def escape(self, text: str):
        for (r, w) in self.ESCAPE:
            text = r.sub(w, text)
        return text

    def make_title(self, title):
        for (r, w) in self.TITLE_REPLACE:
            title = title.replace(r, w)
        for (r, w) in self.TITLE_REGEXES:
            title = r.sub(w, title)
        for r in self.CAPITALIZATION:
            for m in r.finditer(title):
                title = title.replace(m.group(1), m.group(1).title())
        for n in self.PROPER_NOUNS:
            title = title.replace(n.lower(), n)
        return title[0].upper() + title[1:]

    def generate_header(self, name):
        if name is None:
            return '\n'
        name = '.'.join(name.split('.')[:-1])
        scp = True if self.SCP_REGEX.match(name) else False
        title = name.upper() if scp else self.make_title(name.lower())
        prefix = '\\title{' + self.escape(title) + '}\n'
        return self.HEADER + prefix + self.POSTHEADER

    def _make_item(self, text: str, sep: str):
        body = text.replace(sep + ' ', '', 1)
        if body.startswith('['):
            tmp = body.split(' ')
            body = '{' + tmp[0] + '} ' + ' '.join(tmp[1:])
        return '\\item ' + body
    
    def _convert_list(self, lines: list, header: str, footer: str, sep: str):
        for k, g in itertools.groupby(lines, lambda x: x.index(sep) == 0):
            if k:
                yield from [self._make_item(x, sep) for x in g]
            else:
                g = list(g)
                min_space = min(len(l) - len(l.lstrip()) for l in g)
                yield header
                yield from self._convert_list(
                    [l[min_space:] for l in g],
                    header,
                    footer,
                    sep
                )
                yield footer

    #def convert_list(self, text: str, header: str, footer: str, sep: str):
    #    return '\n'.join([header] + list(self._convert_list(text.splitlines(), header, footer, sep)) + [footer])

    def _find_and_convert_lists(self, lines: list, header: str, footer: str, sep: str):
        for k, g in itertools.groupby(lines, lambda x: (sep in x) and (x.lstrip().index(sep) == 0)):
            if not k:
                yield from g
            else:
                yield header
                yield from self._convert_list(g, header, footer, sep)
                yield footer
    
    def find_and_convert_lists(self, text: str):
        lines = text.splitlines()
        lines = list(self._find_and_convert_lists(lines, '\\begin{itemize}', '\\end{itemize}', '*'))
        lines = list(self._find_and_convert_lists(lines, '\\begin{enumerate}', '\\end{enumerate}', '\\#'))
        return '\n'.join(lines)

    def convert(self, text: str, name=None):
        text = '\n'.join(text.splitlines()[4:-4])
        text = self.escape(text)
        for (r, w) in self.PREPROCESS:
            text = r.sub(w, text)
        to_shield = []
        for (r, w) in self.APPLY_ONCE:
            to_shield.extend(r.finditer(text))
        to_shield = sorted(to_shield, key=lambda m: m.start())
        shielded_table = []
        shielded = []
        i = 0
        for m in to_shield:
            shielded.append(text[i:m.start()])
            shielded.append(self.SHIELD)
            w = [w for (r, w) in self.APPLY_ONCE if m.re == r][0]
            shielded_table.append(m.expand(w))
            shielded.append(self.SHIELD)
            i += m.end() - m.start()
        if i < len(text):
            shielded.append(text[i:])
        new_text = ''.join(shielded)
        for (r, w) in self.REGEXES:
            new_text = r.sub(w, new_text)
        done = False
        while not done:
            done = True
            for (r, w) in self.LOOPED:
                new_text_ = r.sub(w, new_text)
                if not (new_text_ == new_text):
                    done = False
                new_text = new_text_
        done = False
        while not done:
            done = True
            for (r, w) in self.LOOPED2:
                new_text_ = r.sub(w, new_text)
                if not (new_text_ == new_text):
                    done = False
                new_text = new_text_
        new_text = self.find_and_convert_lists(new_text)
        for (r, w) in self.POSTPROCESS:
            new_text = r.sub(w, new_text)
        for s in shielded_table:
            new_text = new_text.replace(self.SHIELD, s, 1)
        return self.generate_header(name) + new_text + self.FOOTER

    def convert_file(self, f):
        fn = None
        if isinstance(f, bytes):
            f = f.decode('utf-8')
        if isinstance(f, str):
            fn = os.path.basename(f)
            f = open(f, 'r', encoding='utf-8')
        with f:
            return self.convert(f.read(), name=fn)

def process(filenames):
    l = LatexConverter()
    for fn in filenames:
        out = l.convert_file(fn)
        out_name = '.'.join(os.path.basename(fn).split('.')[:-1]) + '.tex'
        with open(out_name, 'w', encoding='utf-8') as f:
            f.write(out)

def chunks(iterable, amount):
    i = list(iterable)
    while len(i):
        yield i[:amount]
        i = i[amount:]

def host(filenames):
    c = list(chunks(filenames, 50))
    with Pool(12) as p:
        p.map(process, c)

if __name__ == "__main__":
    host(glob.glob(sys.argv[1] + '/*.txt'))
