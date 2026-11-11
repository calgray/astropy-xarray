import functools
import inspect
import sys
from inspect import Parameter

import astropy.units as u
import xarray as xr

from astropy_xarray.conversion import strip_units
from astropy_xarray.itertools import zip_mappings

if sys.version_info >= (3, 13, 0):
    from builtins import ExceptionGroup
else:
    from exceptiongroup import ExceptionGroup

variable_parameters = (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)


def _number_of_results(result):
    if isinstance(result, tuple):
        return len(result)
    elif result is None:
        return 0
    else:
        return 1


def _add_note_310(exc: BaseException, note: str) -> None:
    """Exception add_note backwards compatibility for python 3.10"""
    if hasattr(exc, "add_note"):
        exc.add_note(note)
    elif exc.args:
        exc.args = (f"{exc.args[0]}\n{note}", *exc.args[1:])
    else:
        exc.args = (note,)


def expects(*args_units, return_value=None, equivalencies=None, **kwargs_units):
    """
    Decorator which ensures the inputs and outputs of the decorated
    function are expressed in the expected units.

    Arguments to the decorated function are checked for the specified
    units, converting to those units if necessary, and then stripped
    of their units before being passed into the undecorated
    function. Therefore the undecorated function should expect
    unquantified DataArrays, Datasets, or numpy-like arrays, but with
    the values expressed in specific units.

    Parameters
    ----------
    func : callable
        Function to decorate, which accepts zero or more
        xarray.DataArrays or numpy-like arrays as inputs, and may
        optionally return one or more xarray.DataArrays or numpy-like
        arrays.
    *args_units : unit-like or mapping of hashable to unit-like, optional
        Units to expect for each positional argument given to func.

        The decorator will first check that arguments passed to the
        decorated function possess these specific units (or will
        attempt to convert the argument to these units), then will
        strip the units before passing the magnitude to the wrapped
        function.

        A value of None indicates not to check that argument for units
        (suitable for flags and other non-data arguments).
    return_value : unit-like or list of unit-like or mapping of hashable to unit-like \
                   or list of mapping of hashable to unit-like, optional
        The expected units of the returned value(s), either as a
        single unit or as a list of units. The decorator will attach
        these units to the variables returned from the function.

        A value of None indicates not to attach any units to that
        return value (suitable for flags and other non-data results).
    **kwargs_units : mapping of hashable to unit-like, optional
        Unit to expect for each keyword argument given to func.

        The decorator will first check that arguments passed to the decorated
        function possess these specific units (or will attempt to convert the
        argument to these units), then will strip the units before passing the
        magnitude to the wrapped function.

        A value of None indicates not to check that argument for units (suitable
        for flags and other non-data arguments).

    Returns
    -------
    return_values : Any
        Return values of the wrapped function, either a single value or a tuple
        of values. These will be given units according to ``return_value``.

    Raises
    ------
    TypeError
        If any of the units are not a valid type.
    ValueError
        If the number of arguments or return values does not match the number of
        units specified. Also thrown if any parameter does not have a unit
        specified.

    See Also
    --------
    pint.registry.UnitRegistry.wraps

    Examples
    --------
    Decorating a function which takes one quantified input, but
    returns a non-data value (in this case a boolean).

    >>> @expects("deg C")
    ... def above_freezing(temp):
    ...     return temp > 0
    ...

    Decorating a function which allows any dimensions for the array, but also
    accepts an optional `weights` keyword argument, which must be dimensionless.

    >>> @expects(None, weights="dimensionless")
    ... def mean(da, weights=None):
    ...     if weights:
    ...         return da.weighted(weights=weights).mean()
    ...     else:
    ...         return da.mean()
    ...
    """

    def outer(func):
        signature = inspect.signature(func)

        params_units = signature.bind(*args_units, **kwargs_units)

        missing_params = [
            name
            for name, p in signature.parameters.items()
            if p.kind not in variable_parameters and name not in params_units.arguments
        ]
        if missing_params:
            raise ValueError(
                "Missing units for the following parameters: "
                + ", ".join(map(repr, missing_params))
            )

        n_expected_results = _number_of_results(return_value)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal return_value

            params = signature.bind(*args, **kwargs)
            # don't apply defaults, as those can't be quantities and thus must
            # already be in the correct units

            errors = []
            for name, (value, units) in zip_mappings(
                params.arguments, params_units.arguments
            ):
                try:
                    if units is None:
                        if isinstance(value, u.Quantity) or (
                            isinstance(value, (xr.DataArray, xr.Dataset))
                            and value.astropy.unit
                        ):
                            raise TypeError(
                                "Passed in a quantity where none was expected"
                            )
                        continue
                    if isinstance(value, u.Quantity):
                        params.arguments[name] = value.to(units, equivalencies).value
                    elif isinstance(value, (xr.DataArray, xr.Dataset)):
                        params.arguments[name] = strip_units(
                            value.astropy.to(units, equivalencies)
                        )
                    else:
                        raise TypeError(
                            f"Attempting to convert non-quantity {value} to {units}."
                        )
                except (
                    TypeError,
                    ValueError,
                    ValueError,
                ) as e:
                    _add_note_310(
                        e, f"expects: raised while trying to convert parameter {name}"
                    )
                    errors.append(e)

            if errors:
                raise ExceptionGroup("Errors while converting parameters", errors)

            result = func(*params.args, **params.kwargs)

            n_results = _number_of_results(result)
            if return_value is not None and (
                (isinstance(result, tuple) ^ isinstance(return_value, tuple))
                or (n_results != n_expected_results)
            ):
                message = "mismatched number of return values:"
                if n_results != n_expected_results:
                    message += f" expected {n_expected_results} but got {n_results}."
                elif isinstance(result, tuple) and not isinstance(return_value, tuple):
                    message += (
                        " expected a single return value but got a 1-sized tuple."
                    )
                else:
                    message += (
                        " expected a 1-sized tuple but got a single return value."
                    )
                raise ValueError(message)

            if result is None:
                return

            if not isinstance(result, tuple):
                result = (result,)
            if not isinstance(return_value, tuple):
                return_value = (return_value,)

            final_result = []
            errors = []
            for index, (value, units) in enumerate(zip(result, return_value)):
                if units is not None:
                    try:
                        if isinstance(value, (xr.Dataset, xr.DataArray)):
                            value = value.astropy.quantify(units)
                        else:
                            value = u.Quantity(value, units)
                    except Exception as e:
                        _add_note_310(
                            e,
                            f"expects: raised while trying to convert return value {index}",
                        )
                        errors.append(e)

                final_result.append(value)

            if errors:
                raise ExceptionGroup("Errors while converting return values", errors)

            if n_results == 1:
                return final_result[0]
            return tuple(final_result)

        return wrapper

    return outer
