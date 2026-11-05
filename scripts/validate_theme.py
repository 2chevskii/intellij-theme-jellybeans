"""Validate theme resources and optionally the release ZIP, using only Python's stdlib."""

import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "src/main/resources"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def resource_path(path):
    relative = PurePosixPath(path.lstrip("/"))
    require(".." not in relative.parts, f"Unsafe resource path: {path}")
    return relative.as_posix()


def validate(read, packaged=False):
    plugin = ET.fromstring(read("META-INF/plugin.xml"))
    require(plugin.tag == "idea-plugin", "Invalid plugin descriptor root")
    for tag in ("id", "name", "vendor", "description", "change-notes"):
        require(plugin.findtext(tag, "").strip(), f"Missing plugin {tag}")
    require(plugin.findtext("depends") == "com.intellij.modules.platform", "Expected platform dependency")
    if packaged:
        version = plugin.findtext("version", "")
        require(re.fullmatch(r"\d+\.\d+\.\d+", version), f"Invalid release version: {version}")
        expected = re.search(r"^pluginVersion=(.+)$", (ROOT / "gradle.properties").read_text(), re.M)[1].strip()
        require(version == expected, "Packaged version differs from gradle.properties")
        compatibility = plugin.find("idea-version")
        require(compatibility is not None and compatibility.get("since-build") == "233", "Incorrect minimum IDE build")
        require(not compatibility.get("until-build"), "Theme should have open-ended compatibility")
        require(read("META-INF/LICENSE") == (ROOT / "LICENSE").read_bytes(), "Missing or changed license")

    providers = plugin.findall("extensions/themeProvider")
    require(len(providers) == 1, "Expected exactly one theme provider")
    provider = providers[0]
    require(provider.get("id") == plugin.findtext("id"), "Theme provider ID differs from plugin ID")
    theme = json.loads(read(resource_path(provider.attrib["path"])), object_pairs_hook=unique_object)
    require(theme.get("name") and theme.get("dark") is True, "Expected named dark theme")
    colors = theme["colors"]
    for name, color in colors.items():
        require(re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", color), f"Invalid palette color {name}: {color}")

    def walk(values, prefix="ui"):
        for key, value in values.items():
            path = f"{prefix}.{key}"
            if isinstance(value, dict):
                walk(value, path)
            elif isinstance(value, str):
                if value.startswith("#"):
                    require(re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", value), f"Invalid color at {path}")
                elif not value.isdigit():
                    require(value in colors, f"Undefined palette reference at {path}: {value}")

    walk(theme["ui"])
    walk(theme.get("icons", {}).get("ColorPalette", {}), "icons.ColorPalette")
    scheme = ET.fromstring(read(resource_path(theme["editorScheme"])))
    require(scheme.tag == "scheme" and scheme.get("parent_scheme") == "Darcula", "Invalid editor scheme")
    for parent in scheme.iter():
        names = [child.get("name") for child in parent.findall("option")]
        require(len(names) == len(set(names)), f"Duplicate editor options under {parent.tag}")
    for option in scheme.findall("colors/option") + scheme.findall("attributes/option/value/option"):
        if option.get("name") in {"FONT_TYPE", "EFFECT_TYPE"}:
            continue
        value = option.get("value")
        require(value is not None and re.fullmatch(r"[0-9a-fA-F]{1,8}", value), f"Invalid editor option: {option.attrib}")
    attributes = {item.attrib["name"]: item.get("baseAttributes") for item in scheme.findall("attributes/option")}
    for name in attributes:
        seen = set()
        while name in attributes and attributes[name]:
            require(name not in seen, f"Cyclic editor inheritance: {name}")
            seen.add(name)
            name = attributes[name]
    icon = ET.fromstring(read("META-INF/pluginIcon.svg"))
    require(icon.get("viewBox") == "0 0 40 40", "Expected 40 x 40 plugin icon")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", type=Path)
    args = parser.parse_args()
    validate(lambda name: (RESOURCES / name).read_bytes())
    print("Theme resources: OK")
    if args.archive:
        with zipfile.ZipFile(args.archive) as distribution:
            entries = distribution.namelist()
            jars = [name for name in entries if name.endswith(".jar")]
            require(len(jars) == 1, f"Expected one resource JAR, found {jars}")
            require(all(name.endswith("/") or name in jars for name in entries), "Unexpected distribution files")
            with zipfile.ZipFile(io.BytesIO(distribution.read(jars[0]))) as jar:
                require(not any(name.endswith(".class") for name in jar.namelist()), "Theme must contain no executable classes")
                validate(jar.read, packaged=True)
                for path in RESOURCES.rglob("*"):
                    if path.is_file() and path.name != "plugin.xml":
                        require(jar.read(path.relative_to(RESOURCES).as_posix()) == path.read_bytes(), f"Stale packaged resource: {path}")
        print(f"Release archive: OK ({args.archive})")


if __name__ == "__main__":
    main()
