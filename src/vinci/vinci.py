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
    fetch_total_notes)
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

#schema_file = open("schema/vinci_schema.sql", "r")
#f = schema_file.read()

db.executescript(DB_SCHEMA)

update_database(db, db_init=True)

db.commit()

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/", methods=["GET"])
def index():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    note_index = create_note_index(db)
    return render_template(
        "index.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        notes=note_index,
        version=VERSION,
    )


@app.route("/tag/<string:tag_query>", methods=["GET"])
def build_note_list(tag_query):
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    note_index = create_note_index(db, tag_query)
    return render_template(
        "index.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        notes=note_index,
        version=VERSION,
    )


@app.route("/update", methods=["GET"])
def update_and_show_index():
    write_default_metadata()
    update_database(db)
    return index()


@app.route("/note/<string:note_id>", methods=["GET"])
def render_note(note_id):
    if note_id[-3:] == '.md':
        note_id = note_id.split('.')[0]
    md_file = render_markdown(db, note_id)
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    return render_template(
        "note.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        note_content=md_file["content"],
        metadata=md_file["metadata"],
        backlinks=md_file["backlinks"],
        version=VERSION,
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    if request.method == "POST":
        regex = request.form["search"]
        notes = fetch_search_results(db, regex)
        return render_template(
            "results.html",
            tag_index_tuple=tag_index,
            tag_index_tuple_sum=tag_index_tuple_sum,
            search_term=regex,
            notes=notes,
        )
    else:
        note_index = create_note_index(db)
        return render_template(
            "index.html", tag_index_tuple=tag_index, tag_index_tuple_sum=tag_index_tuple_sum, notes=note_index
        )


@app.route("/tasks", methods=["GET"])
def tasks():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    notes = fetch_search_results(db, "\- \[.\]")
    return render_template(
        "tasks.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        notes=notes,
    )
