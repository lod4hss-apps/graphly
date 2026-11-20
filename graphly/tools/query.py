from typing import Literal, cast
import re


_SUPPORTED_QUERY_TYPES = {"SELECT", "CONSTRUCT", "INSERT", "DELETE", "CLEAR"}
_PREFIX_DECLARATION_PATTERN = re.compile(
    r"^PREFIX\s+(?:[-\w.]+)?\s*:\s*<[^>]*>\s*",
    flags=re.IGNORECASE,
)


def get_sparql_type(
    query: str,
) -> Literal["SELECT", "CONSTRUCT", "INSERT", "DELETE", "CLEAR", "OTHER"]:
    """
    Determine the type of a SPARQL query.

    This function analyzes a SPARQL query string and returns its main operation type.
    It correctly handles leading comments and PREFIX declarations.

    Supported query types:
        - "SELECT"
        - "CONSTRUCT"
        - "INSERT"
        - "DELETE"
        - "CLEAR"
    If the query does not match any of these, it returns "OTHER".

    Args:
        query (str): The SPARQL query string to analyze.

    Returns:
        str: The type of the SPARQL query ("SELECT", "INSERT", "DELETE", "CLEAR", or "OTHER").
    """
    q = query

    # Skip prologue pieces until the first operation keyword:
    # - whitespace / empty lines
    # - line comments
    # - PREFIX declarations
    while True:
        q = q.lstrip()
        if not q:
            return "OTHER"

        if q.startswith("#"):
            newline_index = q.find("\n")
            if newline_index == -1:
                return "OTHER"
            q = q[newline_index + 1 :]
            continue

        prefix_match = _PREFIX_DECLARATION_PATTERN.match(q)
        if prefix_match:
            q = q[prefix_match.end() :]
            continue

        break

    # Get the first keyword
    first_word_match = re.match(r"^([A-Za-z]+)", q, flags=re.IGNORECASE)
    if first_word_match:
        kw = first_word_match.group(1).upper()
        if kw in _SUPPORTED_QUERY_TYPES:
            return cast(Literal["SELECT", "CONSTRUCT", "INSERT", "DELETE", "CLEAR"], kw)

    return "OTHER"
