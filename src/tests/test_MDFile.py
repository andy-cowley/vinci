import os
import shutil
import unittest
from datetime import datetime

from vinci.classes.mdfile import MDFile


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
        os.mkdir("TestNotes/meta")
        with open("TestNotes/meta/note-with-metadata.md", "x") as f:
            note_with_metadata_text = """
---
author: test
last_updated: "2020-02-03T09:59:19"
tags:
- tag1
- tag2
- tag3
title: Note with Metadata
---

# Title
Bumf
            """
            f.write(note_with_metadata_text)
            f.close()

    def tearDown(self):
        shutil.rmtree("TestNotes")

    def test_note_with_no_metadata(self):
        md_file = "TestNotes/Test Note 1/Test Note 1.md"
        note = MDFile(md_file)
        modified_date = datetime.fromtimestamp(os.stat(md_file).st_mtime)
        assert note.md.metadata["title"] == "Test Note 1.md"
        assert note.md.metadata["author"] == "No-one"
        assert note.md.metadata["tags"] == ["untagged"]
        assert datetime.fromisoformat(note.md.metadata["last_updated"]) == modified_date
        assert note.parent == "Test Note 1"
        assert note.path == ["TestNotes", "Test Note 1", "Test Note 1.md"]

    def test_note_with_metadata(self):
        md_file = "TestNotes/meta/note-with-metadata.md"
        note = MDFile(md_file)
        modified_date = "2020-02-03T09:59:19"
        assert note.md.metadata["title"] == "Note with Metadata"
        assert note.md.metadata["author"] == "test"
        assert note.md.metadata["tags"] == ["tag1", "tag2", "tag3"]
        assert note.md.metadata["last_updated"] == modified_date
        assert note.parent == "meta"
        assert note.path == ["TestNotes", "meta", "note-with-metadata.md"]

if __name__ == "__main__":
    unittest.main()
