from _typeshed import Incomplete
from typing import Any, Generator

class DottedDict:
    __slots__: Incomplete
    _d: dict[str, Any]
    def __init__(self, d: dict[str, Any] | None = None) -> None:
        """
        Construct a DottedDict, optionally from an existing dictionary.

        :param      d:    An existing dictionary.
        """
    @classmethod
    def from_base_and_override(cls, base: DottedDict, override: dict[str, Any] | None) -> DottedDict: ...
    def get(self, path: str | None = None) -> Any:
        """
        Get a value from the dictionary.

        :param      path:  The path, e.g. foo.bar.baz, or None.

        :returns:   The value stored at the path, or None if it doesn't exist.
                    Note that this cannot distinguish between None values and
                    paths that don't exist. If the path is None, returns the
                    entire dictionary.
        """
    def walk(self, path: str) -> Generator[Any, None, None]: ...
    def set(self, path: str, value: Any) -> None:
        """
        Set a value in the dictionary.

        :param      path:   The path, e.g. foo.bar.baz
        :param      value:  The value
        """
    def remove(self, path: str) -> None:
        """
        Remove a key from the dictionary.

        :param      path:  The path, e.g. foo.bar.baz
        """
    def copy(self, path: str | None = None) -> Any:
        """
        Get a copy of the value from the dictionary or copy of whole dictionary.

        :param      path:  The path, e.g. foo.bar.baz, or None.

        :returns:   A copy of the value stored at the path, or None if it doesn't exist.
                    Note that this cannot distinguish between None values and
                    paths that don't exist. If the path is None, returns a copy of the
                    entire dictionary.
        """
    def __bool__(self) -> bool:
        """
        If this collection has at least one key-value pair, return True, else return False.
        """
    def __contains__(self, path: object) -> bool: ...
    def clear(self) -> None:
        """
        Remove all key-value pairs.
        """
    def assign(self, d: dict[str, Any]) -> None:
        """
        Overwrites the old stored dictionary with a fresh new dictionary.

        :param      d:    The new dictionary to store
        """
    def update(self, d: dict[str, Any]) -> None:
        """
        Overwrite and/or add new key-value pairs to the collection.

        :param      d:    The overriding dictionary. Can contain nested dictionaries.
        """
    def get_resolved(self, variables: dict[str, str]) -> dict[str, Any]:
        """
        Resolve a DottedDict that may potentially contain template variables like $folder.

        :param      variables:  The variables

        :returns:   A copy of the underlying dictionary, but with the variables replaced
        """
    def _update_recursive(self, current: dict[str, Any], prefix: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: Any) -> bool: ...
