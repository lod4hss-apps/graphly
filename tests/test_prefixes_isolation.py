import unittest

from graphly.schema.prefix import Prefix
from graphly.schema.prefixes import Prefixes


class TestPrefixesIsolation(unittest.TestCase):
    def test_default_constructor_does_not_share_state(self):
        first = Prefixes()
        second = Prefixes()

        first.add(Prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"))

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 0)
        self.assertIsNot(first.prefix_list, second.prefix_list)

    def test_constructor_copies_input_list(self):
        source = [Prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")]
        prefixes = Prefixes(source)

        source.append(Prefix("xsd", "http://www.w3.org/2001/XMLSchema#"))

        self.assertEqual(len(prefixes), 1)


if __name__ == "__main__":
    unittest.main()
