import os
import shutil
import unittest
from datetime import datetime

from vinci.classes.mdfile import MDFile


class BasicTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        notes = ["202004031915", "202004032004", "202008312334", "202008312335"]
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
        with open("TestNotes/meta/202005070809.md", "x") as f:
            note_with_metadata_text = """
---
created: 2020-02-03T09:59:19
modified: 2020-02-03T09:59:19
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
        md_file = "TestNotes/202004031915/202004031915.md"
        note = MDFile(md_file)
        assert note.md.metadata["title"] == "202004031915.md"
        assert note.md.metadata["tags"] == ["untagged"]
        assert note.parent == "202004031915"
        assert note.path == ["TestNotes", "202004031915", "202004031915.md"]

    def test_note_with_metadata(self):
        md_file = "TestNotes/meta/202005070809.md"
        note = MDFile(md_file)
        assert note.md.metadata["title"] == "Note with Metadata"
        assert note.md.metadata["tags"] == ["tag1", "tag2", "tag3"]
        assert note.parent == "meta"
        assert note.path == ["TestNotes", "meta", "202005070809.md"]

if __name__ == "__main__":
    unittest.main()
