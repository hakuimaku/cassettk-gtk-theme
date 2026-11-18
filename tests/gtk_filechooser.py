"""Check GTK3 file chooser rendering with Cassettk."""
from pathlib import Path
import sys
import tempfile

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

with tempfile.TemporaryDirectory(prefix="cassettk-chooser-") as directory:
    root = Path(directory)
    (root / "files/Folder").mkdir(parents=True)
    (root / "files/README.md").write_text("Cassettk fixture\n")
    window = Gtk.Window()
    chooser = Gtk.FileChooserWidget(action=Gtk.FileChooserAction.OPEN)
    chooser.set_current_folder(str(root / "files"))
    window.add(chooser)
    window.show_all()
    loop = GLib.MainLoop()
    failures = []

    def finish():
        try:
            import cairo
            screenshot = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                window.get_allocated_width(),
                window.get_allocated_height(),
            )
            window.draw(cairo.Context(screenshot))
            screenshot.write_to_png(sys.argv[1])
            print("PASS GTK3 file chooser rendered")
        except Exception as error:
            failures.append(error)
        finally:
            window.destroy()
            loop.quit()
        return GLib.SOURCE_REMOVE

    GLib.timeout_add(800, finish)
    loop.run()
    if failures:
        raise failures[0]
