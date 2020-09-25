[![PyPI version](https://badge.fury.io/py/markdown-xblock.svg)](https://pypi.python.org/pypi/markdown-xblock)

# Markdown XBlock
### Based on the [HTML XBlock by OpenCraft](https://github.com/open-craft/xblock-html)

## Introduction
This XBlock allows course authors to create and edit course content in Markdown
and displays it as HTML.

## Installation
You may install the markdown-xblock using its setup.py, or if you prefer to use pip, run:

```shell
pip install markdown-xblock
```

If you prefer to install directly from Git, run:

```shell
pip install git+https://github.com/citynetwork/markdown-xblock.git
```

You may specify the `-e` flag if you intend to develop on the repo.

The minimum supported Python version is 3.5.

To enable this block, add `"markdown"` to the course's advanced module list. 
The option `Markdown` will appear in the advanced components.

Once you've added a new `Markdown` component to your course, you can also add custom CSS classes to the component
by selecting `EDIT`/`Settings` and adding to the `classes` list (Note: use double quotes `" "`). Example:
```
["custom-css-class-1", "custom-css-class-2"]
```

The `Markdown` block uses [markdown2](https://pypi.org/project/markdown2/) to translate the content into HTML, 
by default the following extras are included:

* "code-friendly"
* "fenced-code-blocks"
* "footnotes"
* "tables"
* "use-file-vars"

It is possible to configure more [extras](https://github.com/trentm/python-markdown2/wiki/Extras), by adding to the extras list under `"markdown"` key in `XBLOCK_SETTINGS`
at `/edx/etc/{studio|lms}.yml`

By default, the `safe_mode` for `markdown2` library is enabled, which means that writing inline HTML is not allowed and if written, all tags will be replaced with `[HTML_REMOVED]`. To disable this setting and allow inline HTML, you'll need to set the `safe_mode` to `False` in `XBLOCK_SETTINGS`.

Example:
```
XBLOCK_SETTINGS:
    markdown:
        extras:
            - code-friendly
            - fenced-code-blocks
            - footnotes
            - header-ids
            - metadata
            - pyshell
            - smarty-pants
            - strike
            - target-blank-links
            - use-file-vars
            - wiki-tables
            - tag-friendly
        safe_mode: True
```

## Development
If you'd like to develop on this repo or test it in [devstack](https://github.com/edx/devstack), clone this repo to your
devstack's `~/workspace/src`, ssh into the appropriate docker container (`make lms-shell` and/or `make studio-shell`),
run `pip install -e /edx/src/xblock-html`, and restart the service(s).


### Running tests
The testing framework is built on [tox](https://tox.readthedocs.io/en/latest/). After installing tox, you can run `tox` from your Git checkout of this repository.

To throw away and rebuild the testing environment, run:
```shell
$ tox -r
```
For running PEP-8 checks only:
```shell
$ tox -e flake8
```
