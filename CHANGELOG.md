```{eval-rst}
.. currentmodule:: astropy_xarray
.. currentmodule:: xarray
```

# What's New

## 0.2.2 (31 October 2026)

- Added improvements from `pint-xarray`:
  - Properly rename the coordinate units (:pull:`351`).
    By [Justus Magin](https://github.com/keewis).
  - Don't rely on ``xarray``'s default behavior regarding ``attrs`` in {py:func}`astropy_xarray.expects`.
    By [Justus Magin](https://github.com/keewis).
  - Fix quantifying a existing index and adjust the index conversion tests.
    By [Justus Magin](https://github.com/keewis).
  - Switch to using pixi for all dependency management.
    By [Justus Magin](https://github.com/keewis).
  - Added the {py:func}`pint_xarray.expects` decorator to allow wrapping quantity-unaware functions.
    By [Justus Magin](https://github.com/keewis) and [Tom Nicholas](https://github.com/TomNicholas>).
  - Follow the change in signature of {py:meth}`xarray.Index.equals`
    By [Justus Magin](https://github.com/keewis).
  - Add units to the inline `repr` and define a custom `repr`.
    By [Justus Magin](https://github.com/keewis).
  - Collect multiple errors into a specific exception group
    By [Justus Magin](https://github.com/keewis).
  - Pass `sel` options to the wrapped array.
    By [Bhavin Patel](https://github.com/bpatel2107>).
- Support python 3.14.

By [Callan Gray](https://github.com/calgray).

## 0.2.1 (18 Apr 2026)

- Added support for `astropy==7.2.0` sky coordinates.

By [Callan Gray](https://github.com/calgray).

## 0.2.0 (31 Mar 2026)

- Added {py:mod}`coordinates` submodule with {py:func}`coordinates.dataset_to_skycoord` and {py:func}`coordinates.skycoord_to_dataset` explicit conversion functions for working with {py:class}`astropy.coordinates.SkyCoord`.

- Added support for specialized quantities:
  - {py:class}`astropy.time.Time`
  - {py:class}`astropy.time.TimeDelta`
  - {py:class}`astropy.coordinates.Angle`
  - {py:class}`astropy.coordinates.Longitude`
  - {py:class}`astropy.coordinates.Latitude`
  - {py:class}`astropy.coordinates.Distance`
  - {py:class}`astropy.units.LogQuantity`

- Added {py:meth}`Dataset.astropy.to_skycoord` accessor.

By [Callan Gray](https://github.com/calgray).

## 0.1.0 (17 Jul 2025)

- Added `equivalencies` parameter to {py:meth}`DataArray.astropy.to` and {py:meth}`Dataset.astropy.to`.

- Removed `registry` parameter from {py:meth}`DataArray.astropy.quantify` and {py:meth}`Dataset.astropy.quantify`.

- Migrated `pint.Quantity` usage to {py:class}`astropy.units.Quantity`, `pint.UnitRegistry` to {py:mod}`astropy.units`, `pint.UnitRegistry.formatter` to {py:mod}`astropy.units.format` ({pull}`1`)

  Notable behavioural differences include:
  - Unit registry instance is managed at module scope instead of local scope.
  - Multiplying by an array by an {py:class}`astropy.units.Unit` coerses to {py:class}`astropy.units.Quantity` of float64. Explicit construction required to use other numpy dtypes.
  - {py:class}`astropy.units.Quantity` uses `unit` and `value` members instead of `units` and `magnitude`.
  - `Unit()` is not an instance of {py:class}`astropy.units.Unit`, only {py:class}`astropy.units.UnitBase`.
  - Different format literals, see [built-in formats](https://docs.astropy.org/en/stable/units/format.html#built-in-formats).

By [Callan Gray](https://github.com/calgray).
