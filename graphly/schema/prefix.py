import re


_PNAME_LOCAL_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*$")


def is_valid_sparql_pname_local(local: str) -> bool:
    """
    Validate a conservative safe subset of SPARQL prefixed-name local parts.

    This intentionally rejects characters that commonly break query parsing
    (for example `/`), and only accepts ASCII alphanumerics plus `_`, `-`, `.`.
    """
    if not local:
        return False
    if "/" in local:
        return False
    return _PNAME_LOCAL_SAFE_PATTERN.fullmatch(local) is not None


class Prefix:
    """
    Represents a namespace prefix mapping for RDF/SPARQL or Turtle syntax.

    Attributes:
        short (str): The short prefix (abbreviation).
        long (str): The full URI associated with the prefix.

    Methods:
        __init__(short: str, url: str):
            Initialize a Prefix instance with a short abbreviation and full URL.
        to_sparql() -> str:
            Return the SPARQL 'PREFIX' representation of the prefix.
        to_turtle() -> str:
            Return the Turtle '@prefix' representation of the prefix.
        shorten(uri: str) -> str:
            Shorten a full URI using the prefix, if applicable.
        lengthen(short: str) -> str:
            Expand a shortened URI using the prefix to its full form.
        to_dict() -> dict[str, str]:
            Convert the Prefix instance into a dictionary representation.
        from_dict(obj: dict[str, str]) -> Prefix:
            Create a Prefix instance from a dictionary.
    """

    short: str
    long: str

    def __init__(self, short: str, url: str) -> None:
        """
        Initializes a Prefix instance that maps a short prefix to a full URL.

        Parameters:
            short (str): The short prefix (abbreviation).
            url (str): The full URL associated with the prefix.
        """
        self.short = short
        self.long = url

    def to_sparql(self) -> str:
        """
        Generates the SPARQL representation of the prefix.

        Returns:
            str: A string in the format 'PREFIX short: <long>'.
        """
        return f"PREFIX {self.short}: <{self.long}>"

    def to_turtle(self) -> str:
        """
        Generates the Turtle syntax representation of the prefix.

        Returns:
            str: A string in the format '@prefix short: <long> .'.
        """
        return f"@prefix {self.short}: <{self.long}> ."

    def shorten(self, uri: str) -> str:
        """
        Shortens a full URI using the prefix when it is SPARQL-safe.

        The URI is shortened only when:
        - the URI starts with this prefix long value, and
        - the resulting local part matches a conservative SPARQL-safe subset.

        If not, the full URI is returned unchanged.

        Parameters:
            uri (str): The full URI to be shortened.

        Returns:
            str: A prefixed name (`prefix:local`) or the original full URI.
        """
        if uri.startswith("<") and uri.endswith(">"):
            uri = uri[1:-1]

        if not uri.startswith(self.long):
            return uri

        local = uri[len(self.long) :]
        if not is_valid_sparql_pname_local(local):
            return uri

        return f"{self.short}:{local}"

    def lengthen(self, short: str) -> str:
        """
        Expands a shortened URI using the prefix to its full form.

        Parameters:
            short (str): The shortened URI using the prefix.

        Returns:
            str: The full URI with the short prefix replaced by the long URL.
        """
        return str(short).replace(self.short + ":", self.long)

    def to_dict(self) -> dict[str, str]:
        """
        Converts the Prefix instance into a dictionary representation.

        Returns:
            dict[str, str]: A dictionary with keys 'short' and 'long' representing the prefix abbreviation and full URL.
        """
        return {"short": self.short, "long": self.long}

    @staticmethod
    def from_dict(obj: dict[str, str]) -> "Prefix":
        """
        Creates a Prefix instance from a dictionary representation.

        Parameters:
            obj (dict[str, str]): A dictionary containing 'short' and 'long' keys.

        Returns:
            Prefix: An instance of the Prefix class with attributes populated from the dictionary.
        """
        return Prefix(obj["short"], obj["long"])
