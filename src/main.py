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


def update_database(db_connection, path="."):
    markdown_file_list = create_markdown_list(path)

    for md_file in markdown_file_list:
        select_string = f"SELECT id FROM notes WHERE notes.path = '{md_file.file_obj}'"
        db_connection.execute(select_string)
        note_index = db_connection.cursor.fetchone()[0]

        if not note_index:
            insert_string = f"""
            INSERT INTO notes (name,author,path)
            VALUES(
            '{md_file.md.metadata['title']}',
            '{md_file.md.metadata['author']}',
            '{md_file.file_obj}')
            """
            db_connection.execute(insert_string)

        for tag in md_file.md.metadata["tags"]:
            select_tag_string = f"SELECT id FROM tags WHERE tags.tag = '{tag}'"
            db_connection.execute(select_tag_string)
            tag_index = db_connection.cursor.fetchone()[0]

            if not tag_index:
                insert_string = f" INSERT INTO tags (tag) VALUES ('{tag}')"
                print(insert_string)
                db_connection.execute(insert_string)

            select_join_string = f"""
            SELECT note,tag FROM notes_tags WHERE note = '{note_index}' AND tag = '{tag_index}'
            """
            db_connection.execute(select_join_string)
            join = db_connection.cursor.fetchone()

            if not join:
                insert_string = f"INSERT INTO notes_tags (note,tag) VALUES ('{note_index}','{tag_index}')"
                db_connection.execute(insert_string)


if __name__ == "__main__":
    DB_FILE = os.getenv("DB_FILE")

    if not DB_FILE:
        DB_FILE = "sqlite_debug.db"

    db = DBConnectionHandler(DB_FILE)

    update_database(db)

    write_default_metadata()

    select_string = """
    SELECT notes.name, tags.tag
    FROM notes
    JOIN notes_tags
    ON notes.id = notes_tags.note
    JOIN tags
    ON tags.id = notes_tags.tag
    """

    db.execute(select_string)
    results = db.cursor.fetchall()

    [print(result) for result in results]

    db.commit()
    db.close()
