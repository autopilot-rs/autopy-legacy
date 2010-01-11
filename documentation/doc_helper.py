#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is just a simple script I use to help extract the documentation I have
written throughout the program. The documentation is by no means auto-generated
-- I edit it by hand -- but having relevant portions intermixed with the code
helps me keep it up-to-date.

Essentially, this extracts comments I have interspersed throughout the source
code and outputs them in a pseudo-XML format I deem as an "MMM" file, which I
roughly define as follows:

File syntax:
        <mmm type="(module|class|index)">
        <name>module name</name>
        <summary>...</summary> (optional)
        <description>...</description> (optional)

        <section name="Functions"> (optional)
            <function>
                <syntax>...</syntax>
                <retval>...</retval> (optional; otherwise assumed None)
                <arguments>...</arguments>
                <description>...</description>
                <exceptions> (optional; otherwise assumed none)
                    <exception name="ExceptionName">...</exception>
                </exceptions>
            </function>
        </functions>

        <section name="Constants"> (optional)
            <constant name="...">
                <value>...</value> (optional)
                <description>...</description> (optional)
            </constant>
        </section>
        </mmm>

Attribute tags (enclosed in brackets):
    - keyword (e.g. integer, double)
    - const (e.g. True, False)
    - mono (anything you want to be monospaced)
    - note (formatted block note)
    - bcode (block code segment)

MMM files can also contain HTML tags (as that is what they are intended to
eventually be converted into), and they will be ignored.
"""

import glob
import os
import re
import textwrap

from XMLGen import XMLGen
from lxml import etree
from sys import argv

def itercat(*iterators):
    """Concatentate several iterators into one."""
    for i in iterators:
        for x in i:
            yield x

def replace_range(str, start, end, repl):
    """Replaces range of characters in str with repl."""
    return str[:start] + repl + str[end:]

def brace_expand(str):
    """Perform brace expansion, a lá bash."""
    match = re.search('{(.+?)(,.*?)?}', str)
    if match:
        strings = brace_expand(replace_range(str,
                                             match.start(),
                                             match.end(),
                                             match.group(1)))
        if match.group(2):
            strings.extend(brace_expand(replace_range(str,
                                                      match.start(),
                                                      match.end(),
                                                      match.group(2)[1:])))
        return strings
    else: # No braces were in the string.
        return [str]

def braceglob(pathname):
    """Returns iterator of brace expansion and globbing on files."""
    return itercat(*(glob.iglob(path) for path in brace_expand(pathname)))

def get_comments(pathnames):
    """
    Extracts comments from given paths.
    Returns dictionary with pathnames as keys and a list of comments as values.
    """
    # Note that is NOT perfect: it matches certain edge cases such as
    # printf("hello /* word */ "), but we're just ignoring that, since it
    # doesn't happen in this project and it is not really worth implementing a
    # parser for this.
    get_comments.regex = re.compile(r'/\*\s*(.+?)\s*\*/', re.DOTALL)
    comments = {}
    for path in pathnames:
        f = open(path, 'r')
        comments[path] = (str for str in get_comments.regex.findall(f.read()))
        f.close()
    return comments

def escape_for_xml(str):
    """Returns string with illegal XML entities escaped."""
    def replace_all(str, replacements):
        for item, repl in replacements.iteritems():
            str = str.replace(item, repl)
        return str
    escape_for_xml.replacements = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
    return replace_all(str, escape_for_xml.replacements)

def format_comment(comment):
    """
    Returns a formatted comment, meaning:
        1.) Extraneous whitespace is ignored.
        2.) Special symbols (e.g. |...|, `...`, {% ... %}) and words (e.g.
            True, False) are given descriptive tags. These tags are to be used
            in an "MMM" file, a format I have invented solely for the purpose
            of this script.
    """
    def format_block(str):
        return textwrap.dedent(str) if '\n' in str else str.strip()
    def format_code_repl(match):
        return '\n<%s>%s</%s>' % ('bcode',
                                  format_block(match.group(1)),
                                  'bcode')

    format_comment.needles = [(re.compile(r'\|(.+?)\|'), r'<var>\1</var>'),
                              (re.compile(r'\b(integer|double|float|char|'
                                          r'Boolean|rect)(s?)\b'),
                               r'<keyword>\1</keyword>\2'),
                              (re.compile(r'\b(True|False|None)\b'),
                               r'<const>\1</const>'),
                              (re.compile('`(.+?)`'), r'<mono>\1</mono>'),
               (re.compile(r'\n[\t ]+'), ' '), # Extraneous whitespace
               (re.compile(r'^ ', re.M), '\n'), # Intentional linebreaks
                              ]
    format_comment.code_regex = re.compile(r'{%(.*?)%}', re.DOTALL)

    formatted = escape_for_xml(comment.strip())
    formatted = sub_all_excluding_regex(formatted,
                                        format_comment.needles,
                                        format_comment.code_regex)
    formatted = format_comment.code_regex.sub(format_code_repl, formatted)
    return formatted

def sub_all_excluding_regex(haystack, needles, exclude_regex):
    """
    Returns the string obtained by replacing each occurrence of regex in each
    (regex, repl) pair of "needles" not matched by "exclude_regex".

    Arguments:
        "haystack": The string to be searched.
        "needles": A list of tuples (regex, repl), where "regex" is a
                   RegexObject, and "repl" is a string to be passed
                   to re.sub().
        "exclude_regex": A RegexObject wherein nothing is to be replaced.

    This could surely be more efficient, but it's fast enough for what
    I'm doing.
    """
    excluded_ranges = []
    def rebuild_excluded_ranged(str):
        global excluded_ranges
        excluded_ranges = [m.span() for m in exclude_regex.finditer(str)]
    def in_exclude_range(x):
        """Returns True if x is within the range matched by exclude_regex."""
        for min, max in excluded_ranges:
            if x <= max:
                return x >= min
        return False

    new_haystack = haystack
    rebuild_excluded_ranged(new_haystack)
    for regex, repl in needles:
        start = 0
        while True:
            # Note that regex.finditer() doesn't work here because we are
            # modifying the haystack as we go along.
            match = regex.search(new_haystack, start)

            if match is None:
                break
            elif not in_exclude_range(match.start()):
                new_str = regex.sub(repl, match.group(0), 1)
                new_haystack = replace_range(new_haystack,
                                             match.start(), match.end(),
                                             new_str)
                start = match.start() + len(new_str) + 1

                # The string has been updated, so we need to rebuild our
                # search index.
                rebuild_excluded_ranged(new_haystack)
            else:
                start = match.end()
    return new_haystack

def parse_args(comment):
    """
    Returns dictionary of formatted arguments, where the arguments are in the
    format:
        "Arguments: |foo| => some type,
                    |bar| => some other type"
    """
    parse_args.regex = re.compile(r'\|(.+?)\| =>\s+(.+?)(,$|\Z)', re.S | re.M)
    args = {}
    for match in parse_args.regex.finditer(comment):
        args[match.group(1)] = format_comment(match.group(2))
    return args

def parse_exceptions(comment):
    """
    Returns dictionary of formatted exceptions, where exceptions are in the
    format:
        "Raises: |Exception| if some reason or another,
                 |SomeOtherException| if that other reason."
    (note that the "if" is required, and the period is optional.)
    """
    parse_exceptions.regex = re.compile(r'\|(.+?)\|\s+if\s+(.+?)(,$|.?\Z)',
                                        re.S | re.M)
    exceptions = {}
    for match in parse_exceptions.regex.finditer(comment):
        exceptions[match.group(1)] = format_comment(match.group(2))
    return exceptions

def remove_extra_whitespace(str):
    return re.sub(r'\s{2,}', ' ', str)

def parse_functions(comments):
    """Parses all the function comments in a module."""
    parse_functions.syntax_regex = \
            re.compile(r'Syntax:\s*((\S+)\(.*?\))( => (.*))?', re.DOTALL)
    functions = []
    parsing_function = False
    for comment in comments:
        if comment.startswith('Syntax:'): # Must be given first.
            parsing_function = True
            function = {}
            functions.append(function)

            match = parse_functions.syntax_regex.match(comment)
            if not match or not match.group(1):
                raise SyntaxError('Comment "%s" started with "Syntax:" but '\
                                  "didn't follow with function." % comment)

            function['name'] = match.group(2)
            function['syntax'] = remove_extra_whitespace(match.group(1))
            function['return'] = format_comment(match.group(4)
                                                if match.group(4) else "None")
        elif parsing_function:
            if comment.startswith('Arguments:'):
                function['args'] = parse_args(comment)
            elif comment.startswith('Description:'):
                function['description'] = format_comment(comment[12:])
            elif comment.startswith('Raises: '):
                function['exceptions'] = parse_exceptions(comment)
                parsing_function = False
            else:
                parsing_function = False
    return functions

def parse_header(comments):
    """Parse header comments (attributes describing module)."""
    attributes = {}
    for comment in comments:
        if comment.startswith('Summary:'):
            attributes['summary'] = format_comment(comment[8:])
        elif comment.startswith('Description:'):
            attributes['description'] = format_comment(comment[12:])
    return attributes

def get_module_attributes(comments):
    """
    Returns dictionary of module and class attributes from a dictionary of
    comments and filenames.
    """
    modules = {}
    for key in comments:
        try:
            match = re.search('(.*-(.*?)-module|py-(.*?-class))', key)
            module_name = match.group(2) if match.group(2) else match.group(3)
        except AttributeError:
            raise SyntaxError("Invalid module name (this shouldn't happen!): "
                              '"%s"' % key)

        if key.endswith('.c'):
            module = modules.setdefault(module_name, {})
            module['functions'] = parse_functions(comments[key])
        elif key.endswith('.h'):
            attributes = parse_header(comments[key])
            modules.setdefault(module_name, {}).update(attributes)
    return modules

def create_mmm_file(name, module):
    """
    Returns string describing an "MMM" psuedo-XML file using a module
    attributes dictionary.
    """
    def insert_function_section(xml, function):
        xml.push_tag('function', [('name', function['name'])]) # <function>
        xml.insert_tag('syntax', text=function['syntax'])

        for tagname in ['description']:
            if function.has_key(tagname):
                xml.insert_tag(tagname, text=function[tagname])

        if function.has_key('exceptions'):
            xml.push_tag('exceptions') # <exceptions>

            exceptions = function['exceptions']
            for exception_name in exceptions:
                xml.insert_tag('exception', [('name', exception_name)],
                               text=exceptions[exception_name])

            xml.pop_tag() # </exceptions>

        xml.pop_tag() # </function>

    xml = XMLGen('<?xml version="1.0" encoding="UTF-8"?>')
    xml.push_tag('mmm',
                 [('type', 'class' if 'class' in name else 'module')]) # <mmm>
    xml.insert_tag('name', text=name) # <name> ... </name>

    for tagname in 'summary', 'description':
        if module.has_key(tagname):
            xml.insert_tag(tagname, text=module[tagname])

    if module.has_key('functions'):
        xml.push_tag('section', [('name', 'Functions')]) # <section>
        for function in module['functions']:
            insert_function_section(xml, function)
        xml.pop_tag() # </section>

    xml.pop_tag() # </mmm>
    return xml.str

def update_mmm_files(dir, modules):
    """
    Creates MMM files if they do not exist, and returns count of files written.
    """
    if not os.path.exists(dir):
        os.mkdir(dir)

    for module in modules:
        fpath = os.path.join(dir, module + '.mmm')
        f = open(fpath, 'r')

        f = open(fpath, 'w')
        f.write(create_mmm_file(module, modules[module]))
        f.close()

    return len(modules)

def main(src_dir, out_dir):
    comments = get_comments(braceglob(os.path.join(src_dir,
                                      '{autopy-*-module,py-*-class}*.{c,h}')))
    modules = get_module_attributes(comments)
    files_written = update_mmm_files(out_dir, modules)

    if files_written:
        print '%d files written in "%s"' % (files_written, out_dir)
    else:
        print 'Uh... nothing happened.'

if __name__ == '__main__':
    main(argv[1] if len(argv) > 1 else '../src',
         argv[2] if len(argv) > 2 else './mmm!')
