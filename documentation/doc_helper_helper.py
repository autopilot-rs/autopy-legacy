#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Another script that generates HTML files from MMM files created by
doc_helper.py (or edited by hand).
"""
import os
import re
import textwrap

from sys import argv
from XMLGen import XMLGen
from lxml import etree
from tidylib import tidy_document

def readfile(path):
    """Convenience function that returns the contents of a file as a string."""
    f = open(path, 'r')
    str = f.read()
    f.close()
    return str

def render_tag_contents(tag):
    """
    Renders the contents inside of (but not including) an lxml tag.
    Rougly equivalent to BeautifulSoup's renderContents() method.
    TODO: Surely there is a safe lxml built-in for this...
    """
    tagname = tag.tag
    return re.sub('</%s>\s*$' % tagname, '',
                  re.sub(r'^<%s(\s+\w+=".*?")*?>' % tagname,
                         '', etree.tostring(tag))).strip()

def attrs_from_mmm(mmm):
    """Returns dictionary of attributes from MMM file."""
    def convert_tags(tree):
        """Converts MMM attribute tags into their associated HTML tags."""
        for tagname in 'keyword', 'const', 'var', 'mono':
            for element in tree.iterfind('.//' + tagname):
                element.tag = 'tt'
                element.set('class', tagname)

        for element in tree.iterfind('.//bcode'):
            element.tag = 'pre'

        for element in tree.iterfind('.//note'):
            element.tag = 'p'
            element.insert(0, '<span class="note-title">Note:</span>')
            element.set('class', 'note')
    def add_links(tree, function_names):
        """Adds links to given functions where referenced."""
        add_links.regex = re.compile(r'\S+(?=\()')
        for element in tree.iterfind(".//tt[@class='mono']"):
            func = add_links.regex.match(element.text)

            if func and func.group(0) in function_names:
                # Wrap the tag in a link.
                child = etree.SubElement(element, 'a',
                                         {'href': '#' + func.group(0)})
                child.text = element.text
                element.text = ''
    def function_attributes(syntax):
        """
        Returns tuple of the name and arguments of a function extracted from a
        syntax tag's string, in the format "function(arg, ...)".

        Returns '', () if syntax is invalid.
        """
        function_attributes.regex = re.compile(r'(\S+)\((.*?)\)')
        synmatch = function_attributes.regex.match(syntax)

        if not synmatch or not synmatch.group(1):
            return '', ()

        name = synmatch.group(1)
        if synmatch.group(2):
            return name, (arg.strip() for arg in synmatch.group(2).split(','))
        return name, ()
    def get_functions(section):
        """
        Returns dictionary of function names and attributes in given section.

        Raises SyntaxError if no <syntax> tag is given, or the <syntax> tag is
        of invalid syntax.
        """
        functions = {}
        for element in section.iterfind('function'):
            syntax = element.find('syntax')
            if syntax is None:
                raise SyntaxError('Missing required <syntax> tag in "%s"' %
                                  render_tag_contents(element))

            # Extract name and arguments from syntax tag.
            name, args = function_attributes(syntax.text)
            if not name:
                raise SyntaxError('<syntax> tag has invalid syntax'
                                  '(how ironic!) "%s"' % syntax.text)
            function = functions[name] = {}

            # Add arguments as an array iff they are given.
            if args:
                function['args'] = args

            description = element.find('description')
            if description is not None:
                function['description'] = render_tag_contents(description)

            exceptions_tag = element.find('exceptions')
            if exceptions_tag is not None:
                exceptions = function['exceptions'] = {}
                for exception_tag in exceptions_tag.iterfind('exception'):
                    name = exception_tag.get('name')
                    exceptions[name] = render_tag_contents(exception_tag)

            no_class = element.get('class') == "NO"
            if no_class:
                function['class'] = False
        return functions
    def get_constants(section):
        """
        Returns dictionary of constant names and attributes in given section.

        Raises SyntaxError if <constant> has invalid syntax.
        """
        constants = {}
        for element in section.iterfind('constant'):
            name = element.get('name')
            if name is None:
                raise SyntaxError('<constant> tag missing "name" attribute' %
                                  render_tag_contents(element))
            constant = constants[name] = {}

            description = element.find('description')
            if description is not None:
                constant['description'] = render_tag_contents(description)

            value = element.find('value')
            if value is not None:
                constant['value'] = render_tag_contents(value)

        return constants
    def get_modules(section):
        """Returns list of module names in given section."""
        return [module.get('name') for module in section.iterfind('module')]

    tree = etree.XML(mmm)

    # Convert MMM tags to HTML attributes.
    convert_tags(tree)

    # Add hyperlinks to function references.
    functions = [function.get('name')
                 for function in tree.iterfind('*//function')]
    add_links(tree, functions)

    attributes = {'type': tree.get('type')}
    for tagname in 'name', 'summary', 'description':
        element = tree.find(tagname)
        if element is not None:
            attributes[tagname] = render_tag_contents(element)

    for section_tag in tree.iterfind('section'):
        sections = attributes.setdefault('sections', {})
        name = section_tag.get('name')
        if name:
            section = sections[name] = {}

            if section_tag.find('function') is not None:
                section['functions'] = get_functions(section_tag)

            description_tag = section_tag.find('description')
            if description_tag is not None:
                section['description'] = render_tag_contents(description_tag)

            if section_tag.find('constant') is not None:
                section['constants'] = get_constants(section_tag)

            # Only relevant for the index file.
            if section_tag.find('module') is not None:
                section['modules'] = get_modules(section_tag)
        else:
            raise SyntaxError('<section> tag requires name parameter')

    return attributes

def html_from_mmm(mmm_attrs, add_header_func=None, add_footer_func=None):
    """Returns valid XHTML page from given attributes."""
    def anchor(str):
        return str.replace(' ', '_')
    def header_link(anchor):
        """Returns header permalink string for given anchor."""
        return '<a href="#%s" class="headerlink" ' \
                  'title="Permalink to this headline">&#182;</a>' % anchor
    def parse_section_outline(doc, section, section_name, is_index_page=False):
        doc.push_tag('ul') # <ul>
        doc.push_tag('li') # <li>
        doc.insert_link(section_name, '#' + anchor(section_name))
        doc.push_tag('ul') # <ul>

        for subsection_name in section:
            if subsection_name == 'description': continue

            for subsubsection_name in section[subsection_name]:
                doc.push_tag('li') # <li>
                doc.insert_link(subsubsection_name,
                                subsubsection_name + '.html' if is_index_page
                                else '#' + anchor(subsubsection_name))
                doc.pop_tag() # </li>

        doc.pop_tag() # </ul>
        doc.pop_tag() # </li>
        doc.pop_tag() # </ul>
    def parse_section_contents(doc, module_name, section, section_name,
                               is_index_page=False):
        # <h2 id="section_name"> ... </h2>
        section_id = anchor(section_name)
        doc.insert_tag('h2', [('id', section_id)],
                       text=section_name.title() + header_link(section_id))

        doc.push_tag('dl', [('class', 'section')]) # <dl>

        if section.has_key('description'):
            doc.push_tag('dd') # <dd>
            doc.insert_paragraphs(section['description'])
            doc.pop_tag() # </dd>

        if is_index_page and section.has_key('modules'):
            parse_module_list(doc, section['modules'])

        if section.has_key('functions'):
            parse_functions_contents(doc, module_name, section['functions'])
        if section.has_key('constants'):
            parse_constants_contents(doc, module_name, section['constants'])

        doc.pop_tag() # </dl>
    def parse_functions_contents(doc, module_name, functions):
        def html_for_function(module_name, function, arguments):
            """Returns string of HTML for given function and attributes."""
            args = ", ".join(['<span class="funcarg">%s</span>' % arg
                             for arg in arguments])
            class_tag = '<tt class="class-name">%s.</tt>' % module_name \
                        if module_name else ''
            return class_tag + \
                   '<tt class="name">%s</tt><big>(</big>%s<big>)</big>%s' \
                   % (function, args, header_link(anchor(function)))
        def parse_exceptions(doc, exceptions):
            doc.insert_tag('div', [('class', 'exceptions-header')],
                           text='Exceptions:')
            doc.push_tag('ul', [('class', 'exceptions')]) # <ul>
            for exception_name in exceptions:
                text = "%s is thrown if %s." % \
                        (('<tt class="var">%s</tt>') % exception_name,
                         exceptions[exception_name])
                doc.insert_tag('li', text=text) # <li> ... </li>
            doc.pop_tag() # </ul>

        class_name = module_name
        for function_name in functions:
            function = functions[function_name]

            # <dt> ... </dt>
            class_name = module_name if not function.has_key('class') or \
                                        function['class'] \
                                     else ''
            doc.insert_tag('dt', [('class', 'function'),
                                  ('id', anchor(function_name))],
                           text=html_for_function(class_name,
                                                  function_name,
                                                  function.get('args', [])))
            if function.has_key('description'):
                doc.push_tag('dd') # <dd>
                doc.insert_paragraphs(function['description'])

                if function.has_key('exceptions'):
                    parse_exceptions(doc, function['exceptions'])

                doc.pop_tag() # </dd>
    def parse_constants_contents(doc, module_name, constants):
        def html_for_constant(module_name, name):
            class_tag = '<tt class="class-name">%s.</tt>' % module_name \
                        if module_name else ''
            name_id = anchor(name)
            return class_tag + \
                   '<tt class="name">%s</tt>%s' % (name, header_link(name_id))

        for constant_name in constants:
            constant = constants[constant_name]

            # <dt> ... </dt>
            doc.insert_tag('dt', [('class', 'constant'),
                                  ('id', anchor(constant_name))],
                           text=html_for_constant(module_name, constant_name))

            if constant.has_key('description'):
                doc.push_tag('dd', [('class', 'constant')]) # <dd>
                doc.insert_paragraphs(constant['description'])
                doc.pop_tag() # </dd>

    def parse_module_list(doc, modules):
        def html_for_module(name, link):
            return '<a class="module" id="%s" href="%s">%s module</a>' % \
                    (anchor(name), link, name)

        for module_name in modules:
            # <dt> ... </dt>
            doc.insert_tag('dt', text=html_for_module(module_name,
                                                      module_name + '.html'))

    doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n' \
              '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
    doc = XMLGen(doctype)
    doc.push_tag('html', [('xmlns', 'http://www.w3.org/1999/xhtml'),
                          ('xml:lang', 'en')]) # <html>
    doc.push_tag('head') # <head>
    doc.insert_tag('meta', [('http-equiv', 'content-type'),
                           ('content', 'text/html; charsetutf-8')],
                   autoclose=True) # <meta content-type="..." />

    summary = mmm_attrs.get('summary', '')
    if summary:
        doc.insert_tag('meta', [('name', 'description'),
                                ('content', summary)],
                       autoclose=True) # <meta name="description" />

    title = '%s &#8212; %s' % (mmm_attrs['name'], summary)

    doc.insert_tag('title', text=title) # <title> ... </title>

    # Add stylesheet
    doc.insert_tag('link', [('rel', 'stylesheet'),
                            ('href', 'style.css'),
                            ('type', 'text/css'),
                            ('charset', 'utf-8')],
                   autoclose=True) # <link type="text/css" ... />

    doc.pop_tag() # </head>

    doc.push_tag('body') # <body>

    if add_header_func:
        add_header_func(doc)

    doc.push_tag('div', [('id', 'container')]) # <div id="container">

    doc.push_tag('div', [('id', 'sidebar')]) # <div id="sidebar">
    doc.insert_tag('h3', text='Table of Contents') # <h3> ... </h3>

    doc.push_tag('ul') # <ul>

    # <li><a href="#module-name">module-name</a></li>
    title_anchor = anchor("module-%s" % mmm_attrs['name'])
    doc.push_tag('li') # <li>
    doc.insert_link(title, '#' + title_anchor)

    sections = mmm_attrs.get('sections', {})
    is_index = mmm_attrs['type'] == 'index'
    for section_name in sections:
        parse_section_outline(doc, sections[section_name], section_name,
                              is_index_page=is_index)

    doc.pop_tag() # </li>
    doc.pop_tag() # </ul>
    doc.pop_tag() # </div>

    doc.push_tag('div', [('id', 'main')]) # <div id="main">
    doc.insert_tag('h1', [('id', title_anchor)],
                   text=title + header_link(title_anchor)) # <h1> ... </h1>

    if mmm_attrs.has_key('description'):
        doc.push_tag('div', [('class', 'description')])
        doc.insert_paragraphs(mmm_attrs['description'])
        doc.pop_tag()

    module_name = mmm_attrs['name'] if mmm_attrs['type'] == 'module' else ''
    for section_name in sections:
        parse_section_contents(doc, module_name,
                               sections[section_name], section_name,
                               is_index_page=is_index)

    doc.pop_tag() # </div>
    doc.pop_tag() # </div>

    if add_footer_func:
        add_footer_func(doc)

    doc.pop_tag() # </body>
    doc.pop_tag() # </html>

    document, errors = tidy_document(doc.str, {'char-encoding': 'utf8'})
    return document

def add_header(doc, next_file='', prev_file=''):
    """
    Adds header and top navigation links to document.
    """
    doc.push_tag('div', [('id', 'header')]) # <div id="header">

    doc.insert_tag('a', [('href', '#')], text='AutoPy Documentation')
    doc.insert_text(' &#187; ')
    doc.insert_tag('a', [('href', 'index.html')], text='API Reference')

    doc.push_tag('div', [('id', 'nav')])

    if prev_file:
        doc.insert_tag('a', [('href', prev_file)], text='previous')
        doc.insert_text(' | ')

    doc.insert_tag('a', [('href', 'index.html')], text='index')

    if next_file:
        doc.insert_text(' | ')
        doc.insert_tag('a', [('href', next_file)], text='next')

    doc.pop_tag() # </div>
    doc.pop_tag() # </div>

def add_footer(doc):
    pass

def prev_cur_next(lst):
    """
    Returns list of tuples (prev, cur, next) for each item in list, where
    "prev" and "next" are the previous and next items in the list,
    respectively, or None if they do not exist.
    """
    return zip([None] + lst[:-1], lst, lst[1:]) + [(lst[-2], lst[-1], None)]

def main(index_file, out_dir):
    for path in index_file, out_dir:
        if not os.path.exists(path):
            raise IOError('"./%s" does not exist.' % path)

    index_attrs = attrs_from_mmm(readfile(index_file))
    module_names = ['index']
    module_names.extend(index_attrs['sections']['Table of Contents']['modules'])

    # Iterate through modules listed in index file.
    dirname = os.path.abspath(os.path.dirname(index_file))
    paths = [os.path.join(dirname, module_name + '.mmm')
             for module_name in module_names]

    module_iterator = zip(prev_cur_next(module_names), paths)
    for (prev_name, name, next_name), inpath in module_iterator:
        outpath = os.path.join(out_dir, name + '.html')
        f = open(outpath, 'w')

        # Pass new header function based on previous and next module names.
        next_file = next_name + '.html' if next_name else ''
        prev_file = prev_name + '.html' if prev_name else ''
        add_header_func = lambda doc: add_header(doc, next_file, prev_file)

        f.write(html_from_mmm(attrs_from_mmm(readfile(inpath)),
                              add_header_func=add_header_func,
                              add_footer_func=add_footer))
        f.close()

    print '%d files written to "%s"!' % (len(module_names), out_dir)

if __name__ == '__main__':
    main(argv[1] if len(argv) > 1 else './mmm!/index.mmm',
         argv[2] if len(argv) > 2 else './api-reference')
