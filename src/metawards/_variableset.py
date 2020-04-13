
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["VariableSets", "VariableSet"]


class VariableSet:
    """This class holds a single set of adjustable variables that
       are used to adjust the variables as part of a model run
    """
    def __init__(self,
                 variables: _Dict[str, float] = None,
                 repeat_index: int = 1,
                 names: _List[str] = None,
                 values: _List[float] = None):
        """Construct a new VariableSet from the passed adjusted variable
           values.

           Parameters
           ----------
           names: List[str]
             The list of the names of the variables to adjust
           values: List[float]
             The values of the variables to adjust (same order as names)
           variables: Dict[str, float]
             names and values of variables to adjust passed as a dictionary
           repeat_index: int
             the index used to distinguish different repeats of the same
             VariableSet from one another
        """
        self._names = None
        self._vals = None
        self._varnames = None
        self._varidxs = None
        self._idx = None

        if variables is not None:
            for name, value in variables.items():
                self._add(name, value)

        if values is not None:
            if names is None:
                names = ["beta[2]", "beta[3]", "progress[1]",
                         "progress[2]", "progress[3]"]

            if len(names) != len(values):
                raise IndexError(
                    f"The number of variable values '{values}' must equal "
                    f"the number of variable names '{names}'")

            for name, value in zip(names, values):
                self._add(name, value)

        self._idx = repeat_index

    def __str__(self):
        """Return a printable representation of the variables to
           be adjusted
        """
        if self._vals is None:
            return "VariableSet::None"

        s = []

        for key, value in zip(self._names, self._vals):
            s.append(f"{key}={value}")

        if len(s) == 0:
            return f"(NO_CHANGE)[repeat {self._idx}]"
        else:
            return f"({', '.join(s)})[repeat {self._idx}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            other = VariableSet(variables=other)

        if self._idx != other._idx:
            return False

        if len(self) != len(other):
            return False

        if self._vals is None:
            return

        for i in range(0, len(self._vals)):
            if self._vals[i] != other._vals[i]:
                return False

            if self._varnames[i] != other._varnames[i]:
                return False

            if self._varidxs[i] != other._varidxs[i]:
                return False

            if self._names[i] != other._names[i]:
                return False

        return True

    def __len__(self):
        if self._vals is None:
            return 0
        else:
            return len(self._vals)

    def __getitem__(self, key):
        if self._vals is None:
            raise KeyError(f"No adjustable parameter {key} in an empty set")

        for i, name in enumerate(self._names):
            if key == name:
                return self._vals[i]

        raise KeyError(f"No adjustable parameter {key}. Available parameters "
                       f"are '{self._names}'")

    def __setitem__(self, key, value):
        if self._names is None:
            self._names = []

        for i, name in enumerate(self._names):
            if key == name:
                self._vals[i] = value
                return

        self._add(key, value)

    def _add(self, name, value):
        """Internal function to add a new variable called 'name' to
           be varied - it will be set equal to 'value'
        """
        import re

        if self._vals is None:
            self._names = []
            self._vals = []
            self._varnames = []
            self._varidxs = []

        name = name.strip()

        # look for 'variable[index]'
        m = re.search(r"(\w+)\[(\d+)\]", name)

        if m:
            self._varnames.append(m.group(1))
            self._varidxs.append(int(m.group(2)))
            self._names.append(name)
            self._vals.append(float(value))
        else:
            self._varnames.append(name)
            self._varidxs.append(None)
            self._names.append(name)
            self._vals.append(float(value))

    def variable_names(self):
        """Return the names of the variables that will be adjusted
           by this VariableSet
        """
        if self._vals is None or len(self._vals) == 0:
            return None
        else:
            from copy import deepcopy
            return deepcopy(self._names)

    def variable_values(self):
        """Return the values that the variables will be adjusted to.
           Note that 'None' means that the variable won't be adjusted
           from its default (original) value
        """
        if self._vals is None or len(self._vals) == 0:
            return None
        else:
            from copy import deepcopy
            return deepcopy(self._vals)

    def variables(self):
        """Return the variables (name and values) to be adjusted"""
        v = {}

        for name, value in zip(self._names, self._vals):
            v[name] = value

        return v

    def repeat_index(self):
        """Return the repeat index of this set. The repeat index is the
           ID of this set if the VariableSet is repeated. The index should
           range from 1 to nrepeats
        """
        return self._idx

    def fingerprint(self, include_index: bool = False):
        """Return a fingerprint for this VariableSet. This can be
           used to quickly identify and distinguish the values of
           the variables in this set from the values in other
           VariableSets which have the same adjustable variables,
           but different parameters

           If 'include_index' is true, then the repeat index
           of this VariableSet is appended to the fingerprint
        """
        if self._vals is None or len(self._vals) == 0:
            f = "NO_CHANGE"
        else:
            f = None
            for val in self._vals:
                v = str(val)
                if v.startswith("0"):
                    v = v[1:]
                if v.startswith("."):
                    v = v[1:]

                if f is None:
                    f = v
                else:
                    f += "_" + v

        if include_index:
            return "%s-%03d" % (f, self._idx)
        else:
            return f

    def adjust(self, params):  # should be 'Parameters' but circular include
        """Use the variables in this set to adjust the passed parameters

           Parameters
           ----------
           params: Parameters
             The parameters whose variables will be adjusted (in a copy)

           Returns
           -------
           params: Parameters
             The returned copy that has the adjusted parameters
        """
        try:
            for varname, varidx, value in zip(self._varnames, self._varidxs,
                                              self._vals):
                if varname == "beta":
                    print(f"SET {varname} {varidx} to {value}")
                    params.disease_params.beta[varidx] = value
                elif varname == "progress":
                    params.disease_params.progress[varidx] = value
                else:
                    raise KeyError(
                        f"Cannot set unrecognised parameter {varname} "
                        f"to {value}")
        except Exception as e:
            raise ValueError(
                f"Unable to set parameters from {self}. Error "
                f"equals {e.__class__}: {e}")


class VariableSets:
    """This class holds the collection of all VariableSet objects
       that contain the set of adjustable variables that are used
       to control a single run of the model
    """
    def __init__(self):
        self._vars = []

    def __str__(self):
        s = []

        for v in self._vars:
            s.append(str(v))

        if len(s) == 1:
            return s[0]
        elif len(s) > 0:
            return "{" + ", ".join(s) + "}"
        else:
            return "VariableSets:empty"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            v = VariableSet(variables=other)
            other = VariableSets()
            other.append(v)

        if len(self._vars) != len(other._vars):
            return False

        for v0, v1 in zip(self._vars, other._vars):
            if v0 != v1:
                return False

        return True

    def __len__(self):
        if self._vars is None:
            return 0
        else:
            return len(self._vars)

    def __getitem__(self, i: int):
        """Return the VariableSet at the specified index"""
        if self._vars is None:
            raise IndexError("Cannot index an empty VariableSets object")
        else:
            return self._vars[i]

    def append(self, variables: VariableSet):
        """Append the passed set of variables to the set that will
           be used to run a model
        """
        if isinstance(variables, dict):
            variables = VariableSet(variables=variables)

        self._vars.append(variables)

    def repeat(self, nrepeats: int):
        """Return a copy of this VariableSet in which all of the
           unique VaribleSet objects have been repeated 'nrepeats'
           times
        """
        if nrepeats <= 1:
            return self

        from copy import deepcopy

        repeats = VariableSets()

        for i in range(1, nrepeats+1):
            for v in self._vars:
                v2 = deepcopy(v)
                v2._idx = i
                repeats.append(v2)

        return repeats

    @staticmethod
    def read(filename: str, line_numbers: _List[int] = None):
        """Read and return collection of VariableSet objects from the
           specified line number(s) of the specified file

           Parameters
           ----------
           filename: str
             The name of the file from which to read the VariableSets
           line_numbers: List[int]
             The line numbers from the file to read. This is 0-indexed,
             meaning that the first line is line 0. If this is None,
             then all lines are read and used

           Returns
           -------
           variables: VariableSets
             The collection of VariableSet objects that have been read,
             in the order they were read from the file
        """
        if not isinstance(line_numbers, list):
            if line_numbers is not None:
                line_numbers = [line_numbers]

        variables = VariableSets()

        i = -1
        with open(filename, "r") as FILE:
            line = FILE.readline()

            # find the first line of the file. Use this to work out
            # the separator to use and also to see if the user has
            # named the adjustable variables
            first_line = None
            separator = ","

            # default adjustable variables
            titles = ["beta[2]", "beta[3]", "progress[1]",
                      "progress[2]", "progress[3]"]

            while line:
                i += 1

                line = line.strip()

                if first_line is None:
                    if len(line) > 0:
                        # this is a valid first line - what separator
                        # should we use?
                        if line.find(",") != -1:
                            separator = ","
                        else:
                            separator = None  # spaces

                        first_line = line

                        words = line.split(separator)

                        try:
                            float(words[0])
                            is_title_line = False
                        except Exception:
                            is_title_line = True

                        if is_title_line:
                            titles = words
                            line = FILE.readline()
                            continue

                if line_numbers is None or i in line_numbers:
                    words = line.split(separator)

                    if len(words) != len(titles):
                        raise ValueError(
                            f"Corrupted input file. Expecting {len(titles)} "
                            f"values. Received {line}")

                    vals = []

                    try:
                        for word in words:
                            vals.append(float(word))
                    except Exception:
                        raise ValueError(
                               f"Corrupted input file. Expected {len(titles)} "
                               f"numbers. Received {line}")

                    variables.append(VariableSet(names=titles,
                                                 values=vals))

                    if line_numbers is not None:
                        if len(variables) == len(line_numbers):
                            return variables

                line = FILE.readline()

        # get here if we can't find this line in the file (or if we
        # are supposed to read all lines)
        if line_numbers is None:
            return variables
        else:
            raise ValueError(
                    f"Cannot read parameters from line {line_numbers} "
                    f"as the number of lines in the file is {i+1}")
