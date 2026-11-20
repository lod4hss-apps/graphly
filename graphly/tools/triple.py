from typing import Any, List, Optional, Tuple
from graphly.tools.uri import prepare


def prepare_triple(
    triple: Tuple[Any, Any, Any], prefixes_names: Optional[List[str]] = None
) -> str:
    """
    Prepare an RDF triple for SPARQL insertion by converting its elements to valid URIs or literals.

    Args:
        triple (Tuple[int | float | complex | str, int | float | complex | str, int | float | complex | str]): 
            A 3-tuple representing the subject, predicate, and object of the triple.
        prefixes_names (List[str], optional): List of prefix names to apply when shortening URIs. Defaults to [].

    Returns:
        str: A string representing the RDF triple in SPARQL/N-Triples format, ending with a period.
    """
    if len(triple) != 3:
        raise ValueError("A SPARQL triple must contain exactly three terms")
    if any(term is None for term in triple):
        raise ValueError("A SPARQL triple cannot contain None")

    t1 = prepare(triple[0], prefixes_names)
    t2 = prepare(triple[1], prefixes_names)
    t3 = prepare(triple[2], prefixes_names)
    return f"{t1} {t2} {t3} ."
