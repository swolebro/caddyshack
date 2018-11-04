"""Aggregating the crap from my CAD scripts into one massive shitpile."""

import datetime
import pathlib
import yaml
import os

import FreeCADGui
import FreeCAD
import Helpers
import Mesh

from . import geometry

def clear():
    """Close all FreeCAD GUI tabs."""

    for x in FreeCAD.listDocuments():
        FreeCAD.closeDocument(x)

def pretty(obj=None):
    """Show the active FreeCAD GUI tab axonometric, and sized to fit."""

    if obj:
        Helpers.show(obj)

    FreeCADGui.activeDocument().activeView().viewAxonometric()
    FreeCADGui.SendMsgToActiveView("ViewFit")

def showsave(obj, dims, dest=None):
    """Save the object to dest. Append the dims as a comment in the file for future
    reference."""

    name = obj.val().label
    doc = FreeCAD.newDocument(name)
    Helpers.show(obj)
    pretty()

    if dest is None:
        # Yeah, yeah, __file__ is bad. TODO.
        dest = pathlib.Path(__file__).parent.parent / 'export'

    if os.path.isdir(dest):
        dest = os.path.join(dest,'%s-%s.obj' % (dims.output.basename, name))

    Mesh.export(doc.Objects, str(dest))

    # Save the entire input file to the end of the gcode as a comment.
    # Save the input file, as opposed to the object in memory, since any
    # changes to the object after reading should be consistent from run to
    # run anyway.
    with open(dest, 'a') as f, open(dims.file) as g:

        # By chance, these lines could actually be read back in as YAML
        # if you stripped the leading "# ", even the input and time entries.
        lines = ["#\n",
                 "# input: %s\n" % dims.file,
                 "# time: %s" % datetime.datetime.utcnow(),
                 "#\n"]
        lines.extend("# " + line for line in  g.readlines())
        f.write(''.join(lines))

class Dims(dict):
    """A deserialization of a YAML file that's . and [] access
    friendly all the way down. A simple abomination."""

    def __convert(self, s, baseunit='', **kwargs):
        """Handle conversion of numberish strings ending with "in", "mm", or "%".

        If a baseunit is provided, force values for in or mm to that unit;
        if not provided, return the float without scaling. Always return non-numberish
        strings unchanged and percentages in their decimal form.
        """

        val, _, unit = s.partition(' ')
        if unit not in ['in', 'mm', '%']:
            return s

        val = float(val)
        if unit == '%':
            return val/100

        if not baseunit:
            return val

        if unit == 'mm' != baseunit:
            return val/25.4

        if unit == 'in' != baseunit:
            return val*25.4

        return val


    def __init__(self, file=None, *, obj=None, **kwargs):
        """You provide a YAML file that's a toplevel list or dict,
        this turns it into nested Dims all the way down.

        In the recursion, lists get turned into dicts with int keys,
        so it will behave slightly differently from a standard YAML
        load (eg. no slicing lists). Might fix that in the future.

        At the leaf level, some automagic is done to convert string
        measurements (eg. with "in" or "mm" attached) into the right
        float.

        The other args and kwargs are for internal use with recursion.
        """

        self.__dict__ = self
        if file is not None:
            self.file = file

        if file:
            obj = yaml.load(open(file))
            kwargs = obj['output']

        if isinstance(obj, list):
            obj = dict(zip(range(len(obj)), obj))

        for k, v in list(obj.items()):
            if isinstance(v, str):
                obj[k] = self.__convert(v, **kwargs)

            if isinstance(v, (list, dict)):
                obj[k] = Dims(obj=v, **kwargs)

        self.update(obj)

