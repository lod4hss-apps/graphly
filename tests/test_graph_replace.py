import unittest
from unittest.mock import patch

from graphly.schema import Prefix, Prefixes, Sparql


class TestGraphReplace(unittest.TestCase):
    def test_replace_uses_one_atomic_update(self):
        endpoint = Sparql("http://example.org/sparql", "", "")
        prefixes = Prefixes([Prefix("ex", "http://example.org/")])

        with patch.object(endpoint, "run") as mock_run:
            endpoint.replace(
                [("ex:entity", "ex:label", "old")],
                [("ex:entity", "ex:label", "new")],
                "ex:graph",
                prefixes,
            )

        mock_run.assert_called_once()
        query = mock_run.call_args.args[0]
        self.assertIn("DELETE", query)
        self.assertIn("INSERT", query)
        self.assertIn("GRAPH ex:graph", query)
        self.assertIn("ex:entity ex:label 'old' .", query)
        self.assertIn("ex:entity ex:label 'new' .", query)


if __name__ == "__main__":
    unittest.main()
