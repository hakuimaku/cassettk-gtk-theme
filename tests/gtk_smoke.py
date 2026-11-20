"""Parse Cassettk CSS and render real GTK3, GTK4, and libadwaita widgets."""
from pathlib import Path
import sys
import os

import gi

mode, output = sys.argv[1:]
version = "4.0" if mode.startswith("4.0") else mode
gi.require_version("Gtk", version)
from gi.repository import Gio, GLib, Gtk

ROOT = Path(__file__).resolve().parents[1]
theme_name = os.environ.get("GTK_THEME", "Cassettk").split(":")[0]
base = 0xE8 / 255
errors = []
providers = []

if version == "3.0":
    if not Gtk.init_check()[0]:
        raise SystemExit("A GTK display is required; use tests/run_checks.py for isolated Broadway tests")
else:
    if not Gtk.init_check():
        raise SystemExit("A GTK display is required; use tests/run_checks.py for isolated Broadway tests")

for name in ("gtk.css", "gtk-dark.css"):
    provider = Gtk.CssProvider()
    provider.connect(
        "parsing-error",
        lambda p, section, error: errors.append(
            f"{section.get_file().get_path()}:{section.get_start_location().lines + 1}: {error.message}"
        ),
    )
    provider.load_from_path(str(ROOT / f"themes/{theme_name}" / f"gtk-{version}" / name))
    providers.append(provider)
assert not errors, errors


def build_gtk3():
    window = Gtk.Window(title="Cassettk — GTK 3.0 widgets")
    window.set_default_size(760, 650)
    hb = Gtk.HeaderBar()
    hb.set_show_close_button(False)
    hb.set_title("Cassettk — GTK 3.0")
    for sym in ("_", "□", "X"):
        b = Gtk.Button(label=sym)
        b.get_style_context().add_class("titlebutton")
        hb.pack_end(b)
    window.set_titlebar(hb)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    for side in ("top", "bottom", "start", "end"):
        getattr(box, f"set_margin_{side}")(12)

    def add(parent, child):
        parent.add(child)
        return child

    window.add(box)
    add(box, Gtk.Label(label="Cassettk · Win9x-inspired beveled gray surfaces", xalign=0))
    buttons = add(box, Gtk.Box(spacing=8))
    add(buttons, Gtk.Button(label="Normal"))
    focused = add(buttons, Gtk.Button(label="Keyboard focus"))
    checked = add(buttons, Gtk.ToggleButton(label="Checked"))
    checked.set_active(True)
    disabled = add(buttons, Gtk.Button(label="Disabled"))
    disabled.set_sensitive(False)
    entry = add(box, Gtk.Entry(text="Editable location / filename"))
    entry.set_placeholder_text("Location")
    controls = add(box, Gtk.Box(spacing=8))
    check = add(controls, Gtk.CheckButton(label="Checked"))
    check.set_active(True)
    mixed = add(controls, Gtk.CheckButton(label="Mixed"))
    mixed.set_inconsistent(True)
    radio = add(controls, Gtk.RadioButton(label="Radio"))
    radio.set_active(True)
    switch = add(controls, Gtk.Switch())
    switch.set_active(True)
    add(controls, Gtk.SpinButton.new_with_range(0, 100, 1))
    scale = add(box, Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1))
    scale.set_value(45)
    progress = add(box, Gtk.ProgressBar())
    progress.set_fraction(0.65)
    progress.set_show_text(True)
    notebook = add(box, Gtk.Notebook())
    notebook.append_page(Gtk.Label(label="Active tab content"), Gtk.Label(label="Files"))
    notebook.append_page(Gtk.Label(label="Second tab content"), Gtk.Label(label="Details"))
    listing = add(box, Gtk.ListBox())
    for title in ("Idle row", "Selected row", "A long filename remains readable in the view"):
        add(listing, Gtk.Label(label=title, xalign=0))
    listing.select_row(listing.get_row_at_index(1))

    model = Gtk.ListStore(str, str)
    model.append(["Detailed list", "Readable cell renderer"])
    model.append(["Selected file", "High-contrast selection"])
    tree = add(box, Gtk.TreeView(model=model))
    for i, title in enumerate(("Name", "Description")):
        tree.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i))
    tree.get_selection().select_path(Gtk.TreePath.new_from_indices([1]))

    scroller = add(box, Gtk.ScrolledWindow())
    scroller.set_min_content_height(70)
    text = Gtk.TextView()
    text.get_buffer().set_text("Scrollable text\n" * 30)
    scroller.add(text)

    menu_button = add(box, Gtk.MenuButton(label="Popover menu"))
    menu = Gio.Menu()
    menu.append("Menu action", "app.example")
    popover = Gtk.Popover.new_from_model(menu_button, menu)
    menu_button.set_popover(popover)
    focused.grab_focus()
    window.show_all()
    return window


def build_gtk4():
    window = Gtk.Window(title="Cassettk — GTK 4.0 widgets")
    window.set_default_size(760, 650)
    hb = Gtk.HeaderBar()
    hb.set_show_title_buttons(False)
    title_lbl = Gtk.Label(label="Cassettk — GTK 4.0")
    title_lbl.add_css_class("title")
    hb.set_title_widget(title_lbl)
    for sym in ("_", "□", "X"):
        b = Gtk.Button(label=sym)
        b.add_css_class("titlebutton")
        hb.pack_end(b)
    window.set_titlebar(hb)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    for side in ("top", "bottom", "start", "end"):
        getattr(box, f"set_margin_{side}")(12)

    def add(parent, child):
        parent.append(child)
        return child

    window.set_child(box)
    add(box, Gtk.Label(label="Cassettk · Win9x-inspired beveled gray surfaces", xalign=0))
    buttons = add(box, Gtk.Box(spacing=8))
    add(buttons, Gtk.Button(label="Normal"))
    focused = add(buttons, Gtk.Button(label="Keyboard focus"))
    checked = add(buttons, Gtk.ToggleButton(label="Checked"))
    checked.set_active(True)
    disabled = add(buttons, Gtk.Button(label="Disabled"))
    disabled.set_sensitive(False)
    entry = add(box, Gtk.Entry())
    entry.set_text("Editable location / filename")
    entry.set_placeholder_text("Location")
    controls = add(box, Gtk.Box(spacing=8))
    check = add(controls, Gtk.CheckButton(label="Checked"))
    check.set_active(True)
    mixed = add(controls, Gtk.CheckButton(label="Mixed"))
    mixed.set_inconsistent(True)
    radio_a = add(controls, Gtk.CheckButton(label="Radio"))
    radio_b = Gtk.CheckButton(label="Other")
    radio_b.set_group(radio_a)
    radio_a.set_active(True)
    switch = add(controls, Gtk.Switch())
    switch.set_active(True)
    add(controls, Gtk.SpinButton.new_with_range(0, 100, 1))
    scale = add(box, Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1))
    scale.set_value(45)
    progress = add(box, Gtk.ProgressBar())
    progress.set_fraction(0.65)
    progress.set_show_text(True)
    notebook = add(box, Gtk.Notebook())
    notebook.append_page(Gtk.Label(label="Active tab content"), Gtk.Label(label="Files"))
    notebook.append_page(Gtk.Label(label="Second tab content"), Gtk.Label(label="Details"))
    listing = add(box, Gtk.ListBox())
    for title in ("Idle row", "Selected row", "A long filename remains readable in the view"):
        listing.append(Gtk.Label(label=title, xalign=0))
    listing.select_row(listing.get_row_at_index(1))

    scroller = add(box, Gtk.ScrolledWindow())
    scroller.set_min_content_height(70)
    text = Gtk.TextView()
    text.get_buffer().set_text("Scrollable text\n" * 30)
    scroller.set_child(text)

    menu_button = add(box, Gtk.MenuButton(label="Popover menu"))
    menu = Gio.Menu()
    menu.append("Menu action", "app.example")
    menu_button.set_menu_model(menu)
    window.present()
    focused.grab_focus()
    return window


def build_adw():
    gi.require_version("Adw", "1")
    from gi.repository import Adw

    Adw.init()
    window = Adw.ApplicationWindow(title="Cassettk — libadwaita")
    window.set_default_size(640, 480)
    display = window.get_display()
    for provider in providers:
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    toolbar_view = Adw.ToolbarView()
    hb = Adw.HeaderBar()
    toolbar_view.add_top_bar(hb)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    for side in ("top", "bottom", "start", "end"):
        getattr(box, f"set_margin_{side}")(16)

    group = Adw.PreferencesGroup(title="Cassettk libadwaita (level b)")
    row = Adw.ActionRow(title="Action row", subtitle="Gray palette override")
    group.add(row)
    sw = Adw.SwitchRow(title="Switch row")
    sw.set_active(True)
    group.add(sw)
    box.append(group)

    actions = Gtk.Box(spacing=8)
    suggested = Gtk.Button(label="Suggested")
    suggested.add_css_class("suggested-action")
    actions.append(suggested)
    destructive = Gtk.Button(label="Destructive")
    destructive.add_css_class("destructive-action")
    actions.append(destructive)
    box.append(actions)

    toolbar_view.set_content(box)
    window.set_content(toolbar_view)
    window.present()
    return window


def render_gtk4_png(window, paintable, path):
    from gi.repository import Graphene, Gsk
    from PIL import Image

    w, h = window.get_width(), window.get_height()
    snapshot = Gtk.Snapshot.new()
    paintable.snapshot(snapshot, w, h)
    node = snapshot.to_node()
    assert node is not None, f"Empty snapshot for {w}x{h}"
    renderer = Gsk.CairoRenderer.new()
    renderer.realize(None)
    try:
        rect = Graphene.Rect().init(0, 0, w, h)
        texture = renderer.render_texture(node, rect)
        texture.save_to_png(path)
    finally:
        renderer.unrealize()

    im = Image.open(path).convert("RGB")
    header_px = im.getpixel((10, 10))
    assert header_px == (0x1B, 0x3B, 0x7A), f"Expected headerbar #1b3b7a, got {header_px}"
    if mode == "4.0":
        bg_px = im.getpixel((6, 60))
        assert bg_px == (0xE8, 0xE8, 0xE8), f"Expected window_bg #e8e8e8, got {bg_px}"
    else:
        bg_px = im.getpixel((6, 80))
        assert bg_px == (0xE8, 0xE8, 0xE8), f"Expected Adw window_bg #e8e8e8, got {bg_px}"


if mode == "3.0":
    window = build_gtk3()
    paintable = None
elif mode == "4.0":
    window = build_gtk4()
    paintable = Gtk.WidgetPaintable.new(window)
elif mode == "4.0-adw":
    window = build_adw()
    paintable = Gtk.WidgetPaintable.new(window)
else:
    raise SystemExit(f"Unsupported mode: {mode}")

loop = GLib.MainLoop()
failure = []


def finish():
    try:
        assert not errors, errors
        if version == "3.0":
            import cairo
            bg = window.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
            assert abs(bg.red - base) < 0.01 and bg.red == bg.green == bg.blue, bg
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, window.get_allocated_width(), window.get_allocated_height()
            )
            window.draw(cairo.Context(surface))
            surface.write_to_png(output)
        else:
            render_gtk4_png(window, paintable, output)
        print(f"GTK {mode}: CSS parsed; widget render and assertions passed")
    except Exception as error:
        failure.append(error)
    finally:
        window.destroy()
        loop.quit()
    return GLib.SOURCE_REMOVE


GLib.timeout_add(500, finish)
loop.run()
if failure:
    raise failure[0]
