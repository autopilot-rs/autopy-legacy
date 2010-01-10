"""
The preferred way to use this module is to first:
    from XMLGen import XMLGen,
and then just use the class documented below.
"""

class XMLGen(object):
    """
    Simple class to ease in generating HTML & XML documents.
    Knows nothing about HTML, only tags and attributes.
    """
    def __init__(self, startstr, is_xml=True):
        self.str = startstr
        self._tagstack = []
        self.is_xml = is_xml # Determines whether "/" should be included in
                             # auto-closing tags.
    def push_tag(self, tagname, attrs=[]):
        """
        Pushes given tag onto stack with given attributes.

        "attrs" should be a list of tuples (attribute, value) to be assigned to
        the tag in order, or an empty list [] if none are to be assigned.

        E.g., push_tag("foo", [("id", "baz")]) output '<foo id="baz">'.

        A list of tuples is used instead of a dict in order for the order to
        be preserved.
        """
        tag = '<%s%s>' % (tagname, string_for_attrs(attrs))
        self.str += '\n' + indent(tag, self.indent_level())
        self._tagstack.append(tagname)
    def pop_tag(self, newline=True):
        """Pops tag from stack (and closes it in string)."""
        tag = '</%s>' % self._tagstack.pop()
        if newline:
            tag = '\n' + indent(tag, self.indent_level())
        self.str += tag
    def insert_tag(self, tagname, attrs=[], text="",
                   autoclose=False, newline=False):
        """Immediately inserts tag, autoclosing it if told to."""
        if autoclose:
            self.str += '\n<%s%s%s>' % (tagname, string_for_attrs(attrs),
                                        ' /' if self.is_xml else '')
        else:
            self.push_tag(tagname, attrs)
            if text:
                if newline:
                    self.insert_text('\n' + indent(text, self.indent_level()))
                else:
                    self.insert_text(text)
            self.pop_tag(newline=newline)
    def insert_text(self, text):
        """Inserts (non-indented) text between last pushed tag."""
        self.str += text
    def insert_paragraphs(self, str, ignore_pre=True):
        """
        Convenience method.
        Inserts paragraphs separated by newlines as paragraphs wrapped in
        <p> tags, while silently ignoring content in <pre> tags if ignore_pre
        is True.
        """
        for block in splittag(str, 'pre'):
            if ignore_pre and '<pre>' in block:
                self.insert_text(block)
                if 'Holds down and then' in block:
                    print block
            else:
                self.insert_text('\n'.join('<p>%s</p>' % line
                                 for line in block.splitlines()))
    def insert_link(self, text, href):
        """
        Convenience method.
        Inserts given text wrapped in anchor to the given URL.
        """
        self.insert_text('\n<a href="%s">%s</a>' % (href, text))
    def indent_level(self):
        """Returns current level of indentation inside pushed tags."""
        return len(self._tagstack) - 1
    def __str__(self):
        return self.str

def indent(str, level):
    """
    Returns string where each line is indented by the given level in tabs.
    """
    if level == 0: return str
    return "\n".join("\t" * level + line for line in str.splitlines())

def string_for_attrs(attrs):
    """Returns string describing tag attributes in the order given."""
    if not attrs: return ''
    return ''.join(' %s="%s"' % (attr, value) for attr, value in attrs)

import re
def splittag(str, tagname):
    tag = re.escape(tagname)
    regex = re.compile('(<%s>.*?</%s>)' % (tag, tag), re.DOTALL)
    return regex.split(str)
