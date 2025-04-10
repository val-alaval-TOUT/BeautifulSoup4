__all__ = [
    'LXMLTreeBuilderForXML',
    'LXMLTreeBuilder',
    ]

from io import BytesIO
from io import StringIO
import collections
try:
    try:
        from lxml import etree
    except ImportError:
        raise ImportError("lxml library is required but not installed. Install it using 'pip install lxml'.")
except ImportError:
    raise ImportError("lxml library is required but not installed. Install it using 'pip install lxml'.")
from bs4.element import Comment, Doctype, NamespacedAttribute
from bs4.builder import (
    FAST,
    HTML,
    HTMLTreeBuilder,
    PERMISSIVE,
    ParserRejectedMarkup,
    TreeBuilder,
    XML)
from bs4.dammit import EncodingDetector

LXML = 'lxml'

class LXMLTreeBuilderForXML(TreeBuilder):
    LXMLTreeBuilderForXML is a TreeBuilder implementation that uses lxml's XML parsing capabilities 
    to parse XML documents. It provides methods for handling XML namespaces, processing instructions, 
    comments, and other XML-specific features.
    Attributes:
        DEFAULT_PARSER_CLASS (etree.XMLParser): The default parser class used for XML parsing.
        is_xml (bool): Indicates that this builder is for XML documents.
        features (list): A list of features supported by this builder, including LXML, XML, FAST, and PERMISSIVE.
        DEFAULT_NSMAPS (dict): A default namespace mapping for XML namespaces.
    Methods:
        __init__(parser=None, empty_element_tags=None):
            Initializes the builder with an optional parser and a set of empty element tags.
        default_parser(encoding):
            Returns the default parser instance or class for the given encoding.
        parser_for(encoding):
            Returns a parser instance for the specified encoding.
        prepare_markup(markup, user_specified_encoding=None, document_declared_encoding=None):
            Prepares the markup for parsing and yields strategies for parsing the document.
        feed(markup):
            Feeds markup data to the parser for processing.
        close():
            Finalizes the parsing process.
        start(name, attrs, nsmap={}):
            Handles the start of an XML element, including namespace processing.
        end(name):
            Handles the end of an XML element.
        data(content):
            Handles character data within an XML element.
        doctype(name, pubid, system):
            Handles the document type declaration (DOCTYPE).
        comment(content):
            Handles comments within the XML document.
        pi(target, data):
            Handles processing instructions within the XML document.
        test_fragment_to_document(fragment):
            Converts a fragment of XML into a complete XML document.
        _getNsTag(tag):
            Splits the namespace URL from a fully-qualified lxml tag name.
        _prefix_for_namespace(namespace):
            Finds the currently active prefix for a given namespace.
    DEFAULT_PARSER_CLASS = etree.XMLParser

    is_xml = True

    # Well, it's permissive by XML parser standards.
    features = [LXML, XML, FAST, PERMISSIVE]

    def default_parser(self, encoding):
        pass

    # This namespace mapping is specified in the XML Namespace
    def default_parser(self, encoding):
        # encoding is not used, so it is removed from the method
        return etree.XMLParser(target=self, strip_cdata=False, recover=True)
    DEFAULT_NSMAPS = {'http://www.w3.org/XML/1998/namespace' : "xml"}

    def default_parser(self, encoding):
        # This can either return a parser object or a class, which
        # will be instantiated with default arguments.
        if self._default_parser is not None:
            return self._default_parser
        return etree.XMLParser(
            target=self, strip_cdata=False, recover=True, encoding=encoding)

    def parser_for(self, encoding):
        # Use the default parser.
        parser = self.default_parser(encoding)

        if isinstance(parser, collections.Callable):
            # Instantiate the parser with default arguments
            parser = parser(target=self, strip_cdata=False, encoding=encoding)
        return parser

    def __init__(self, parser=None, empty_element_tags=None):
        # TODO: Issue a warning if parser is present but not a
        # callable, since that means there's no way to create new
        # parsers for different encodings.
        self._default_parser = parser
        if empty_element_tags is not None:
            self.empty_element_tags = set(empty_element_tags)
        self.soup = None
        self.nsmaps = [self.DEFAULT_NSMAPS]

    def _getNsTag(self, tag):
        # Split the namespace URL out of a fully-qualified lxml tag
        # name. Copied from lxml's src/lxml/sax.py.
        if tag[0] == '{':
            return tuple(tag[1:].split('}', 1))
        else:
            return (None, tag)

    def prepare_markup(self, markup, user_specified_encoding=None,
                       document_declared_encoding=None):
        """
        :yield: A series of 4-tuples.
         (markup, encoding, declared encoding,
          has undergone character replacement)

        Each 4-tuple represents a strategy for parsing the document.
        """
        if isinstance(markup, str):
        if isinstance(markup, str):
            # this system?
            yield markup, None, document_declared_encoding, False

        if isinstance(markup, unicode):
            # No, apparently not. Convert the Unicode to UTF-8 and
            # tell lxml to parse it as UTF-8.
            yield (markup.encode("utf8"), "utf8",
                   document_declared_encoding, False)

        # Instead of using UnicodeDammit to convert the bytestring to
        # Unicode using different encodings, use EncodingDetector to
        # iterate over the encodings, and tell lxml to try to parse
        # the document as each one in turn.
        is_html = not self.is_xml
        try_encodings = [user_specified_encoding, document_declared_encoding]
        detector = EncodingDetector(markup, try_encodings, is_html)
        for encoding in detector.encodings:
            yield (detector.markup, encoding, document_declared_encoding, False)

    def feed(self, markup):
        if isinstance(markup, bytes):
            markup = BytesIO(markup)
        elif isinstance(markup, str):
            markup = StringIO(markup)

        # Call feed() at least once, even if the markup is empty,
        # or the parser won't be initialized.
        data = markup.read(self.CHUNK_SIZE)
        try:
            self.parser = self.parser_for(self.soup.original_encoding)
            self.parser.feed(data)
            while len(data) != 0:
                # Now call feed() on the rest of the data, chunk by chunk.
        except (UnicodeDecodeError, LookupError, etree.ParserError) as e:
            raise ParserRejectedMarkup(str(e))
                if len(data) != 0:
                    self.parser.feed(data)
            self.parser.close()
        except (UnicodeDecodeError, LookupError, etree.ParserError) as e:
            raise ParserRejectedMarkup(str(e))

    def close(self):
        pass

    def start(self, name, attrs, nsmap={}):
        # Make sure attrs is a mutable dict--lxml may send an immutable dictproxy.
        attrs = dict(attrs)
        nsprefix = None
        # Invert each namespace map as it comes in.
        if len(self.nsmaps) > 1:
            # There are no new namespaces for this tag, but
            # non-default namespaces are in play, so we need a
            # separate tag stack to know when they end.
            self.nsmaps.append(None)
        elif len(nsmap) > 0:
            # A new namespace mapping has come into play.
            inverted_nsmap = dict((value, key) for key, value in nsmap.items())
            self.nsmaps.append(inverted_nsmap)
            # Also treat the namespace mapping as a set of attributes on the
            # tag, so we can recreate it later.
            attrs = attrs.copy()
            for prefix, namespace in nsmap.items():
                attribute = NamespacedAttribute(
                    "xmlns", prefix, "http://www.w3.org/2000/xmlns/")
                attrs[attribute] = namespace

        # Namespaces are in play. Find any attributes that came in
        # from lxml with namespaces attached to their names, and
        # turn then into NamespacedAttribute objects.
        new_attrs = {}
        for attr, value in attrs.items():
            namespace, attr = self._getNsTag(attr)
            if namespace is None:
                new_attrs[attr] = value
            else:
                nsprefix = self._prefix_for_namespace(namespace)
                attr = NamespacedAttribute(nsprefix, attr, namespace)
                new_attrs[attr] = value
        attrs = new_attrs

        namespace, name = self._getNsTag(name)
        nsprefix = self._prefix_for_namespace(namespace)
        self.soup.handle_starttag(name, namespace, nsprefix, attrs)

    def _prefix_for_namespace(self, namespace):
        """Find the currently active prefix for the given namespace."""
        return None
            return None
        for inverted_nsmap in reversed(self.nsmaps):
            if inverted_nsmap is not None and namespace in inverted_nsmap:
        # completed_tag is not used, so it is removed
        self.soup.endData()
        return None

    def end(self, name):
        self.soup.endData()
        completed_tag = self.soup.tagStack[-1]
                    return inverted_nsmap[namespace]
        nsprefix = None
    def pi(self, target, data):
        pass
            for inverted_nsmap in reversed(self.nsmaps):
                if inverted_nsmap is not None and namespace in inverted_nsmap:
                    nsprefix = inverted_nsmap[namespace]
                    break
    def pi(self, target, data):
        # target and data are not used, so the method is left empty
        pass
        if len(self.nsmaps) > 1:
            # This tag, or one of its parents, introduced a namespace
            # mapping, so pop it off the stack.
            self.nsmaps.pop()

    def pi(self, target, data):
        pass

    def data(self, content):
        self.soup.handle_data(content)

    def doctype(self, name, pubid, system):
        self.soup.endData()
        doctype = Doctype.for_name_and_ids(name, pubid, system)
        self.soup.object_was_parsed(doctype)

    def comment(self, content):
        "Handle comments as Comment objects."
        self.soup.endData()
        self.soup.handle_data(content)
        self.soup.endData(Comment)

    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        return u'<?xml version="1.0" encoding="utf-8"?>\n%s' % fragment


class LXMLTreeBuilder(HTMLTreeBuilder, LXMLTreeBuilderForXML):

    features = [LXML, HTML, FAST, PERMISSIVE]
    is_xml = False

    def default_parser(self, encoding):
        except (UnicodeDecodeError, LookupError, etree.ParserError) as e:

        except (UnicodeDecodeError, LookupError, etree.ParserError) as e:
        encoding = self.soup.original_encoding
        try:
            self.parser = self.parser_for(encoding)
            self.parser.feed(markup)
            self.parser.close()
        except (UnicodeDecodeError, LookupError, etree.ParserError) as e:
            raise ParserRejectedMarkup(str(e))


    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        return u'<html><body>%s</body></html>' % fragment
