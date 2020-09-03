# Markdown XBlock
### Based on the [HTML XBlock by OpenCraft](https://github.com/open-craft/xblock-html)

## Introduction
This XBlock allows course authors to create and edit course content in Markdown
and displays it as HTML.

## Installation
You may install the markdown-xblock using its setup.py, or if you prefer to use pip, run:

```shell
pip install https://github.com/citynetwork/xblock-html.git
```
You may specify the `-e` flag if you intend to develop on the repo.

The minimum supported Python version is 3.5.

To enable this block, add `"markdown"` to the course's advanced module list. 
The option `Markdown` will appear in the advanced components.

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


### Setting the requirements up
Hitting the following command will install in your python environment all the requirements you need for this project:

```shell
$ make requirements
```

### Running tests
Tests are essential for this project to keep all its features working as expected. To check your changes you can use:

```shell
$ make test
```
Or if you want to check the code quality only, hit:
```shell
$ make quality
```