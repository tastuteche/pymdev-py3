# pymdev-py3
<div class="document" id="pymdev-a-python-emacs-development-module">

# pymdev - A Python Emacs Development Module

<table class="docinfo" frame="void" rules="none"><colgroup><col class="docinfo-name"> <col class="docinfo-content"></colgroup>

<tbody valign="top">

<tr>

<th class="docinfo-name">Author:</th>

<td>Atul Varma</td>

</tr>

<tr>

<th class="docinfo-name">Copyright:</th>

<td>This document has been placed in the public domain.</td>

</tr>

</tbody>

</table>

<div class="contents topic">

<a id="contents" name="contents">Contents</a>

*   [1   Introduction](#introduction)
    *   [1.1   What is pymdev?](#what-is-pymdev)
*   [2   Obtaining the latest version](#obtaining-the-latest-version)
*   [3   Prerequisites](#prerequisites)
*   [4   Installation](#installation)
*   [5   Usage](#usage)
*   [6   Bugs](#bugs)
*   [7   Future Development](#future-development)
*   [8   Contact Information](#contact-information)
*   [9   License](#license)

</div>

<div class="section">

# [1   Introduction](#id1)

<div class="section">

## [1.1   What is pymdev?](#id2)

pymdev is a simple Python module that uses pymacs, a tool that allows both-way communication between Emacs Lisp and Python, to provide Python development tools in Emacs.

The idea for pymdev was largely inspired by Jef Raskin's "The Humane Environment", now known as Archy. In Archy, Python code can be executed anywhere; you simply select code and issue the "run" command on it. This essentially obviates the need to switch to a separate Python interpreter application; whether you were writing an email or a term paper or developing software in Archy, you could harness the power of Python anywhere, at any time, simply by selecting text and issuing a "run" command.

Since Archy was very much a prototype not ready for real-world use, I decided that the text editor I used for most of my work, Emacs, could use similar functionality, so I created pymdev.

pymdev goes beyond the implementation of a simple "run" command by using Python's introspection and documentation-testing capabilities to aid in the development of Python code. See the "Usage" section of this document for more information.

</div>

</div>

<div class="section">

# [2   Obtaining the latest version](#id3)

pymdev can be downloaded from the following location:

> [http://www.toolness.com/pymdev/pymdev.py](http://www.toolness.com/pymdev/pymdev.py)

</div>

<div class="section">

# [3   Prerequisites](#id4)

pymdev has been tested on Python 2.4.

You will also need pymacs installed and set up:

> [http://pymacs.progiciels-bpi.ca/manual/index.html](http://pymacs.progiciels-bpi.ca/manual/index.html)

Optionally, you can also install autoimp if you'd like the Python code execution functions to automatically have all your packages in their global namespace:

> [http://www.princeton.edu/~csbarnes/code/autoimp](http://www.princeton.edu/~csbarnes/code/autoimp)

However, pymdev will still work fine without autoimp installed.

</div>

<div class="section">

# [4   Installation](#id5)

First, copy the <tt class="docutils literal"><span class="pre">pymdev.py</span></tt> file to your <tt class="docutils literal"><span class="pre">site-packages</span></tt> directory.

You will also need to add at least the following line to your .emacs file:

<pre class="literal-block">(pymacs-load "pymdev" "pymdev-")
</pre>

You also may want to bind some of pymdev's exported emacs functions to keys. Personally, I've abandoned the traditional use of ctrl-z for suspending emacs and replaced it for accessing my pymdev functions:

<pre class="literal-block">(define-key global-map [(control z)] nil)
(global-set-key [(control z) (control z)] 'pymdev-eval-region-to-minibuffer)
(global-set-key [(control z) (control r)] 'pymdev-eval-region-in-place)
(global-set-key [(control z) (control i)] 'pymdev-eval-region-insert)
(global-set-key [(control z) (control x)] 'pymdev-exec-and-doctest-region)
(global-set-key [(control z) (control h)] 'pymdev-help-on-region)
(global-set-key [(control z) (control d)] 'pymdev-doctest-region)
</pre>

</div>

<div class="section">

# [5   Usage](#id6)

The following are lisp functions usable from Emacs.

<tt class="docutils literal"><span class="pre">pymdev-eval-region-to-minibuffer</span></tt>

> This function evaluates the current region as a Python expression, placing the result in the minibuffer.

<tt class="docutils literal"><span class="pre">pymdev-eval-region-in-place</span></tt>

> This function evaluates the current region as a Python expression, replacing the region with the result of the evaluation.

<tt class="docutils literal"><span class="pre">pymdev-eval-region-insert</span></tt>

> This function evaluates the current region as a Python expression and inserts the result into the current buffer at the cursor position, prepending the result with an equals sign.

<tt class="docutils literal"><span class="pre">pymdev-exec-and-doctest-region</span></tt>

> This function executes the current region as a Python statement or series of statements.
> 
> stdout and stderr are redirected to an emacs buffer called 'Python output'.
> 
> If any of the objects produced by the selected code (functions, classes, etc) have doctests, they are executed automatically, and any errors in them are placed in an emacs buffer called 'Doctest output'.

<tt class="docutils literal"><span class="pre">pymdev-help-on-region</span></tt>

> Evaluates the current region as a Python expression and provides you with context-sensitive help on the result.
> 
> If the result of the expression is a module, function, class, or anything with a docstring, the documentation for it will be placed in a new buffer called 'Python documentation'.
> 
> If the result of the expression is a dictionary, its keys will be listed in the minibuffer.
> 
> If the expression is followed by a period ('.'), this function will work somewhat similarly to the 'autocomplete' mechanism of an IDE: it will inspect the result of the expression and present you with a list of members from which you can select. The item you select will be inserted at the cursor location (i.e., after the '.').
> 
> Note that this function actually evaluates the text denoted by the given region, so if any of the functions have side effects, they will manifest themselves!

</div>

<div class="section">

# [6   Bugs](#id7)

pymdev doesn't currently respond very well if the result of an evaluation contains non-ASCII characters.

</div>

<div class="section">

# [7   Future Development](#id8)

I'm not a big fan of the distinction in this module between "evaluating" Python expressions and "executing" Python statements: it forces me to think about whether the Python code I've selected is an expression or a statement. I'd rather have that be auto-detected, or something similarly humane.

I'd like to integrate statistics about code coverage for statement execution/doctests, as well as some kind of pychecker support.

</div>

<div class="section">

# [8   Contact Information](#id9)

Please feel free to send questions, comments, bug reports, and other correspondence regarding pymdev to <tt class="docutils literal"><span class="pre">varmaa@gmail.com</span></tt>.

</div>

<div class="section">

# [9   License](#id10)

This software has been contributed to the public domain.

</div>

</div>
