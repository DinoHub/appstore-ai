# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../../inference_engine"))

project = "AAS Inference Engine"
copyright = "2022, Defence Science & Technology Agency"
author = "Oh Tien Cheng, Mathias Ho"
release = "0.1"

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

# Set up automated doc generation
apidoc_module_dir = "../../inference_engine"
apidoc_output_dir = "api"
apidoc_excluded_paths = ["tests", ".cache"]
apidoc_separate_modules = True
apidoc_module_first = True
apidoc_extra_args = ["-P"]
autodoc_mock_imports = [
    "fastapi",
    "yaml",
    "pydantic",
    "uvicorn",
    "json",
    "base64",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_title = "AAS Inference Engine Documentation"
