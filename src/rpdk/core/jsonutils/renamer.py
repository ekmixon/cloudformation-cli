from itertools import count

from jsonschema.compat import urldefrag

from .pointer import fragment_decode


class RefRenamer:
    def __init__(self, renames=None):
        self.renames = renames or {}
        # this generator never completes
        self.names = iter(f"schema{i}" for i in count())

    def items(self):
        """Return all renames.

        >>> r = RefRenamer()
        >>> r.items()
        dict_items([])
        """
        return self.renames.items()

    def parse_ref_url(self, ref):
        """Parse a reference URL into a tuple of base + parts.

        Schemas are renamed for easier processing.

        >>> r = RefRenamer({"file://base.json": "base"})
        >>> sorted(r.items())
        [('file://base.json', 'base')]
        >>> r.parse_ref_url("file://base.json")
        ('base',)
        >>> r.parse_ref_url("file://base.json#/foo/bar")
        ('base', 'foo', 'bar')
        >>> sorted(r.items())
        [('file://base.json', 'base')]
        >>> r.parse_ref_url("file://other.json")
        ('schema0',)
        >>> r.parse_ref_url("file://other.json#/foo/bar")
        ('schema0', 'foo', 'bar')
        >>> sorted(r.items())
        [('file://base.json', 'base'), ('file://other.json', 'schema0')]
        """
        url, fragment = urldefrag(ref)
        try:
            rename = self.renames[url]
        except KeyError:
            self.renames[url] = rename = next(self.names)
        return (rename,) + fragment_decode(fragment, prefix="")
