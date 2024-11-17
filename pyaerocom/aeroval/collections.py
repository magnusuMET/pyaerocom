import abc
from fnmatch import fnmatch
import json

from pyaerocom._lowlevel_helpers import BrowseDict
from pyaerocom.aeroval.modelentry import ModelEntry
from pyaerocom.aeroval.obsentry import ObsEntry
from pyaerocom.exceptions import EntryNotAvailable, EvalEntryNameError


class BaseCollection(BrowseDict, abc.ABC):
    #: maximum length of entry names
    MAXLEN_KEYS = 25
    #: Invalid chars in entry names
    FORBIDDEN_CHARS_KEYS = []

    # TODO: Wait a few release cycles after v0.23.0 and see if this can be removed
    def _check_entry_name(self, key):
        if any([x in key for x in self.FORBIDDEN_CHARS_KEYS]):
            raise EvalEntryNameError(
                f"Invalid name: {key}. Must not contain any of the following "
                f"characters: {self.FORBIDDEN_CHARS_KEYS}"
            )

    def __setitem__(self, key, value):
        self._check_entry_name(key)
        super().__setitem__(key, value)

    def keylist(self, name_or_pattern: str = None) -> list:
        """Find model names that match input search pattern(s)

        Parameters
        ----------
        name_or_pattern : str, optional
            Name or pattern specifying search string.

        Returns
        -------
        list
            list of keys in collection that match input requirements. If
            `name_or_pattern` is None, all keys will be returned.

        Raises
        ------
        KeyError
            if no matches can be found
        """
        if name_or_pattern is None:
            name_or_pattern = "*"

        matches = []
        for key in self.keys():
            if fnmatch(key, name_or_pattern) and key not in matches:
                matches.append(key)
        if len(matches) == 0:
            raise KeyError(f"No matches could be found that match input {name_or_pattern}")
        return matches

    @abc.abstractmethod
    def get_entry(self, key) -> object:
        """
        Getter for eval entries

        Raises
        ------
        KeyError
            if input name is not in this collection
        """
        pass

    @property
    @abc.abstractmethod
    def web_interface_names(self) -> list:
        """
        List of webinterface names for
        """
        pass


class Collection(abc.ABC):
    def __init__(self):
        self._entries = {}

    def __iter__(self):
        """
        Yield each entry in the collection.
        """
        yield from self._entries.values()

    @abc.abstractmethod
    def add_entry(self, key, value) -> None:
        pass

    @abc.abstractmethod
    def remove_entry(self, key) -> None:
        pass

    @abc.abstractmethod
    def get_entry(self, key) -> object:
        pass

    def keylist(self, name_or_pattern: str = None) -> list[str]:
        """Find model / obs names that match input search pattern(s)

        Parameters
        ----------
        name_or_pattern : str, optional
            Name or pattern specifying search string.

        Returns
        -------
        list
            list of keys in collection that match input requirements. If
            `name_or_pattern` is None, all keys will be returned.

        Raises
        ------
        KeyError
            if no matches can be found
        """
        if name_or_pattern is None:
            name_or_pattern = "*"

        matches = []
        for key in self._entries.keys():
            if fnmatch(key, name_or_pattern) and key not in matches:
                matches.append(key)
        if len(matches) == 0:
            raise KeyError(f"No matches could be found that match input {name_or_pattern}")
        return matches

    @property
    def web_interface_names(self) -> list:
        """
        List of web interface names for each obs entry

        Returns
        -------
        list
        """
        return self.keylist()

    def to_json(self) -> str:
        """Serialize ModelCollection to a JSON string."""
        return json.dumps({k: v.dict() for k, v in self._entries.items()}, default=str)


class ObsCollection(Collection):
    """
    Dict-like object that represents a collection of obs entries

    Keys are obs names, values are instances of :class:`ObsEntry`. Values can
    also be assigned as dict and will automatically be converted into
    instances of :class:`ObsEntry`.


    Note
    ----
    Entries must not necessarily be only observations but may also be models.
    Entries provided in this collection refer to the y-axis in the AeroVal
    heatmap display and must fulfill the protocol defined by :class:`ObsEntry`.

    """

    def add_entry(self, key: str, entry: dict | ObsEntry):
        if isinstance(entry, dict):
            entry = ObsEntry(**entry)
        self._entries[key] = entry

    def remove_entry(self, key: str):
        if key in self._entries:
            del self._entries[key]

    def get_entry(self, key) -> ObsEntry:
        """
        Getter for obs entries

        Raises
        ------
        KeyError
            if input name is not in this collection
        """
        try:
            entry = self._entries[key]
            entry.obs_name = self.get_web_interface_name(key)
            return entry
        except (KeyError, AttributeError):
            raise EntryNotAvailable(f"no such entry {key}")

    def get_all_vars(self) -> list[str]:
        """
        Get unique list of all obs variables from all entries

        Returns
        -------
        list
            list of variables specified in obs collection

        """
        vars = []
        for ocfg in self._entries.values():
            vars.extend(ocfg.get_all_vars())
        return sorted(list(set(vars)))

    def get_web_interface_name(self, key):
        """
        Get webinterface name for entry

        Note
        ----
        Normally this is the key of the obsentry in :attr:`obs_config`,
        however, it might be specified explicitly via key `web_interface_name`
        in the corresponding value.

        Parameters
        ----------
        key : str
            key of entry.

        Returns
        -------
        str
            corresponding name

        """
        # LB: private method?
        return (
            self._entries[key].web_interface_name
            if self._entries[key].web_interface_name is not None
            else key
        )

    @property
    def web_interface_names(self) -> list:
        """
        List of web interface names for each obs entry

        Returns
        -------
        list
        """
        return [self.get_web_interface_name(key) for key in self.keylist()]

    @property
    def all_vert_types(self):
        """List of unique vertical types specified in this collection"""
        return list({x.obs_vert_type for x in self._entries.values()})


class ModelCollection(Collection):
    """
    Object that represents a collection of model entries

    Keys are model names, values are instances of :class:`ModelEntry`. Values
    can also be assigned as dict and will automatically be converted into
    instances of :class:`ModelEntry`.

    Note
    ----
    Entries must not necessarily be only models but may also be observations.
    Entries provided in this collection refer to the x-axis in the AeroVal
    heatmap display and must fulfill the protocol defined by
    :class:`ModelEntry`.
    """

    def add_entry(self, key: str, entry: dict | ModelEntry):
        if isinstance(entry, dict):
            entry = ModelEntry(**entry)
        entry.model_name = key
        self._entries[key] = entry

    def remove_entry(self, key: str):
        if key in self._entries:
            del self._entries[key]

    def get_entry(self, key: str) -> ModelEntry:
        """
        Get model entry configuration
        Parameters
        ----------
        model_name : str
            name of model

        Returns
        -------
        dict
            Dictionary that specifies the model setup ready for the analysis
        """
        if key in self._entries:
            return self._entries[key]
        else:
            raise EntryNotAvailable(f"no such entry {key}")
