
Indentation finder, by Philippe Fremy <phil at freehackers dot org>
Copyright 2002-2010 Philippe Fremy

This program is distributed under the BSD license. You should have received
a copy of the file LICENSE.txt along with this software.

To test me, type:
python run_tests.py

To install, type:
python setup.py install

See web page for more information:
http://www.freehackers.org/Indent_Finder

History:
========

version 1.4:
- improve the heuristic, some file where incorrectly reported as tab when being mixed
- ('tab', 4) was returned instead of DEFAULT_OUTPUT when no decision could be made. This is now
  configurable.
- vim_output() now includes a comment about the detected indentation

version 1.31:
hum, previous released was rushed!
- the --vim-output was not working. Fixed in this version

version 1.3:
- remove indent_checker, this was a useless program
- improve the indentation algorithm to be able to detecte mixed type
  indentation
- detect mixed type indentation, like the one used in vim source files

version 1.2:
- add indent_checker, to check the consistency of the indentation of a source
  tree

version 1.1:
- improve the heuristic by detecting indentation steps

version 1.0:
- initial release

