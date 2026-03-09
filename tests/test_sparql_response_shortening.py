import unittest

from graphly.schema.prefix import Prefix
from graphly.schema.prefixes import Prefixes
from graphly.schema.sparql import parse_sparql_json_response
from graphly.tools.uri import prepare


class TestSparqlResponseShortening(unittest.TestCase):
    def test_parse_response_keeps_full_uri_when_local_part_is_not_sparql_safe(self):
        prefixes = Prefixes([Prefix("base", "https://lod4hss.org/resource/")])
        response = {
            "results": {
                "bindings": [
                    {
                        "uri": {
                            "type": "uri",
                            "value": "https://lod4hss.org/resource/type/quantifiable-quality/capacite-lits",
                        }
                    }
                ]
            }
        }

        parsed = parse_sparql_json_response(response, prefixes)

        self.assertEqual(
            parsed[0]["uri"],
            "https://lod4hss.org/resource/type/quantifiable-quality/capacite-lits",
        )
        self.assertEqual(
            prepare(parsed[0]["uri"], prefixes.shorts()),
            "<https://lod4hss.org/resource/type/quantifiable-quality/capacite-lits>",
        )


if __name__ == "__main__":
    unittest.main()
