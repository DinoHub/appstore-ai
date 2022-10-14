# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../../back-end"))

project = "AI App Store"
copyright = "2022, Defence Science & Technology Agency"
author = "Oh Tien Cheng, Mathias Ho"
release = "0.1"
language = "en"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosectionlabel",  # Allow reference sections using its title
    "sphinx.ext.autosummary",  # Generates summary for autodocs
    "sphinx.ext.autodoc",  # Generate documentation from docstrings
    "sphinx.ext.doctest",  # Include code snippets in the documentation
    "sphinx.ext.duration",  # Generate duration report
    "sphinx.ext.napoleon",  # Supports Google-style and Numpy-style docstrings
    "sphinx.ext.viewcode",  # Add link to source code
    "sphinxcontrib.apidoc",  # Populate autodoc for API documentation
    "sphinx_copybutton",  # Copy button for code to clipboard
    "sphinx_design",  # Extension for more supporting components
    "sphinx_inline_tabs",  # Extension for inline tabs
    "myst_parser",  # Extend the usage of Markdowns with Directives
]

templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}


# Set up auto-generated documentation for Back-end
apidoc_module_dir = "../../back-end"
apidoc_output_dir = "back-end-api"
apidoc_excluded_paths = ["tests", ".cache"]
apidoc_separate_modules = True
apidoc_module_first = True
apidoc_extra_args = ["-P"]
autodoc_mock_imports = [
    # If possible, try to use real imports, but sometimes this is not possible so we fake the import
    "pymongo",
    "motor",
]
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo-dark.png",
    "dark_logo": "logo-dark.png",
    "sidebar_hide_name": True,
}
html_title = "AI App Store Documentation"
