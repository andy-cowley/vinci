import os

from classes import DBConnectionHandler, MDFile
from pathlib import Path, PurePath


def create_markdown_list(path_string):
    """Returns a list of MDFile objects from markdown files recursively"""
    p = Path(path_string)
    all_markdown = list(p.glob("**/*.md"))
    all_markdown_as_string = [str(PurePath(x)) for x in all_markdown]
    markdown_file_list = [MDFile(x) for x in all_markdown_as_string]
    return markdown_file_list


def write_default_metadata(path="."):
    markdown_file_list = create_markdown_list(path)
    [md_file.write() for md_file in markdown_file_list]


if __name__ == "__main__":
    DB_FILE = os.getenv("DB_FILE")

    if not DB_FILE:
        DB_FILE = "sqlite_debug.db"

    db = DBConnectionHandler(DB_FILE)

    join_string = """
    SELECT notes.name, tags.tag
    FROM notes
    JOIN notes_tags
    ON notes.id = notes_tags.note
    JOIN tags
    ON tags.id = notes_tags.tag
    """

    db.execute(join_string)

    result = [row for row in db.cursor]

    print(result)

    write_default_metadata()

    db.commit()
    db.close()
