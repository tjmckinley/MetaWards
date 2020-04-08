
__all__ = ["VariableSets", "VariableSet"]


class VariableSet:
    """This class holds a single set of adjustable variables that
       are used to adjust the variables as part of a model run
    """
    def __init__(self, variables=None, repeat_index: int = 1):
        """Construct a new VariableSet from the passed adjusted variable
           values. This 'variables' should be a dictionary giving the
           names of all variables to be adjusted, together with the
           values to which they should be set. If the set value
           is "None" then this means that the value should be kept
           at whatever the original value was (useful if you want to
           include the original value as part of a larger run)
        """
        self._vars = variables
        self._idx = repeat_index

    def __str__(self):
        """Return a printable representation of the variables to
           be adjusted
        """
        s = []

        for key, value in self._vars.items():
            s.append(f"{key}={value}")

        if len(s) == 0:
            return f"(NO_CHANGE)[repeat {self._idx}]"
        else:
            return f"({', '.join(s)})[repeat {self._idx}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            if self._vars is None or len(self._vars) == 0:
                return len(other) == 0

            if len(self._vars) != len(other):
                return False

            for key, value in self._vars.items():
                if value != other[key]:
                    return False

            return True
        else:
            if self._idx != other._idx:
                return False

            if len(self) != len(other):
                return False

            if self._vars is None:
                return

            for key, value in self._vars.items():
                if value != other._vars[key]:
                    return False

            return True

    def __len__(self):
        if self._vars is None:
            return 0
        else:
            return len(self._vars)

    def __getitem__(self, key):
        if self._vars is None:
            raise KeyError(f"No adjustable parameter {key} in an empty set")

        return self._vars[key]

    def __setitem__(self, key, value):
        if self._vars is None:
            self._vars = {}

        self._vars[key] = value

    def variable_names(self):
        """Return the names of the variables that will be adjusted
           by this VariableSet
        """
        if self._vars is None or len(self._vars) == 0:
            return None
        else:
            return list(self._vars.keys())

    def variable_values(self):
        """Return the values that the variables will be adjusted to.
           Note that 'None' means that the variable won't be adjusted
           from its default (original) value
        """
        if self._vars is None or len(self._vars) == 0:
            return None
        else:
            return list(self._vars.values())

    def variables(self):
        """Return the variables (name and values) to be adjusted"""
        return self._vars

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
        if self._vars is None or len(self._vars) == 0:
            f = "NO_CHANGE"
        else:
            f = None
            for val in self._vars.values():
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
        """Use the variables in this set to adjust the passed parameters"""
        try:
            for key, value in self._vars.items():
                if value is not None:
                    if key == "beta2":
                        params.disease_params.beta[2] = value
                    elif key == "beta3":
                        params.disease_params.beta[3] = value
                    elif key == "progress1":
                        params.disease_params.progress[1] = value
                    elif key == "progress2":
                        params.disease_params.progress[2] = value
                    elif key == "progress3":
                        params.disease_params.progress[3] = value
                    else:
                        raise KeyError(
                            f"Cannot set unrecognised parameter {key} "
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

        if len(s) > 0:
            return "\n".join(s)
        else:
            return "VariableSets:empty"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
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
            variables = VariableSet(variables)

        self._vars.append(variables)

    def repeat(self, nrepeats: int):
        """Return a copy of this VariableSet in which all of the
           unique VaribleSet objects have been repeated 'nrepeats'
           times
        """
        if nrepeats <= 1:
            return self

        repeats = VariableSets()

        for i in range(1, nrepeats+1):
            for v in self._vars:
                repeats.append(VariableSet(variables=v.variables(),
                                           repeat_index=i))

        return repeats
