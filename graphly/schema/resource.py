from typing import Literal, Dict, Any

class Resource:
    """
    Represents a resource that can be an entity (a class is an entity), a literal, a numeric value, or a blank node.

    Attributes:
        resource_type (Literal['blank', 'literal', 'numeric', 'entity']):
            The type of the resource.
        value (str | int | float):
            The literal or numeric value, if applicable.
        uri (str):
            The URI of the resource, if applicable.
        label (str):
            A human-readable label for the resource (eg: object of rdfs:label).
        comment (str):
            Additional descriptive information about the resource (eg: object of rdfs:comment).
        class_uri (str):
            The URI of the class this resource belongs to, if any (eg: object of rdf:type).

    Methods:
        __init__(uri_or_value, label=None, comment=None, class_uri=None, resource_type='entity'):
            Initialize a Resource instance with the given attributes.
        is_value() -> bool:
            Check if the resource is a value (literal or numeric).
        get_text(comment: bool = False) -> str:
            Get a human-readable string representation of the resource, optionally including the comment.
        to_dict(prefix: str = '') -> dict:
            Convert the resource into a dictionary representation, with an optional key prefix.
        from_dict(obj: dict, prefix: str = '') -> Resource:
            Create a Resource instance from a dictionary representation.
    """

    # To define the type of resource it is
    resource_type: Literal['blank', 'text', 'numeric', 'entity']

    # Information about the resource
    value: str | int | float
    uri: str
    label: str 
    comment: str
    class_uri: str 


    def __init__(self, uri_or_value, label: str = None, comment: str = None, class_uri: str = None, resource_type: Literal['blank', 'text', 'numeric', 'entity'] = 'entity') -> None:
        """
        Initialize a Resource object.

        Args:
            uri_or_value (str | int | float, optional): The URI of the resource if it's an entity,
                or the literal/numeric value if the resource is a value type. Defaults to None.
            label (str, optional): A human-readable label for the resource (eg: object of rdfs:label). Defaults to None.
            comment (str, optional): Additional information or description of the resource (eg: object of rdfs:comment). Defaults to None.
            resource_type (Literal['blank', 'literal', 'numeric', 'entity'], optional): 
                Specifies the type of the resource. Defaults to 'entity'.
            class_uri (str, optional): The URI of the class this resource belongs to (if any) (eg: object of rdf:type). Defaults to None.

        Attributes set based on type:
            - If the resource is a value (literal or numeric), `self.value` is set.
            - If the resource is an entity or blank node, `self.uri`, `self.label`, `self.comment`, 
            and `self.class_uri` are set.
        """

        self.resource_type = resource_type

        if self.is_value():
            self.value = uri_or_value
            self.text = f"{self.value}"
        else: 
            self.uri = uri_or_value
            self.label = label or None
            self.comment = comment or None
            self.class_uri = class_uri or None

    def is_value(self) -> bool:
        """
        Check if the resource represents a value (a literal or numeric value).

        Returns:
            bool: True if the resource_type is 'literal' or 'numeric', False otherwise.
        """
        return self.resource_type == 'text' or self.resource_type == 'numeric'


    def get_text(self, comment: bool = False) -> str:
        """
        Get a string representation of the resource.

        For value resources (literal or numeric), returns the value as a string.
        For entity or blank resources, returns the label if available, otherwise the URI.
        Optionally appends the comment if `comment=True` and a comment exists.

        Args:
            comment (bool, optional): Whether to include the resource's comment in the output. Defaults to False.

        Returns:
            str: The textual representation of the resource.
        """

        # If the Resource is a value, just return the value
        if self.is_value(): 
            return f"{self.value}"

        # But if it is an Entity, construct a Text
        text = f"{self.label or self.uri}"
        # And append the comment if asked
        if comment and self.comment: 
            return f"{text}: {self.comment}"
        # Otherwise just return the text without the comment
        return text


    def to_dict(self, prefix: str= '') -> Dict[str, Any]:
        """
        Converts the object into a dictionary representation.

        Parameters:
            prefix (str): Optional string to prepend to each key in the dictionary.

        Returns:
            dict: A dictionary containing the object's properties. Includes 'value' if the object represents a value,
                or 'uri', 'label', 'comment', and 'class_uri' if it represents an entity.
        """

        # Create the properties that there is all the time
        to_return = { prefix + 'resource_type': self.resource_type }
        # If it is a value, add the value part
        if self.is_value(): to_return[prefix + 'value'] = self.value
        # And otherwise, add the Entity part
        else: 
            to_return[prefix + 'uri'] = self.uri
            to_return[prefix + 'label'] = self.label
            if self.comment: to_return[prefix + 'comment'] = self.comment
            if self.class_uri: to_return[prefix + 'class_uri'] = self.class_uri
        return to_return
    
    
    @staticmethod
    def from_dict(obj: Dict[str, Any], prefix: str= '') -> 'Resource':
        """
        Creates a Resource instance from a dictionary representation.

        Parameters:
            obj (dict): The dictionary containing resource data.
            prefix (str): Optional string that was prepended to keys in the dictionary.

        Returns:
            Resource: An instance of the Resource class with properties populated from the dictionary.
        """
        
        resource_type = obj.get(prefix + 'resource_type', 'entity')
        is_value = resource_type == "text" or resource_type == "numeric"

        # Parse the object and return a Resource instance
        return Resource(
            resource_type=resource_type,
            uri_or_value=obj.get(prefix + 'value') if is_value else obj.get(prefix + 'uri'),
            label=obj.get(prefix + 'label', None),
            comment=obj.get(prefix + 'comment', None),
            class_uri=obj.get(prefix + 'class_uri', None)
        )
    
    def __str__(self):
        return self.uri