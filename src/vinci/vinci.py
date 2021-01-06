import logging
import os

from vinci.classes import DBConnectionHandler
from vinci.functions import (
    write_default_metadata,
    update_database,
    create_tag_index,
    create_note_index,
    render_markdown,
    fetch_search_results,
    fetch_total_notes,
    fetch_all_topics,
    fetch_unlinked_notes,
)
from flask import Flask, render_template, request, send_from_directory

if os.getenv("VINCI_DEBUG"):
    logging.basicConfig(level="INFO")

DB_FILE = os.getenv("DB_FILE")
VERSION = os.getenv("VERSION")

DB_SCHEMA = """
    BEGIN TRANSACTION;
    DROP TABLE IF EXISTS "notes";
    CREATE TABLE IF NOT EXISTS "notes" (
        "name"	TEXT,
        "path"	TEXT UNIQUE,
        "id"	INTEGER,
        "parent"	TEXT DEFAULT '.',
        PRIMARY KEY("id")
    );
    DROP TABLE IF EXISTS "notes_tags";
    CREATE TABLE IF NOT EXISTS "notes_tags" (
        "id"	INTEGER,
        "note"	INTEGER,
        "tag"	INTEGER,
        PRIMARY KEY("id")
    );
    DROP TABLE IF EXISTS "notes_topics";
    CREATE TABLE IF NOT EXISTS "notes_topics" (
        "id"	INTEGER,
        "note"	INTEGER,
        "topic"	INTEGER,
        PRIMARY KEY("id")
    );
    DROP TABLE IF EXISTS "tags";
    CREATE TABLE IF NOT EXISTS "tags" (
        "id"	INTEGER,
        "tag"	TEXT UNIQUE,
        PRIMARY KEY("id")
    );
    DROP TABLE IF EXISTS "topics";
    CREATE TABLE IF NOT EXISTS "topics" (
        "id"	INTEGER,
        "topic"	TEXT UNIQUE,
        PRIMARY KEY("id")
    );
    COMMIT;
   """

if not DB_FILE:
    DB_FILE = "sqlite_debug.db"

db = DBConnectionHandler(DB_FILE)
db.commit()

write_default_metadata()

# schema_file = open("schema/vinci_schema.sql", "r")
# f = schema_file.read()

db.executescript(DB_SCHEMA)

update_database(db, db_init=True)

db.commit()

app = Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.route("/", methods=["GET"])
def all_tags():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    note_index = create_note_index(db)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "index.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        notes=note_index,
        version=VERSION,
    )


@app.route("/topics", methods=["GET"])
def index():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    topics = fetch_all_topics(db)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "topics.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        topics=topics,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        version=VERSION,
    )


@app.route("/unlinked", methods=["GET"])
def unlinked():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "unlinked.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        version=VERSION,
    )


@app.route("/tag/<string:tag_query>", methods=["GET"])
def build_note_list(tag_query):
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    note_index = create_note_index(db, tag_query)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "index.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        notes=note_index,
        version=VERSION,
    )


@app.route("/topic/<string:topic_query>", methods=["GET"])
def build_list_of_notes_from_topic(topic_query):
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    note_index = create_note_index(db, topic=topic_query)
    index_note_content = "No index note, yet..."
    metadata = {}
    for note in note_index:
        for tag in note[4]:
            if "index" in tag:
                md_file = render_markdown(db, note[2])
                index_note_content = md_file["content"]
                metadata = (md_file["metadata"],)
        unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "index.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        note_content=index_note_content,
        metadata=metadata,
        notes=note_index,
        topic=topic_query,
        version=VERSION,
    )


@app.route("/update", methods=["GET"])
def update_and_show_index():
    write_default_metadata()
    update_database(db)
    return index()


@app.route("/note/<string:note_id>", methods=["GET"])
def render_note(note_id):
    if note_id[-3:] == ".md":
        note_id = note_id.split(".")[0]
    md_file = render_markdown(db, note_id)
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "note.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        note_content=md_file["content"],
        metadata=md_file["metadata"],
        file_name=note_id,
        backlinks=md_file["backlinks"],
        version=VERSION,
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    if request.method == "POST":
        regex = request.form["search"]
        notes = fetch_search_results(db, regex)
        return render_template(
            "results.html",
            tag_index_tuple=tag_index,
            tag_index_tuple_sum=tag_index_tuple_sum,
            unlinked_notes=unlinked_notes,
            num_unlinked_notes=num_unlinked_notes,
            search_term=regex,
            notes=notes,
        )
    else:
        note_index = create_note_index(db)
        return render_template(
            "index.html",
            tag_index_tuple=tag_index,
            tag_index_tuple_sum=tag_index_tuple_sum,
            notes=note_index,
            unlinked_notes=unlinked_notes,
            num_unlinked_notes=num_unlinked_notes,
        )


@app.route("/tasks", methods=["GET"])
def tasks():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    notes = fetch_search_results(db, "\- \[.\]")
    unlinked_notes = fetch_unlinked_notes(db)
    num_unlinked_notes = len(unlinked_notes)
    return render_template(
        "tasks.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        unlinked_notes=unlinked_notes,
        num_unlinked_notes=num_unlinked_notes,
        notes=notes,
    )
