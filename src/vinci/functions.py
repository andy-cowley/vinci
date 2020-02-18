import logging
import pypandoc
from vinci.classes import MDFile
from pathlib import Path, PurePath
from ripgrepy import Ripgrepy


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


def update_database(db_connection, path=".", db_init=False):
    markdown_file_list = create_markdown_list(path)
    note_index_list = []

    for md_file in markdown_file_list:
        select_string = f"SELECT id FROM notes WHERE notes.path = '{md_file.file_obj}'"
        db_connection.execute(select_string)
        note_index = db_connection.cursor.fetchone()

        if not note_index:
            insert_string = f"""
            INSERT INTO notes (name,author,path,parent)
            VALUES(
            '{md_file.md.metadata['title']}',
            '{md_file.md.metadata['author']}',
            '{md_file.file_obj}',
            '{md_file.parent}')
            """
            db_connection.execute(insert_string)
        else:
            update_string = f"""
            UPDATE notes
            SET
            name = '{md_file.md.metadata['title']}',
            author = '{md_file.md.metadata['author']}',
            parent = '{md_file.parent}'
            WHERE path = '{md_file.file_obj}'
            """
            db_connection.execute(update_string)

        select_string = f"SELECT id FROM notes WHERE notes.path = '{md_file.file_obj}'"
        db_connection.execute(select_string)
        note_index = db_connection.cursor.fetchone()[0]
        note_index_list.append(note_index)

        tag_index_list = []
        for tag in md_file.md.metadata["tags"]:
            select_tag_string = f"SELECT id FROM tags WHERE tags.tag = '{tag}'"
            db_connection.execute(select_tag_string)
            tag_index = db_connection.cursor.fetchone()
            if tag_index:
                tag_index_list.append(tag_index[0])

            if not tag_index:
                insert_string = f" INSERT INTO tags (tag) VALUES ('{tag}')"
                db_connection.execute(insert_string)
                select_tag_string = f"SELECT id FROM tags WHERE tags.tag = '{tag}'"
                db_connection.execute(select_tag_string)
                tag_index = db_connection.cursor.fetchone()

            select_join_string = f"""
            SELECT note,tag FROM notes_tags WHERE note = '{note_index}' AND tag = '{tag_index[0]}'
            """
            db_connection.execute(select_join_string)
            join = db_connection.cursor.fetchone()

            if not join:
                insert_string = f"INSERT INTO notes_tags (note,tag) VALUES ('{note_index}','{tag_index[0]}')"
                db_connection.execute(insert_string)

        # Remove associations for removed/not present tags
        tag_index_list = ",".join([f"{tag}" for tag in tag_index_list])
        select_join_string = f"""
        DELETE FROM notes_tags
        WHERE notes_tags.note = '{note_index}'
        AND notes_tags.tag NOT IN ({tag_index_list})"""
        db_connection.execute(select_join_string)

    if not db_init:
        # Remove all associations for deleted notes
        note_index_list = ",".join([f"{note}" for note in note_index_list])
        delete_join_string = f"DELETE FROM notes_tags WHERE notes_tags.note NOT IN ({note_index_list})"
        db_connection.execute(delete_join_string)
        delete_note_string = f"DELETE FROM notes WHERE notes.id NOT IN ({note_index_list})"
        db_connection.execute(delete_note_string)
    else:
        logging.info("Database initialisation complete")
        update_database(db_connection)


def fetch_all_tags(db_connection):
    select_tags_string = "SELECT * from tags"
    db_connection.execute(select_tags_string)
    tags_tuples = db_connection.cursor.fetchall()
    return tags_tuples


def fetch_all_notes(db_connection):
    select_notes_string = "SELECT * from notes"
    db_connection.execute(select_notes_string)
    all_notes_tuples = db_connection.cursor.fetchall()
    notes_tuples = []
    for note in all_notes_tuples:
        join_string = f"""
        SELECT tags.tag
        FROM notes_tags
        JOIN tags ON tags.id = notes_tags.tag
        WHERE notes_tags.note = {note[3]}
        """
        db_connection.execute(join_string)
        tag_list = list(db_connection.cursor.fetchall())
        note_tuple = note + (tag_list,)
        notes_tuples.append(note_tuple)

    return notes_tuples


def fetch_one_note(db_connection, note_path=None, note_id=None):
    print(note_path)
    if note_path and note_id:
        raise ValueError(
            f"""fetch_one_note() cannot handle id and path at the same time:
            note_path = {note_path}, note_tag = {note_id}"""
        )
    elif note_path:
        select_note_string = f"SELECT * FROM notes WHERE notes.path = '{note_path}'"
    elif note_id:
        select_note_string = f"SELECT * FROM notes WHERE notes.id = '{note_id}'"
    else:
        raise ValueError(f"""Exactly one of note_path or note_id must be passed to this function.""")
    db_connection.execute(select_note_string)
    note = db_connection.cursor.fetchone()
    join_string = f"""
    SELECT tags.tag
    FROM notes_tags
    JOIN tags ON tags.id = notes_tags.tag
    WHERE notes_tags.note = "{note[3]}"
    """
    db_connection.execute(join_string)
    tag_list = list(db_connection.cursor.fetchall())
    print("debug", note, tag_list)
    note_tuple = note + (tag_list,)
    return note_tuple


def fetch_tagged_notes(db_connection, tag_id):
    select_string = f"SELECT note FROM notes_tags WHERE tag = '{tag_id}'"
    db_connection.execute(select_string)
    note_id_list = db_connection.cursor.fetchall()
    note_id_list = [note[0] for note in note_id_list]
    notes_tuples = []
    for note in note_id_list:
        select_string = f"""
        SELECT name,author,path,id,parent
        FROM notes
        WHERE id = '{note}'
        """
        db_connection.execute(select_string)
        note_tuple_no_tag = db_connection.cursor.fetchone()
        join_string = f"""
        SELECT tags.tag
        FROM notes_tags
        JOIN tags ON tags.id = notes_tags.tag
        WHERE notes_tags.note = {note}
        """
        db_connection.execute(join_string)
        tag_list = list(db_connection.cursor.fetchall())
        note_tuple = note_tuple_no_tag + (tag_list,)

        notes_tuples.append(note_tuple)
    return notes_tuples


def fetch_total_notes(db_connection):
    count_string = "SELECT COUNT(*) FROM notes"
    db_connection.execute(count_string)
    count_total = db_connection.cursor.fetchone()[0]
    return count_total


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


def create_note_index(db_connection, tag=None):
    if not tag:
        notes = fetch_all_notes(db_connection)
    else:
        select_string = f"SELECT id FROM tags WHERE tag = '{tag}'"
        db_connection.execute(select_string)
        tag_id = db_connection.cursor.fetchone()
        tag_id = tag_id[0]
        notes = fetch_tagged_notes(db_connection, tag_id)
        notes = sorted(notes, key=lambda note: note[4])

    return notes


def render_markdown(db_connection, note_id):
    select_string = f"""
    SELECT path FROM notes WHERE id={note_id}
    """
    db_connection.execute(select_string)
    note_path = Path(db_connection.cursor.fetchone()[0])
    note = MDFile(note_path)
    content = pypandoc.convert_text(note.md.content, to="html5", format="md")
    output = {"metadata": note.md.metadata, "content": content}
    return output


def text_search(regex, path="."):
    rg = Ripgrepy(regex, path)
    files_and_lines = rg.with_filename().line_number().run().as_string.split("\n")
    result = [tuple(item.split(":")) for item in files_and_lines if item.split(":")[0][-3:] == '.md']
    return result


def fetch_search_results(db_connection, regex, path="./**/*"):
    notes = []
    search_results = text_search(regex, path)
    print(search_results)
    for sr in search_results:
        note_tuple = fetch_one_note(db_connection, note_path=sr[0][2:])
        if "- [x] " in sr[2]:
            result_as_html = f"<input type='checkbox' disabled checked> {sr[2][5:]}"
        elif "- [ ] " in sr[2]:
            result_as_html = f"<input type='checkbox' disabled> {sr[2][5:]}"
        else:
            result_as_html = sr[2]
        note = note_tuple + (sr[1],) + (result_as_html,)
        notes.append(note)
    return notes
