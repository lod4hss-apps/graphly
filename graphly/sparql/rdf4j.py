from graphly.sparql.graphdb import GraphDB

class RDF4J(GraphDB):

    def __init__(self, url: str, username: str, password: str, name: str = None) -> None:
        super().__init__(url, username, password, name)
        self.technology_name = "RDF4J"