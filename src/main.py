import logging
import os

from classes import DBConnectionHandler
from functions import (
    write_default_metadata,
    update_database,
    create_tag_index,
    create_note_index,
    render_markdown,
    fetch_search_results,
)
from flask import Flask, render_template, request

if os.getenv("VINCI_DEBUG"):
    logging.basicConfig(level="INFO")

DB_FILE = os.getenv("DB_FILE")

if not DB_FILE:
    DB_FILE = "sqlite_debug.db"

db = DBConnectionHandler(DB_FILE)
db.commit()

write_default_metadata()

schema_file = open("sqlite_debug.db.sql", "r")
f = schema_file.read()

db.executescript(f)

update_database(db, db_init=True)

db.commit()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = sum([tag[1] for tag in tag_index])
    note_index = create_note_index(db)
    return render_template(
        "index.html", tag_index_tuple=tag_index, tag_index_tuple_sum=tag_index_tuple_sum, notes=note_index
    )


@app.route("/tag/<string:tag_query>", methods=["GET"])
def build_note_list(tag_query):
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = sum([tag[1] for tag in tag_index])
    note_index = create_note_index(db, tag_query)
    return render_template(
        "index.html", tag_index_tuple=tag_index, tag_index_tuple_sum=tag_index_tuple_sum, notes=note_index
    )


@app.route("/update", methods=["GET"])
def update_and_show_index():
    update_database(db)
    return index()


@app.route("/note/<string:note_id>", methods=["GET"])
def render_note(note_id):
    md_file = render_markdown(db, note_id)
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = sum([tag[1] for tag in tag_index])
    return render_template(
        "note.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        note_content=md_file["content"],
        metadata=md_file["metadata"],
    )


@app.route("/search", methods=["POST"])
def search():
    regex = request.form["search"]
    notes = fetch_search_results(db, regex)
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = sum([tag[1] for tag in tag_index])
    return render_template(
        "results.html",
        tag_index_tuple=tag_index,
        tag_index_tuple_sum=tag_index_tuple_sum,
        search_term=regex,
        notes=notes,
    )


app.run(debug=True, host="0.0.0.0", port=5001)
