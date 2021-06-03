from xml.sax import *
from xml.sax.handler import ContentHandler
from typing import List, Dict, Callable
import sys
import re
import click

class Element:
    """Just like DOM element except it only knows about ancestors"""

    ## XML tag name
    # name: str

    ## parent element
    # parent: Element

    ## attributes. 'Attributes' class doesn't seem to exist
    # attrs: object

    ## tags captured at this context
    # tags: Dict[str,object]

    def __init__(self, parent: 'Element', name: str, attrs):
        self.name = name
        self.attrs = attrs
        self.parent = parent
        # start with a copy of parents, and we modify it with ours
        self.tags = parent.tags.copy() if parent else dict()    # type: Dict[str,object]

    def __str__(self):
        return "%s %s" % (self.name, self.tags)

class TagMatcher:
    """Matches to an attribute of an XML element and captures its value as a 'tag' """

    ## XML tag name to match
    # element: str
    ## XML attribute name to match
    # attr: str

    ## Name of the variable to capture
    # var: str

    def __init__(self, element: str, attr: str, var: str):
        self.element = element
        self.attr = attr
        self.var = var

    def matches(self, e: Element) -> str:
        return e.attrs.get(self.attr) if self.element==e.name or self.element=="*" else None

    @staticmethod
    def parse(spec :str) -> 'TagMatcher':
        """Parse a string like foo/@bar={zot}"""
        m = re.match(r"(\w+|\*)/@([a-zA-Z_\-]+)={(\w+)}", spec)
        if m:
            return TagMatcher(m.group(1), m.group(2), m.group(3))
        else:
            raise click.BadParameter("Invalid tag spec: %s"%spec)

class SaxParser(ContentHandler):
    """
    Parse XML in a streaming manner, capturing attribute values as specified by TagMatchers
    """

    ## represents the current element
    context = None  # type: Element

    # matchers: List[TagMatcher]

    # receiver: Callable[[Element],None]

    def __init__(self, matchers: List[TagMatcher], receiver: Callable[[Element],None]):
        super().__init__()
        self.matchers = matchers
        self.receiver = receiver

    def startElement(self, tag, attrs):
        self.context = Element(self.context, tag, attrs)

        # match tags at this element
        for m in self.matchers:
            v = m.matches(self.context)
            if v!=None:
                self.context.tags[m.var] = v

        # yield is more Pythonesque but because this is called from SAX parser
        # I'm assuming that won't work
        self.receiver(self.context)

    def endElement(self, tag):
        self.context = self.context.parent

    def parse(self, body):
        p = make_parser()
        p.setContentHandler(self)
        p.parse(body)


# Scaffold JUnit parser
# python -m launchable.utils.sax < result.xml
if __name__ == "__main__":
    def print_test_case(e: Element):
        if e.name=="testcase":
            print(e)

    SaxParser([
        TagMatcher.parse("testcase/@name={testcaseName}"),
        TagMatcher.parse("testsuite/@timestamp={timestamp}")
    ], print_test_case).parse(sys.stdin)
