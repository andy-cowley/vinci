import os
import shutil
import unittest

from vinci.vinci import app


class BasicTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        self.app = app.test_client()

        notes = ["202004031915", "202004032004", "202008312334", "202008312335"]
        os.mkdir("TestNotes")
        for note in notes:
            with open(f"TestNotes/{note}.md", "x") as f:
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
        with open("TestNotes/202005070809.md", "x") as f:
            note_with_metadata_text = """
---
created: 2020-02-03T09:59:19
modified: 2020-02-03T09:59:19
tags:
- tag1
- Tag2

- tag3
title: Note with Metadata
---

# Title
Bumf
            """
            f.write(note_with_metadata_text)
            f.close()

    def tearDown(self):
        #
        shutil.rmtree("TestNotes")
        os.remove("sqlite_debug.db")

    def test_basic_web_server_paths(self):
        index_response = self.app.get('/', follow_redirects=True)
        search_response = self.app.get('/search', follow_redirects=True)
        update_response = self.app.get('/update', follow_redirects=True)
        tag_response = self.app.get('/tag/untagged', follow_redirects=True)
        note_response = self.app.get('/note/202005070809', follow_redirects=True)
        self.assertEqual(index_response.status_code, 200)
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(tag_response.status_code, 200)
        self.assertEqual(note_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
