
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["VariableSets", "VariableSet"]


class VariableSet:
    """This class holds a single set of adjustable variables that
       are used to adjust the variables as part of a model run

       Examples
       --------
       >>> v = VariableSet()
       >>> v["beta[1]"] = 0.95
       >>> v["beta[2]"] = 0.9
       >>> print(v.fingerprint())
       (beta[1]=0.95, beta[2]=0.9)[repeat 1]
       >>> params = Parameters()
       >>> params.set_disease("ncov")
       >>> v.adjust(params)
       >>> print(params.disease_params.beta[1],
       >>>       params.disease_params.beta[2])
       0.95 0.9
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

           Examples
           --------
           >>> v = VariableSet()
           >>> v["beta[1]"] = 0.95
           >>> v["beta[2]"] = 0.9
           >>> print(v.fingerprint())
           (beta[1]=0.95, beta[2]=0.9)[repeat 1]
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
        s = []

        if self._vals is not None and len(self._vals) > 0:
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

           Returns
           -------
           names: List[str]
             The list of names of variables to be adjusted
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

           Returns
           -------
           values: List[float]
             The list of values for variables to be adjusted to
        """
        if self._vals is None or len(self._vals) == 0:
            return None
        else:
            from copy import deepcopy
            return deepcopy(self._vals)

    def variables(self):
        """Return the variables (name and values) to be adjusted

           Returns
           -------
           variables: Dict[str, float]
             The dictionary mapping the names of the variables that
             with be adjusted to their desired values
        """
        v = {}

        for name, value in zip(self._names, self._vals):
            v[name] = value

        return v

    def repeat_index(self):
        """Return the repeat index of this set. The repeat index is the
           ID of this set if the VariableSet is repeated. The index should
           range from 1 to nrepeats

           Returns
           -------
           index: int
             The repeat index of this set
        """
        return self._idx

    def make_compatible_with(self, other):
        """Return a copy of this VariableSet which has been made
           compatible with 'other'. This means that it will change
           the same variables as 'other', e.g. by adding 'None'
           changes for missing variables. This will raise an error
           if it is not possible to make this set compatible

           Parameters
           ----------
           other: VariableSet
             The passed VariableSet for which this should be made compatible

           Returns
           -------
           result: VariableSet
             A copy of this VariableSet which is now compatible with 'other'

           Example
           -------
           >>> v1 = VariableSet()
           >>> v1["beta1"] = 0.9
           >>> v1["beta2"] = 0.8

           >>> v2 = VariableSet()
           >>> v2["beta1"] = 0.6
           >>> v2 = v2.make_compatible_with(v1)
           >>> print(v2)
           (beta1=0.6, beta2=0.8)[repeat 1]
        """
        from copy import deepcopy

        if self._names is None:
            v = deepcopy(other)
            v._idx = self._idx
            return v

        if other._names is None:
            raise ValueError(f"VariableSet {self} is not compatible with "
                             f"VariableSet {other}")

        nmatch = 0

        for name in self._names:
            if name not in other._names:
                raise ValueError(f"VariableSet {self} is not compatible with "
                                 f"VariableSet {other}")
            nmatch += 1

        if len(other._names) == nmatch:
            # fully compatible
            return deepcopy(self)

        v = deepcopy(self)

        for name in other._names:
            if name not in self._names:
                v[name] = other[name]

        return v

    @staticmethod
    def extract_values(fingerprint: str):
        """Return the original values from the passed fingerprint
           or filename. This assumes that the fingerprint
           was created using the 'fingerprint' function, namely
           that any integers are actually 0.INTEGER

           Parameters
           ----------
           fingerprint: str
             The fingerprint (or filename) to decode

           Returns
           -------
           (values, repeat): (List[float], int)
             The list of values of the variables and the repeat
             index. The repeat index is None if it wasn't included
             in the fingerprint
        """
        from pathlib import Path

        # if this is a filename then extract only the fingerprint
        fingerprint = Path(Path(fingerprint).name)
        for suffix in fingerprint.suffixes:
            fingerprint = str(fingerprint).replace(suffix, "")

        # does this have a repeat index - if so, this is the last
        # value at the end after the hyphen (negative numbers are ~)
        parts = fingerprint.split("-")

        if len(parts) > 1:
            repeat_index = int(parts[-1])
            fingerprint = "-".join(parts[0:-1])
        else:
            repeat_index = None

        # now get the values
        values = []

        for part in fingerprint.split("_"):
            try:
                if part.startswith("~"):
                    scl = -1.0
                    part = part[1:]
                else:
                    scl = 1.0

                if part.find(".") != -1:
                    # this is already a floating point number
                    value = float(part)
                else:
                    # this is an integer, which represents 0.INT
                    part = f"0.{part}"
                    value = float(part)

                values.append(value)
            except Exception:
                # this is not part of the fingerprint
                pass

        return (values, repeat_index)

    def fingerprint(self, include_index: bool = False):
        """Return a fingerprint for this VariableSet. This can be
           used to quickly identify and distinguish the values of
           the variables in this set from the values in other
           VariableSets which have the same adjustable variables,
           but different parameters

           Parameters
           ----------
           include_index: bool
             Whether or not to include the repeat_index in the fingerprint

           Returns
           -------
           fingerprint: str
             The fingerprint for this VariableSet
        """
        if self._vals is None or len(self._vals) == 0:
            f = "NO_CHANGE"
        else:
            f = None
            for val in self._vals:
                v = str(val)
                if v.startswith("-"):
                    v = v[1:]
                if v.startswith("0"):
                    v = v[1:]
                if v.startswith("."):
                    v = v[1:]

                if val < 0:
                    # use `~` for negative numbers
                    v = "~" + v

                if f is None:
                    f = v
                else:
                    f += "_" + v

        if include_index:
            return "%s-%03d" % (f, self._idx)
        else:
            return f

    def adjust(self, params):  # should be 'Parameters' but circular include
        """Use the variables in this set to adjust the passed parameters.
           Note that this directly modifies 'params'

           Parameters
           ----------
           params: Parameters
             The parameters whose variables will be adjusted

           Returns
           -------
           None

           Examples
           --------
           >>> v = VariableSet()
           >>> v["beta[1]"] = 0.95
           >>> v["beta[2]"] = 0.9
           >>> print(v.fingerprint())
           (beta[1]=0.95, beta[2]=0.9)[repeat 1]
           >>> params = Parameters()
           >>> params.set_disease("ncov")
           >>> v.adjust(params)
           >>> print(params.disease_params.beta[1],
           >>>       params.disease_params.beta[2])
           0.95 0.9
        """
        if self._vals is None or len(self._vals) == 0:
            return

        try:
            for varname, varidx, value in zip(self._varnames, self._varidxs,
                                              self._vals):
                if value is not None:
                    if varname == "beta":
                        params.disease_params.beta[varidx] = value
                    elif varname == "progress":
                        params.disease_params.progress[varidx] = value
                    elif varname == "too_ill_to_move":
                        params.disease_params.too_ill_to_move[varidx] = value
                    elif varname == "contrib_foi":
                        params.disease_params.contrib_foi[varidx] = value
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

       Examples
       --------
       >>> v = VariableSets()
       >>> v.append({"beta[2]": 0.95, "beta[3]": 0.9})
       >>> v.append({"beta[1]": 0.86, "beta[2]": 0.89})
       >>> print(v)
       {(beta[2]=0.95, beta[3]=0.9)[repeat 1], (beta[1]=0.86,
       beta[2]=0.89)[repeat 1]}
       >>> v = v.repeat(2)
       >>> print(v)
       {(beta[2]=0.95, beta[3]=0.9)[repeat 1], (beta[1]=0.86,
       beta[2]=0.89)[repeat 1], (beta[2]=0.95, beta[3]=0.9)[repeat 2],
       (beta[1]=0.86, beta[2]=0.89)[repeat 2]}
    """
    def __init__(self):
        """Initialise an empty VariableSets object

           Parameters
           ----------
           None

           Returns
           -------
           None
        """
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
           be used to run a model. If there are any existing
           VariableSet objects in this list, then the new VariableSet
           must adjust the same variables

           Parameters
           ----------
           variables: VariableSet
             The VariableSet to append to this list. If you pass a
             dict of {str: float} values, then this will automatically
             be converted into a VariableSet. Note that all VariableSet
             objects in a VariableSets must adjust the same variables

           Returns
           -------
           None
        """
        if isinstance(variables, dict):
            variables = VariableSet(variables=variables)

        if self._vars is None:
            self._vars = []

        if len(self._vars) > 0:
            variables = variables.make_compatible_with(self._vars[0])

        self._vars.append(variables)

    def repeat(self, nrepeats: int):
        """Return a copy of this VariableSet in which all of the
           unique VaribleSet objects have been repeated 'nrepeats'
           times

           Parameters
           ----------
           nrepeats: int
             The number of repeats of the VariableSet objects to
             perform

           Returns
           -------
           repeats: VariableSets
             A new VariableSets object containing 'nrepeats' copies
             of the VariableSet objects from this set
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
