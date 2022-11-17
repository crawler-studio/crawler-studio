# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from recommonmark.parser import CommonMarkParser
source_parsers = {
  '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']

project = 'crawler_studio'
copyright = '2022, liuxianglong'
author = 'liuxianglong'
release = '1.5.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.viewcode',
  'sphinx.ext.todo',
  'sphinx.ext.mathjax',
  'sphinx.ext.apidoc',
  'sphinx.ext.extlinks',
  'nbsphinx',
  'sphinx_markdown_tables'
]

templates_path = ['_templates']
exclude_patterns = []

language = 'zh_CN'

master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

import sphinx_rtd_theme  # 添加这行

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']
