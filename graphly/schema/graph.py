from typing import List, Dict
from graphly.schema.sparql import Sparql
from graphly.schema.prefixes import Prefixes
from graphly.tools.uri import prepare


class Graph:
    """
    Represents an RDF graph that can be queried, modified, and serialized via a SPARQL endpoint.

    Attributes:
        sparql (Sparql): The SPARQL client used to execute queries.
        uri (str): The URI of the graph.
        uri_long (str): The expanded URI using provided prefixes, if any.
        sparql_begin (str): Opening clause for SPARQL queries targeting this graph.
        sparql_end (str): Closing clause for SPARQL queries targeting this graph.

    Methods:
        __init__: Initializes the Graph with a SPARQL client, optional URI, and optional prefixes.
        run: Executes a SPARQL query and returns results as a list of dictionaries.
        insert: Inserts one or more RDF triples into the graph.
        delete: Deletes one or more RDF triples from the graph.
        dump_dict: Retrieves all triples from the graph as a list of dictionaries.
        dump_turtle: Serializes all triples in Turtle format with prefixes.
        dump_nquad: Serializes all triples in N-Quads format with optional graph URI.
        upload_turtle: Uploads RDF data in Turtle format to the graph via the SPARQL endpoint.
    """

    sparql: Sparql
    uri: str
    uri_long: str
    prefixes: Prefixes

    sparql_begin: str
    sparql_end: str

    def __init__(
        self, sparql: Sparql, uri: str = None, prefixes: Prefixes = None
    ) -> None:
        """
        Initialize a Graph instance with optional URI and prefixes for SPARQL queries.

        Args:
            sparql (Sparql): The SPARQL client used to execute queries.
            uri (str, optional): The URI of the graph. Defaults to None.
            prefixes (Prefixes, optional): Prefix mappings to expand or shorten URIs. Defaults to None.

        Attributes:
            sparql (Sparql): The SPARQL client.
            uri (str): The graph URI.
            uri_long (str): The expanded URI using prefixes if provided.
            sparql_begin (str): Opening clause for SPARQL queries targeting this graph.
            sparql_end (str): Closing clause for SPARQL queries targeting this graph.
        """
        self.sparql = sparql
        self.uri = uri
        self.prefixes = prefixes
        if prefixes:
            self.uri_long = prefixes.lengthen(uri)
        else:
            self.uri_long = uri

        self.sparql_begin = (
            "GRAPH " + prepare(self.uri, prefixes.shorts()) + " {" if self.uri else ""
        )
        self.sparql_end = "}" if self.uri else ""

    def run(self, text: str, prefixes: Prefixes = None) -> List[Dict]:
        """
        Executes a SPARQL query on this graph using the associated SPARQL endpoint.

        Args:
            text (str): The raw SPARQL query string.

        Returns:
            List[Dict]: The parsed results of the query as a list of dictionaries.
        """
        return self.sparql.run(text, self.prefixes if prefixes is None else prefixes)

    def insert(
        self,
        triples: List[tuple[str, str, str]] | tuple[str, str, str],
        prefixes: Prefixes = None,
    ) -> None:
        """
        Inserts one or more RDF triples into this graph using the associated SPARQL endpoint.

        Args:
            triples (List[tuple[str, str, str]] | tuple[str, str, str]): A single triple or a list of triples to insert.

        Returns:
            None
        """
        if len(triples) != 0:
            self.sparql.insert(
                triples, self.uri, self.prefixes if prefixes is None else prefixes
            )

    def delete(
        self,
        triples: List[tuple[str, str, str]] | tuple[str, str, str],
        prefixes: Prefixes = None,
    ) -> None:
        """
        Deletes one or more RDF triples from this graph using the associated SPARQL endpoint.

        Args:
            triples (List[tuple[str, str, str]] | tuple[str, str, str]): A single triple or a list of triples to delete.

        Returns:
            None
        """
        if len(triples) != 0:
            self.sparql.delete(
                triples, self.uri, self.prefixes if prefixes is None else prefixes
            )

    def dump_dict(self) -> list[dict]:
        """
        Dumps all triples from this graph as a list of dictionaries.

        The method retrieves triples in batches to handle large datasets.

        Args:

        Returns:
            list[dict]: A list of dictionaries, each representing a triple with keys 's', 'p', and 'o'.
        """
        # Prepare the queries
        step = 5000
        result = []
        offset = 0
        query = f"""
            # graphly.schema.graph.dump
            SELECT 
                ?s ?p ?o 
                ?s_is_blank ?o_is_blank
            WHERE {{ 
                {self.sparql_begin} 
                    ?s ?p ?o . 
                    BIND(isBlank(?s) as ?s_is_blank)
                    BIND(isBlank(?o) as ?o_is_blank)
                {self.sparql_end} 
            }}
            LIMIT {step}
        """

        # Extract triples as long as they are coming
        while True:
            query_ = query + f"    OFFSET {offset}"  # Append the offset
            local_result = self.run(query_)  # Run the query

            # If there are results, add them, and prepare next request, otherwise, everything is extracted
            if len(local_result) > 0:
                result += local_result
                offset += step
            else:
                break

        return result

    def dump_turtle(self) -> str:
        """
        Dumps all triples from this graph in Turtle serialization format.

        Args:

        Returns:
            str: The RDF data serialized in Turtle format, including prefixes.
        """
        # Get all the triples
        triples = self.dump_dict()

        # Format prefixes for turtle file
        content = (
            "\n".join(list(map(lambda prefix: prefix.to_turtle(), self.prefixes)))
            + "\n\n"
        )

        # Build the output: add all triples
        for triple in triples:
            # Need to save blank nodes correctly
            subj = str(triple["s"])
            obj = triple["o"]

            if subj.startswith("_:"):
                s = subj
            elif triple["s_is_blank"] == "true":
                s = f"_:{subj}"
            else:
                s = prepare(subj, self.prefixes.shorts())

            p = prepare(str(triple["p"]), self.prefixes.shorts())

            obj_str = str(obj)
            if obj_str.startswith("_:"):
                o = obj_str
            elif triple["o_is_blank"] == "true":
                o = f"_:{obj_str}"
            else:
                o = prepare(obj, self.prefixes.shorts())

            content += f"{s} {p} {o} .\n"

        return content

    def dump_nquad(self) -> str:
        """
        Dumps all triples from this graph in N-Quads serialization format.

        Args:

        Returns:
            str: The RDF data serialized in N-Quads format, including the graph URI if defined.
        """
        # Get all the triples
        triples = self.dump_dict()

        # Build the output: add all quads
        graph_uri = prepare(self.prefixes.lengthen(self.uri)) + " " if self.uri else ""
        content = ""
        for triple in triples:
            # Need to save blank nodes correctly
            subj = str(triple["s"])
            if subj.startswith("_:"):
                s = subj
            elif triple["s_is_blank"] == "true":
                s = f"_:{subj}"
            else:
                s = prepare(self.prefixes.lengthen(subj))

            p = prepare(self.prefixes.lengthen(triple["p"]))

            # Need to save blank nodes correctly
            if str(triple["o"]).startswith("_:"):
                o = triple["o"]
            elif triple["o_is_blank"] == "true":
                o = f"_:{triple['o']}"
            else:
                o = prepare(self.prefixes.lengthen(triple["o"]))

            content += f"{s} {p} {o} {graph_uri}.\n"

        return content

    def upload_turtle(self, turtle_content: str) -> None:
        """
        Upload RDF data in Turtle format to the graph via the SPARQL endpoint.

        Args:
            turtle_content (str): The RDF data serialized in Turtle format.

        Returns:
            None
        """
        return self.sparql.upload_turtle(turtle_content, self.uri_long)
