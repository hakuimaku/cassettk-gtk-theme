#!/usr/bin/env python3
"""Install the Cassettk GTK theme without changing desktop settings."""
import argparse
import os
from pathlib import Path
import re
import shutil
import tempfile
from materialize import ROOT, SOURCE, VARIANTS, materialize


def install(theme_root):
    """Stage Cassettk and restore the previous installation on replacement failure."""
    root = Path(theme_root).expanduser().resolve()
    for name in VARIANTS.values():
        target = root / name
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError(f"Refusing to replace a symlink or file: {target}")
        if target.exists():
            metadata = target / "index.theme"
            if metadata.is_symlink() or not metadata.is_file() or f"GtkTheme={name}" not in metadata.read_text().splitlines():
                raise ValueError(f"Refusing to replace an unrecognized directory: {target}")
        for source in (SOURCE, ROOT / "themes"):
            if target == source or target in source.parents or source in target.parents:
                raise ValueError("Installation destination must be outside the theme source")

    with tempfile.TemporaryDirectory(prefix="cassettk-build-") as generated:
        materialize(generated)
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".cassettk-install-", dir=root) as staging:
            for name in VARIANTS.values():
                staged = Path(staging) / name
                target = root / name
                shutil.copytree(Path(generated) / name, staged)
                for css in staged.rglob("*.css"):
                    def installed_url(match):
                        resource = (css.parent / match[1]).resolve(strict=True).relative_to(staged)
                        return f'url("{(target / resource).as_uri()}")'
                    css.write_text(re.sub(r'url\("([^\"]+)"\)', installed_url, css.read_text()))
            backup = Path(tempfile.mkdtemp(prefix=".Cassettk-backup-", dir=root))
            replaced = []
            try:
                for name in VARIANTS.values():
                    target = root / name
                    if target.exists():
                        target.rename(backup / name)
                    (Path(staging) / name).rename(target)
                    replaced.append(target)
            except OSError:
                for target in reversed(replaced):
                    shutil.rmtree(target)
                for previous in backup.iterdir():
                    previous.rename(root / previous.name)
                backup.rmdir()
                raise
            if not any(backup.iterdir()):
                backup.rmdir()
                backup = None
    return root / "Cassettk", backup / "Cassettk" if backup else None


def main():
    default = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "themes"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=default, help="theme root (default: XDG user themes)")
    args = parser.parse_args()
    try:
        target, backup = install(args.dest)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Install failed: {error}\n")
    print(f"Installed {target}")
    if backup:
        print(f"Previous installation preserved at {backup.parent}")
    print("Desktop settings, user CSS, icons, fonts and cursors were not changed.")


if __name__ == "__main__":
    main()
