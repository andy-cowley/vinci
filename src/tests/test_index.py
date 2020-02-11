import os
import shutil
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import main, app
from functions import update_database, write_default_metadata
from classes.db import DBConnectionHandler


class BasicTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        notes = ["Test Note 1", "Test Note 2", "Test Note 3", "Test Note 4"]
        os.mkdir("TestNotes")
        for note in notes:
            os.mkdir(f"TestNotes/{note}")
            with open(f"TestNotes/{note}/{note}.md", "x") as f:
                test_string = f"""
                # Heading for {note}\n
                This is a paragraph in the notes.\n
                Wibble.\n
                ## This is a sub-heading\n
                More guff.\n
                Wobble.
                """
                f.write(test_string)
                f.close()
        self.app = app.test_client()
        db = DBConnectionHandler("test_db.db")
        db.commit()

        write_default_metadata()

        schema_file = open("", "r")
        f = schema_file.read()

        db.executescript(f)

        update_database(db, db_init=True)

        db.commit()

    def tearDown(self):
        shutil.rmtree("TestNotes")

    def test_main_page(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
