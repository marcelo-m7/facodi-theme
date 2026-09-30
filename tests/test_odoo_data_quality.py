import ast
import glob
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "theme_facodi"
MANIFEST = ast.literal_eval((ADDON / "__manifest__.py").read_text(encoding="utf-8"))
EXTERNAL_ID_TAGS = {"record", "template", "menuitem"}


class OdooDataQualityTest(unittest.TestCase):
    def test_manifest_data_files_exist_and_are_unique(self):
        paths = [*MANIFEST.get("data", []), *MANIFEST.get("demo", [])]
        duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
        self.assertFalse(duplicates, f"duplicate manifest data entries: {duplicates}")
        missing = sorted(path for path in paths if not (ADDON / path).is_file())
        self.assertFalse(missing, f"manifest references missing data files: {missing}")

    def test_manifest_xml_is_well_formed_and_external_ids_are_unique(self):
        owners = {}
        duplicates = []
        for relative_path in [*MANIFEST.get("data", []), *MANIFEST.get("demo", [])]:
            if not relative_path.endswith(".xml"):
                continue
            path = ADDON / relative_path
            root = ET.parse(path).getroot()
            for element in root.iter():
                external_id = element.attrib.get("id")
                if element.tag not in EXTERNAL_ID_TAGS or not external_id:
                    continue
                previous = owners.setdefault(external_id, relative_path)
                if previous != relative_path:
                    duplicates.append((external_id, previous, relative_path))
        self.assertFalse(
            duplicates,
            "duplicate external IDs across manifest XML files: "
            + ", ".join(
                f"{external_id} ({first}, {second})"
                for external_id, first, second in duplicates
            ),
        )

    def test_manifest_asset_sources_resolve(self):
        missing = []
        for bundle, entries in MANIFEST.get("assets", {}).items():
            for entry in entries:
                pattern = str(ROOT / entry)
                if glob.has_magic(pattern):
                    if not glob.glob(pattern, recursive=True):
                        missing.append(f"{bundle}: {entry}")
                elif not Path(pattern).is_file():
                    missing.append(f"{bundle}: {entry}")
        self.assertFalse(missing, f"manifest assets do not resolve: {missing}")


if __name__ == "__main__":
    unittest.main()
