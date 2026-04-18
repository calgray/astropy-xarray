# Contributing

`astropy-xarray` is developed on [github](https://github.com/calgray/astropy-xarray).

## Commit message tags

By default, the upstream dev CI is disabled on pull request and push events. You can
override this behavior per commit by adding a \<tt>[test-upstream]\</tt> tag to the first
line of the commit message.

## Linters / Autoformatters

In order to keep code consistent, we use

- [Black](https://black.readthedocs.io/en/stable/) for standardized code formatting
- [blackdoc](https://blackdoc.readthedocs.io/en/stable/) for standardized code formatting in documentation
- [Flake8](https://flake8.pycqa.org/en/latest/) for general code quality
- [isort](https://github.com/PyCQA/isort) for standardized order in imports. See also [flake8-isort](https://github.com/gforcada/flake8-isort).

## Release process

1.  the release happens from `main` so make sure it is up-to-date:

    ```sh
    git pull origin main
    ```

2.  look at `CHANGELOG.md` and make sure it is complete and with
    references to issues and pull requests

3.  open and merge a pull request with these changes

4.  make sure the CI on main pass

5.  check that the documentation build on readthedocs completed successfully

6.  Fill in the release date and commit the release:

    ```sh
    git commit -am "Release v0.X.Y"
    ```

7.  Tag the release and push to main:

    ```sh
    git tag -a v0.X.Y -m "v0.X.Y"
    git push origin --tags
    ```

8.  Draft a release for the new tag on github. A CI will pick that up, build the project
    and push to PyPI. Be careful, this can't be undone.

9.  Make sure readthedocs builds both `stable` and the new tag

10. Add a new section to `CHANGELOG.md` and push directly to main
