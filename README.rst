caddyshack
==========

This is a semi-organized pile of utilities and `FreeCAD`__/`CadQuery`__ scripts with
modest documentation. Most of them are meant to be run with the `CadQuery plugin
module`__.

.. __: https://freecadweb.org/
.. __: https://github.com/dcowden/cadquery
.. __: https://github.com/jmwright/cadquery-freecad-module

For a quickstart on how to get those running, see `below`_.

Some of the parts are meant to be 3D printed and used as-is in plastic, whereas
others are meant to be turned into templates and jigs (mostly for metalworking).

My goals for this project are:

1. Help me keep track of dimensional tweaks to my designs as I test and find
   that parts are too tight/too loose, etc.
2. Eventually form some utilities that can be resused between designs (if
   nothing else, a library of standard measurements for clearance holes, etc).
3. Maybe help some people with examples. This stuff is hard to come by and not
   necessarily intuitive.

I'll try and include photos of finished products here (yes, committing PNGs to
a repo), with links to `my Thingiverse`__ for object files and `my YouTube`__
for stuff in action (because I'm not committing *those* to the the repo). That
should give you an idea of where to look for code examples to help you build your
own stuff. See other README files and script docstrings for those links. Note
that anything you see outside this repo is prone to being outdated, with this
repo being the current source. Consult these files, git log, and git blame for
a better cronology.

.. __: https://www.thingiverse.com/swolebro/designs
.. __: https://www.youtube.com/channel/UCRMLI3S0AFukV1tzX6Cl2Cw

For licensing, see the file: :doc:`LICENSE`.

Project Layout
--------------

::

    caddyshack
    ├── caddyshack      # Python utilities for reducting duplication. No stable API.
    ├── export          # Default folder I dump STL or OBJ files to; not here, on Thingiverse.
    ├── gcode           # Default folder I dump sliced gcode to. You need to slice your own.
    ├── scripts         # Python scripts for generating export objects. Further categorized.
    ├── environment.yml # Might help you install all the software you need.
    └── README.rst      # You are here.


I'm not going to bother with any standard development processes here. No
branches, no releases, no "stable," just a pile of scripts. I'm not even making
caddyshack an installable module for now, since I don't want to give anyone
the idea that they should be using it in their projects.

If a script doesn't work because of an import error, see if it's one of my files,
or a third party library. If it's third party, install it. If it's one of mine,
check your ``sys.path`` to make sure it's looking in the right places. If the code
executes but doesn't do what you expect, I might have updated a utility, breaking
and older script by mistake, without knowing/fixing it. In that case, you can
``git log -p script_file_or_dir`` to find its last working state and checkout the code
from that point in time.

.. _below:

Quick Guide to Running FreeCAD/CadQuery
---------------------------------------

This is easiest if you already have the `Anaconda Python distribution`__ installed,
since it lets you install a whole mess of software in an isolated system, and if you
fuck it up, you can blow it all away and rebuild it without losing much.

.. __: https://www.anaconda.com/download/

With that, you can run:

.. code-block:: bash

    cd path/to/caddyshack
    conda env create --file environment.yml
    source activate freecad
    FreeCAD

And you should be on your way, with a reasonably recent and hopefully not-broken
version of FreeCAD. The environment creation step takes a minute (and installs
about 2 gigs worth of dependencies), but you only have to do that the first time.
Browsing the menus to ``View > Workbench > CadQuery`` will add a CadQuery item
to the menu list so you can open a script and run it (shortcut: F2). If you go to
``Edit > Preferences > General`` you can set it so the workbench opens automatically
every time.

At some point I'll get around to figuring out how to run these things from
the commandline directly (or better, while editing in vim), but for now, this works,
and it's handy to have the 3D view to check your work.

Most of these scripts are going to be written for Python 3.6, FreeCAD
>=0.18_pre, the CadQuery plugin >=1.2.0, and to be used inside the plugin
workbench. These designs are all very specific-use, so I'm not worried about
other people needing to be able to run my code verbatim anyway. I'm just
putting it up here for you to have examples - an addendum to those provided
in the CadQuery docs.

Also, one super-duper pro-tip... FreeCAD can be finnicky with a few operations,
particularly fillets. Things will crash occasionally - open source software,
right?  It's not professional, but you get a hell of a lot more than you pay
for and it saves you from being shafted by ever-changing license requirements
on SAS CAD products. Anyway, each time you run a script through the CadQuery
plugin, a copy of the file is saved to ``/tmp``. So, this line of bash will
take the latest tempfile and put it into your clipboard, so when you reopen
your script, you can just paste the contents over and carry on where you left
off:

.. code-block:: bash

    ls -tc /tmp/tmp* | head -1 | xargs xclip -selection clipboard

Additionally, if you find yourself making changes that break something in the
course of a work session (where you don't have multiple commits snapshotting
each change), looking to the tempfiles can help you track where you botched it
up.

Printed Parts
-------------

My prints are done with a Lulzbot Mini, usually with ABS. Most measurements are
in inches, because: 1. 'murica. 2. Fuck you, world. It should be rather obvious
when you load an STL or OBJ into your slicer whether you need to scale it by
25.4x or not. At some point I may figure out a shortcut for scaling everything
prior to exporting.

For the prints that are to be used as-is, I typically stick with fine settings,
4-ish shells, 30-50% infill, and zig-zag support. Yes, the prints are slow, but
it makes them generally passable quality, and speed doesn't matter so much
when your printer is networked and you don't need you laptop hooked up to it. If
your printer is not networked, you should really fix that.

For my slicer, I use Cura Lulzbot Edition (an ungodly mess to compile from source
if you can't use the provided Ubuntu packages). At some point I hope to take
that out of the equation and call CuraEngine from the commandline directly, so
it'll be easier to record exact printer settings with each GCODE file (say, in
comments). For the time being, I'll keep human-readable, free-form notes.

As for the software to run the printer, a Raspberry Pi or equivalent SOC with a
combination of `ArchLinuxArm`__/SSH/tmux/`pronsole.py`__ works well for me. If you're
less technically inclined, you might b better off with `OctoPi`__, a purpose-built
OS image for Raspberry Pis.

.. __: https://archlinuxarm.org/
.. __: https://github.com/kliment/Printrun
.. __: https://octoprint.org/

Printed Jigs
------------

Some things are just things to help me make other things using other things. I think
this is a pretty under-appreciated application of consumer-grade 3D printers.

It turns out 3D printers are a nice way to make jigs for marking cuts/holes,
aligning parts for tack welding, or handheld plasma torch stenciling. Yes, even
plasma cut stenciling. The workpiece stays surprisingly cool during that
process, so as long as you build your stencil with some offsets, it should last
for anywhere from 10-50 cuts, and when it's too melt-y, you can just print a
new one. You likely won't have the same luck with oxy-acetylene.

The plasma cutting jigs I build are meant to work for the geometry of a Hypertherm
Duramax drag-tip torch, so you can just run it along the stencil. Shouldn't be too
hard to apply the same idea for other drag-tip torches. (There are much cheaper
and adequate alternatives to Hypertherm today.)

Most of these I'll print at a higher speed with lower infill. Stenciles still end
up being 100% solid though, just by virtue of their thinness.

I guess some of this code could be modified for woodworking (eg. router rigs),
if you're more of a dead-trees kind of guy. Really, you could even use FreeCAD
to design templates, print them out on paper, and cut them from plywood or HDF
with a bandsaw.

I'm hoping that once I get off my lazy ass and actually do my `CNC plasma build`__
that I can reuse some of this same code and skip the 3D printing part. Though
more likely than not I'll end up having to start from scratch, because computers
and tech stacks and `programming sucks`__.

.. __: https://github.com/swolebro/plasma-build.git
.. __: https://www.stilldrinking.org/programming-sucks
