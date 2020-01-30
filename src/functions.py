from classes import MDFile
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


def fetch_all_tags(db_connection):
    select_tags_string = "SELECT * from tags"
    db_connection.execute(select_tags_string)
    tags_tuples = db_connection.cursor.fetchall()
    return tags_tuples


def fetch_all_notes(db_connection):
    select_notes_string = "SELECT * from notes"
    db_connection.execute(select_notes_string)
    notes_tuples = db_connection.cursor.fetchall()
    return notes_tuples


def create_tag_index(db_connection):
    all_tags = fetch_all_tags(db_connection)
    tag_index_tuple_list = []
    for tag in all_tags:
        select_string = f"""
        SELECT * FROM notes_tags WHERE notes_tags.tag = "{tag[0]}"
        """
        db_connection.execute(select_string)
        tag_refs = db_connection.cursor.fetchall()
        tag_tuple = (tag[1], len(tag_refs))
        tag_index_tuple_list.append(tag_tuple)
    return sorted(tag_index_tuple_list, key=lambda tag: tag[0])
