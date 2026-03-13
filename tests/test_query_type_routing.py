import unittest
from unittest.mock import patch

from graphly.sparql.fuseki import Fuseki
from graphly.sparql.graphdb import GraphDB
from graphly.tools.query import get_sparql_type


class TestGetSparqlType(unittest.TestCase):
    def test_select_without_prefix(self):
        query = "SELECT * WHERE { ?s ?p ?o }"
        self.assertEqual(get_sparql_type(query), "SELECT")

    def test_select_with_standard_prefix(self):
        query = (
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
            "SELECT * WHERE { ?s ?p ?o }"
        )
        self.assertEqual(get_sparql_type(query), "SELECT")

    def test_select_with_hyphenated_prefix(self):
        query = (
            "PREFIX crm-sup: <https://example.org/crm-sup#>\n"
            "SELECT * WHERE { ?s ?p ?o }"
        )
        self.assertEqual(get_sparql_type(query), "SELECT")

    def test_select_with_comment_prefix_spacing_and_case(self):
        query = (
            "  # leading comment\n"
            "\n"
            "  prefix crm-sup: <https://example.org/crm-sup#>\n"
            "\tSeLeCt * WHERE { ?s ?p ?o }"
        )
        self.assertEqual(get_sparql_type(query), "SELECT")


class TestEndpointRouting(unittest.TestCase):
    def test_graphdb_routes_select_with_hyphenated_prefix_to_query(self):
        endpoint = GraphDB("http://example.org/sparql", "", "")
        query = (
            "PREFIX crm-sup: <https://example.org/crm-sup#>\n"
            "SELECT * WHERE { ?s ?p ?o }"
        )

        with patch("graphly.schema.sparql.Sparql.run", return_value=[]) as mock_run:
            endpoint.run(query)

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args[0][2], "query")
        self.assertEqual(mock_run.call_args[0][3], "")
        self.assertTrue(mock_run.call_args[0][4])

    def test_fuseki_routes_select_with_hyphenated_prefix_to_query(self):
        endpoint = Fuseki("http://example.org/sparql", "", "")
        query = (
            "PREFIX crm-sup: <https://example.org/crm-sup#>\n"
            "SELECT * WHERE { ?s ?p ?o }"
        )

        with patch("graphly.schema.sparql.Sparql.run", return_value=[]) as mock_run:
            endpoint.run(query)

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args[0][2], "query")
        self.assertEqual(mock_run.call_args[0][3], "")
        self.assertTrue(mock_run.call_args.kwargs["parse_response"])


if __name__ == "__main__":
    unittest.main()
