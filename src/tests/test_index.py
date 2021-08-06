import os
import shutil
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import main, app
from vinci.functions import update_database, write_default_metadata
from vinci.classes.db import DBConnectionHandler
from vinci.classes.mdfile import MDFile

@pytest.fixture
def setUp():
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
            print(note)
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

    db = DBConnectionHandler("test_db.db")
    db.commit()

    write_default_metadata()

    schema_file = open("src/schema/vinci_schema.sql", "r")
    f = schema_file.read()

    db.executescript(f)

    update_database(db, db_init=True)

    db.commit()
    yield setUp
    shutil.rmtree("TestNotes")
    os.remove("test_db.db")

def test_main_page(setUp):
    test_client = app.test_client()
    response = test_client.get("/", follow_redirects=True)
    assert response.status_code == 200

def test_basic_web_server_paths(setUp):
    test_client = app.test_client()
    index_response = test_client.get('/', follow_redirects=True)
    search_response = test_client.get('/search', follow_redirects=True)
    update_response = test_client.get('/update', follow_redirects=True)
    tag_response = test_client.get('/tag/untagged', follow_redirects=True)
    note_response = test_client.get('/note/202004032004', follow_redirects=True)
    assert index_response.status_code == 200
    assert search_response.status_code == 200
    assert update_response.status_code == 200
    assert tag_response.status_code == 200
    assert note_response.status_code == 200

def test_note_with_no_metadata(setUp):
    md_file = "TestNotes/202004031915.md"
    note = MDFile(md_file)
    assert note.md.metadata["title"] == "202004031915.md"
    assert note.md.metadata["tags"] == ["untagged"]
    assert note.parent == "TestNotes"
    assert note.path == ["TestNotes", "202004031915.md"]

def test_note_with_metadata(setUp):
    md_file = "TestNotes/meta/202005070809.md"
    note = MDFile(md_file)
    assert note.md.metadata["title"] == "Note with Metadata"
    assert note.md.metadata["tags"] == ["tag1", "tag2", "tag3"]
    assert note.parent == "meta"
    assert note.path == ["TestNotes", "meta", "202005070809.md"]
