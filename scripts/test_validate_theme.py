"""Regression checks for errors that XML/JSON parsing alone cannot detect."""

import unittest

from validate_theme import RESOURCES, unique_object, validate


class ValidationTests(unittest.TestCase):
    def read(self, name):
        return (RESOURCES / name).read_bytes()

    def replacing(self, path, old, new):
        def read(name):
            data = self.read(name)
            return data.replace(old, new) if name == path else data
        return read

    def test_current_resources(self):
        validate(self.read)

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            unique_object([("background", "#ffffff"), ("background", "#000000")])

    def test_undefined_palette_reference(self):
        read = self.replacing("themes/jellybeans.theme.json", b'"background": "primaryBackground"', b'"background": "typoColor"')
        with self.assertRaisesRegex(ValueError, "Undefined palette reference"):
            validate(read)

    def test_duplicate_editor_option(self):
        read = self.replacing("themes/jellybeans.xml", b'<colors>', b'<colors><option name="CARET_COLOR" value="ffffff"/>')
        with self.assertRaisesRegex(ValueError, "Duplicate editor options"):
            validate(read)

    def test_missing_editor_scheme(self):
        read = self.replacing("themes/jellybeans.theme.json", b'/themes/jellybeans.xml', b'/themes/missing.xml')
        with self.assertRaises(FileNotFoundError):
            validate(read)

    def test_cyclic_editor_inheritance(self):
        read = self.replacing("themes/jellybeans.xml", b'baseAttributes="DEFAULT_METADATA"', b'baseAttributes="ANNOTATION_NAME_ATTRIBUTES"')
        with self.assertRaisesRegex(ValueError, "Cyclic editor inheritance"):
            validate(read)


if __name__ == "__main__":
    unittest.main()
