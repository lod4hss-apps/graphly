import unittest

from graphly.schema.prefix import Prefix


class TestPrefixShorten(unittest.TestCase):
    def test_shorten_valid_local_part(self):
        prefix = Prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(
            prefix.shorten("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            "rdf:type",
        )

    def test_shorten_invalid_local_part_with_slash_keeps_full_uri(self):
        prefix = Prefix("base", "https://lod4hss.org/resource/")
        uri = "https://lod4hss.org/resource/type/quantifiable-quality/capacite-lits"
        self.assertEqual(prefix.shorten(uri), uri)

    def test_shorten_bracketed_uri_still_shortens_when_valid(self):
        prefix = Prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(
            prefix.shorten("<http://www.w3.org/2001/XMLSchema#string>"),
            "xsd:string",
        )

    def test_shorten_does_not_replace_when_prefix_is_only_contained(self):
        prefix = Prefix("base", "https://lod4hss.org/resource/")
        uri = "https://example.org/redirect?target=https://lod4hss.org/resource/type"
        self.assertEqual(prefix.shorten(uri), uri)

    def test_shorten_prefixed_value_stays_stable(self):
        prefix = Prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(prefix.shorten("rdf:type"), "rdf:type")


if __name__ == "__main__":
    unittest.main()
