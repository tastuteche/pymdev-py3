# -----------------------------------------------------------------
# pymdev.py
# 5/30/2004
# By Atul Varma (varmaa@gmail.com)
# -----------------------------------------------------------------

"""
    pymdev - A Python Emacs Development Module

    pymdev is a simple Python module that uses pymacs, a tool that
    allows both-way communication between Emacs Lisp and Python, to
    provide Python development tools in Emacs.

    This software has been contributed to the public domain.
"""

# -----------------------------------------------------------------
# Imports
# -----------------------------------------------------------------

from future import standard_library
standard_library.install_aliases()
from builtins import str
import sys
import io
import doctest

from Pymacs import lisp


# -----------------------------------------------------------------
# Public constants
# -----------------------------------------------------------------

__version__ = "0.1.1"


# -----------------------------------------------------------------
# Private module variables
# -----------------------------------------------------------------

# A dictionary representing the global namespace for calls
# to py_eval(), exec_and_doctest_region(), etc.
_py_globals = {
     "__builtins__" : __builtins__
     }

# If the autoimp module is installed, use it to import every module
# into the _py_globals namespace; otherwise, don't worry about it.
try:
     exec("from autoimp import *", _py_globals)
except ImportError:
     pass


# -----------------------------------------------------------------
# Public module helper functions
# -----------------------------------------------------------------

def eval_region(delete=0):
     """Evaluate the current region and return the result,
     optionally deleting the region from the buffer."""

     return eval(get_region(delete), _py_globals)

def get_region(delete=0):
     """Returns the text of the current region, optionally
     deleting the region from the buffer."""
     
     start = lisp.point()
     end = lisp.mark(lisp.t)
     text = lisp.buffer_substring(start, end)
     if delete:
          lisp.delete_region(start, end)
     return text

def list_items(list):
     """Returns a string with a listing of all the items
     in the list."""
     
     string = ""
     for i in list:
          string += str(i) + "    "
     return string

def make_symbol_list(list):
     """Makes a lisp associative list (alist) of all the elements in
     the given list and returns it."""
     
     from Pymacs.pymacs import Symbol
     out = "("
     for i in list:
          if not str(i).startswith('__'):
               out += '("%s" 1) ' % str(i)
     out += ")"
     return Symbol(out)

def autocomplete_list(prompt, listy):
     """Presents the user with a minibuffer prompt and the given
     auto-completion list."""
     
     completion_list = make_symbol_list(listy)
     return lisp.completing_read(prompt, completion_list)

def autocomplete_member(prompt, members):
     """Presents the user with a minibuffer prompt and the given
     auto-completion list based on a member list like the one
     returned by inspect.getmembers()."""
     
     listy = []
     for i,j in members:
          listy.append(i)
     return autocomplete_list(prompt, listy)

def insert_in_other_buffer(bufname, text):
     """Creates/erases a buffer with the given name, opens it in a
     separate visible  pane, and pastes the given text into it."""
     
     lisp.get_buffer_create(bufname)
     lisp.display_buffer(bufname, 1)
     old_buf = lisp.current_buffer()
     lisp.set_buffer(bufname)
     lisp.erase_buffer()
     lisp.insert(text)
     lisp.set_buffer(old_buf)


# -----------------------------------------------------------------
# Public pymacs lisp functions
#
# These functions are exported to emacs.
# -----------------------------------------------------------------

def eval_region_in_place():
     """Evaluate the current region as a python expression
     and replace the region with the result."""     

     lisp.insert(str(eval_region(delete=1)))

def eval_region_insert():
     """Evaluate the current region as a python expression and insert
     the result into the current buffer, prepended with an equals
     sign."""
     
     lisp.insert(" = " + str(eval_region()))

def eval_region_to_minibuffer():
     """Evaluate the current region as a python expression
     and put the result in the minibuffer."""

     lisp.message(str(eval_region()))

def exec_and_doctest_region():
     """This function executes the current region as a Python
     statement or series of statements.

     Stdout and stderr are redirected to an emacs buffer called
     'Python output'.

     If any of the objects produced by the selected code (functions,
     classes, etc) have doctests, they are executed automatically, and
     any errors in them are placed in an emacs buffer called 'Doctest
     output'."""

     code_str = get_region()

     temp_stdout = io.StringIO()
     tempLocals = {}
     old_stdout = sys.stdout
     old_stderr = sys.stderr
     sys.stdout = temp_stdout
     sys.stderr = temp_stdout

     try:
          exec(code_str, _py_globals, tempLocals)
     finally:
          sys.stdout = old_stdout
          sys.stderr = old_stderr

     doctests = []
     finder = doctest.DocTestFinder()
     for obj in list(tempLocals.values()):
          if hasattr( obj, "__name__" ):
               doctests.extend( finder.find(obj) )

     buf = io.StringIO()
     runner = doctest.DocTestRunner(verbose=1)

     for test in doctests:
          runner.run(test, out=buf.write)

     if runner.failures:
          out = buf.getvalue()
          insert_in_other_buffer("Doctest output", out)
     else:
          if runner.tries:
               test_info_str = "All %d doctest(s) passed." % (runner.tries)
          else:
               test_info_str = ""

          _py_globals.update( tempLocals )

          out = temp_stdout.getvalue()
          if out:
               insert_in_other_buffer("Python output", out)

          messageStr = "Python code executed " \
                       "successfully. %s" % test_info_str
          lisp.message( messageStr )

def doctest_region():
     """Run doctests in the current region.  Note that this will
     essentially look at the current region as a 'doctest file', not
     as python code; if you want to run doctests in python code, use
     exec_and_doctest_region().

     Any errors in the doctests are placed in an emacs buffer called
     'Doctest output'.
     """

     text = get_region()

     parser = doctest.DocTestParser()
     test = parser.get_doctest(
          text,
          _py_globals,
          "<emacs text selection>",
          "<emacs text selection>",
          0
          )

     buf = io.StringIO()
     runner = doctest.DocTestRunner(verbose=1)
     runner.run(test, out=buf.write)

     if runner.failures:
          out = buf.getvalue()
          insert_in_other_buffer("Doctest output", out)
     else:
          lisp.message("All %d doctest(s) passed." % (runner.tries))

def help_on_region():
     """Evaluates the current region as a Python expression and
     provides you with context-sensitive help on the result.

     If the result of the expression is a module, function, class, or
     anything with a docstring, the documentation for it will be
     placed in a new buffer called 'Python documentation'.

     If the result of the expression is a dictionary, its keys will be
     listed in the minibuffer.

     If the expression is followed by a period ('.'), this function
     will work somewhat similarly to the 'autocomplete' mechanism of
     an IDE: it will inspect the result of the expression and present
     you with a list of members from which you can select.  The item
     you select will be inserted at the cursor location (i.e., after
     the '.').

     Note that this function actually evaluates the text denoted by
     the given region, so if any of the functions have side effects,
     they will manifest themselves!"""
     
     text = get_region()
     if text[-1] == '.':
          dot_used = 1
          text = text[0:-1]
     else:
          dot_used = 0
          
     try:
          obj = eval(text, _py_globals)
     except Exception:
          lisp.message("Can't evaluate that region.")
          return

     import types
     if isinstance(obj, int) or \
        isinstance(obj, float):
          lisp.message("Target is a number.")
          return

     docs = getattr(obj, '__doc__')
     if docs == None:
          docs = ""

     import inspect

     try:
          import autoimp

          if isinstance( obj, autoimp._RecursiveLazyModule ):
               # Force the lazy module to load its 'real' module
               obj.__help__()
               # Have the object point to the real module, not the
               # lazy proxy.
               obj = obj._autoimp_lib
     except ImportError:
          pass

     if inspect.isbuiltin(obj):
          insert_in_other_buffer("Python documentation", docs)
          #lisp.message(docs)
          return

     if inspect.isfunction(obj) or inspect.ismethod(obj):
          out = text + inspect.formatargspec(*inspect.getargspec(obj))
          out += "\n\n" + docs
          insert_in_other_buffer("Python documentation", out)
          #lisp.message(out)
          return

     if isinstance(obj, dict):
          if dot_used:
               m = autocomplete_member("Enter dictionary method name:",
                                       inspect.getmembers(obj))
               lisp.insert(m)
          else:
               out = "Target is a dictionary.  Keys are:\n\n"
               out += list_items(list(obj.keys()))
               lisp.message(out)
          return
     elif isinstance(obj, list) or isinstance(obj, tuple):
          if dot_used:
               m = autocomplete_member("Enter list/tuple method name:",
                                       inspect.getmembers(obj))
               lisp.insert(m)
          else:
               out = "Target is a list.  Elements are:\n\n"
               out += list_items(obj)
               lisp.message(out)
          return

     if not dot_used:
          #lisp.message(docs + "\n\n")
          insert_in_other_buffer("Python documentation", docs)
          return

     if inspect.ismodule(obj):
          m = autocomplete_member("Enter module attribute name:",
                                  inspect.getmembers(obj))
          lisp.insert(m)
          return

     klass = obj
     try:
          klass = getattr(obj, '__class__')
          prompt = "Enter attribute name for instance of class %s: " % \
                   klass.__name__
     except AttributeError:
          prompt = "Enter attribute name: "

     m = autocomplete_member(prompt, inspect.getmembers(klass))
     lisp.insert(m)


# -----------------------------------------------------------------
# Module initialization
# -----------------------------------------------------------------

# A dictionary containing functions to be exported to emacs.
interactions = {}

interactions[eval_region_in_place] = ''
interactions[eval_region_insert] = ''
interactions[eval_region_to_minibuffer] = ''
interactions[exec_and_doctest_region] = ''
interactions[help_on_region] = ''
interactions[doctest_region] = ''

# Local Variables :
# pymacs-auto-reload : t
# End :
