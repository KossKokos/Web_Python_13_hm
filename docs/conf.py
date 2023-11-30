# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

# sys.path.append(os.path.abspath('..'))
# sys.path.append(r"C:\Users\kosko\Documents\Python\Python_Web\Module_13\Web_Python_13_hm\.env")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


project = 'Contacts API'
copyright = '2023, koskokos'
author = 'koskokos'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
