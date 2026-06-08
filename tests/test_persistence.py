import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "app.py"


spec = importlib.util.spec_from_file_location("app_module", MODULE_PATH)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


class PersistenceTests(unittest.TestCase):
    def test_load_activities_reads_from_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "activities.json"
            expected = {"Sample Activity": {"description": "desc", "schedule": "now", "max_participants": 5, "participants": ["a@example.com"]}}
            data_file.write_text(json.dumps(expected), encoding="utf-8")

            original = app_module.DATA_FILE
            app_module.DATA_FILE = data_file
            try:
                loaded = app_module.load_activities()
            finally:
                app_module.DATA_FILE = original

            self.assertEqual(loaded, expected)

    def test_signup_persists_changes_to_disk(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "activities.json"
            initial = {
                "Chess Club": {
                    "description": "Learn strategies",
                    "schedule": "Fridays",
                    "max_participants": 12,
                    "participants": ["existing@example.com"],
                }
            }
            data_file.write_text(json.dumps(initial), encoding="utf-8")

            original_data_file = app_module.DATA_FILE
            original_activities = app_module.activities
            app_module.DATA_FILE = data_file
            app_module.activities = app_module.load_activities()
            try:
                app_module.signup_for_activity("Chess Club", "new@example.com")
                saved = json.loads(data_file.read_text(encoding="utf-8"))
            finally:
                app_module.DATA_FILE = original_data_file
                app_module.activities = original_activities

            self.assertIn("new@example.com", saved["Chess Club"]["participants"])


if __name__ == "__main__":
    unittest.main()
