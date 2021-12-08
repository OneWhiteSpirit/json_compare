# json_compare

Compare two JSON files
----------

``json_compare`` is a library for comparing JSON files in a way that yields difference on each level. Realization based on Tree data structure.

Features
----------

- Python 3.6+


Installation
===============

1. Clone the Repository
	git clone https://github.com/OneWhiteSpirit/json_compare.git
2. Change the directory
	cd json_compare

Usage
===============
	Perform file comparison:
	python3 diff.py test_files/File-A.json test_files/File-B.json

	Perform unit testing of the library (Warnings about some resources may appear):
	python3 test.py


Supported options
~~~~~~~~~~~~~~~~~~~~~~

``json_first``
	Relative or absolute path to the first input JSON file. Mandatory option.

``json_second``
	Relative or absolute path to the second input JSON file. Mandatory option.

