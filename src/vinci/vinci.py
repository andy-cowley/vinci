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

if not DB_FILE:
    DB_FILE = "sqlite_debug.db"

db = DBConnectionHandler(DB_FILE)
db.commit()

write_default_metadata()

schema_file = open("schema/vinci_schema.sql", "r")
f = schema_file.read()

db.executescript(f)

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
    update_database(db)
    return index()


@app.route("/note/<string:note_id>", methods=["GET"])
def render_note(note_id):
    md_file = render_markdown(db, note_id)
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = fetch_total_notes(db)
    return render_template(
        "note.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        note_content=md_file["content"],
        metadata=md_file["metadata"],
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


