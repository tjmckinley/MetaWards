
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List

__all__ = ["WardInfo", "WardInfos"]


@_dataclass
class WardInfo:
    """This class holds metadata about a ward, e.g. its name(s),
       any ID code(s), any information about the region or
       authority it is in etc.
    """
    #: Name of the ward
    name: str = ""
    #: Any alternative names of the ward
    alternate_names: _List[str] = _field(default_factory=list)

    #: Official ID code of the ward
    code: str = ""
    #: Any alternative ID codes of the ward
    alternate_codes: _List[str] = _field(default_factory=list)

    #: The name of the local authority it is in
    authority: str = ""

    #: The ID of the local authority it is in
    authority_code: str = ""

    #: The name of the region it is in
    region: str = ""

    #: The ID of the region it is in
    region_code: str = ""


@_dataclass
class WardInfos:
    """Simple class that holds a list of WardInfo objects, and provides
       useful search functions over that list. This prevents me from
       cluttering up the interface of Network
    """
    #: The list of WardInfo objects, one for each ward in order
    wards: _List[WardInfo] = _field(default_factory=list)

    def __len__(self):
        return len(self.wards)

    def __getitem__(self, index):
        return self.wards[index]

    def find_by_name(self, name: str, include_alternates=True,
                     authority: str = None, region: str = None,
                     match: bool = False,
                     match_authority_and_region: bool = False,
                     best_match: bool = False):
        """Find a ward that matches the name 'name'. This returns
           the set of indicies of all wards that match the passed
           name

           Parameters
           ----------
           name: str or regexp
             The name to search. This is case-insensitve and a partial
             match by default. If you want more control, then pass
             in a regular expression object
           include_alternates:
             Search the alternative names as well as the primary name
           authority: str or regexp
             Optionally limit the search to authorities that match 'authority'
           region: str or regexp
             Optionally limit the search to regions that match 'region'
           match: bool
             If True, then match rather than search
           match_authority_and_region: bool
             If True, then also match the authority and region rather
             than searching
           best_match: bool
             If True, then return the best matching ward

           Returns
           -------
           indicies: list[int]
             The indicies of all nodes that match
        """
        import re

        if not isinstance(name, re.Pattern):
            search = re.compile(name, re.IGNORECASE)
        else:
            search = name

        if authority is not None:
            if not isinstance(authority, re.Pattern):
                authority = re.compile(authority, re.IGNORECASE)

            if match_authority_and_region:
                authority = authority.match
            else:
                authority = authority.search

        if region is not None:
            if not isinstance(region, re.Pattern):
                region = re.compile(region, re.IGNORECASE)

            if match_authority_and_region:
                region = region.match
            else:
                region = region.search

        if match:
            search = search.match
        else:
            search = search.search

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            is_match = False

            if search(ward.name):
                is_match = True

            elif include_alternates:
                for alternate in ward.alternate_names:
                    if search(alternate):
                        is_match = True
                        break

            if is_match:
                if authority and authority(ward.authority) is None:
                    continue

                if region and region(ward.region) is None:
                    continue

                matches.append(i)

        if best_match:
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return matches[0]

            best = None
            score = None
            pattern = search.__self__.pattern

            for match in matches:
                diff = abs(len(pattern) - len(self.wards[match].name))

                if best is None:
                    best = match
                    score = diff
                elif diff < score:
                    best = match
                    score = diff

            return best
        else:
            return matches

    find = find_by_name

    def find_by_authority(self, name, include_region=False,
                          match: bool = False):
        """Find a ward whose authority matches the name 'name'. This returns
           the set of indicies of all wards whose authorities that
           match the passed name

           Parameters
           ----------
           name: str or regexp
             The name to search. This is case-insensitve and a partial
             match by default. If you want more control, then pass
             in a regular expression object
           include_region:
             Search the region as well as the authority
           match: bool
             If True, then match rather than search

           Returns
           -------
           indicies: list[int]
             The indicies of all wards that match
        """
        import re

        if not isinstance(name, re.Pattern):
            search = re.compile(name, re.IGNORECASE)
        else:
            search = name

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            if search.search(ward.authority):
                matches.append(i)

            elif include_region:
                if search.search(ward.region):
                    matches.append(i)

        return matches

    def find_by_code(self, code: str, include_alternates=True,
                     authority: str = None, region: str = None,
                     match: bool = False,
                     match_authority_and_region: bool = False):
        """Find a ward that matches the code 'code'. This returns
           the set of indicies of all wards that match the passed
           code

           Parameters
           ----------
           code: str or regexp
             The code to search. This is case-insensitve and a partial
             match by default. If you want more control, then pass
             in a regular expression object
           include_alternates:
             Search the alternative codes as well as the primary codes
           authority: str or regexp
             Optionally limit the search to authorities that match 'authority'
             code
           region: str or regexp
             Optionally limit the search to regions that match 'region' code
           match: bool
             If True, then match rather than search
           match_authority_and_region: bool
             If True, then also match the authority and region rather
             than searching

           Returns
           -------
           indicies: list[int]
             The indicies of all nodes that match
        """
        import re

        if not isinstance(code, re.Pattern):
            search = re.compile(code, re.IGNORECASE)
        else:
            search = code

        if authority is not None:
            if not isinstance(authority, re.Pattern):
                authority = re.compile(authority, re.IGNORECASE)

            if match_authority_and_region:
                authority = authority.match
            else:
                authority = authority.search

        if region is not None:
            if not isinstance(region, re.Pattern):
                region = re.compile(region, re.IGNORECASE)

            if match_authority_and_region:
                region = region.match
            else:
                region = region.search

        if match:
            search = search.match
        else:
            search = search.search

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            is_match = False

            if search(ward.code):
                is_match = True

            elif include_alternates:
                for alternate in ward.alternate_codes:
                    if search(alternate):
                        is_match = True
                        break

            if is_match:
                if authority and authority(ward.authority_code) is None:
                    continue

                if region and region(ward.region_code) is None:
                    continue

                matches.append(i)

        return matches
