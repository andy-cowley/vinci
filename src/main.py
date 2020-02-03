import os

from classes import DBConnectionHandler
from functions import (
    create_markdown_list,
    write_default_metadata,
    update_database,
    create_tag_index,
    create_note_index,
)
from flask import Flask, flash, make_response, send_file, redirect, request, render_template, url_for


# -----------------------------------------------------------------------------
DB_FILE = os.getenv("DB_FILE")

if not DB_FILE:
    DB_FILE = "sqlite_debug.db"

db = DBConnectionHandler(DB_FILE)

update_database(db)

write_default_metadata()


db.commit()
#    select_string = """
#    SELECT notes.name, tags.tag
#    FROM notes
#    JOIN notes_tags
#    ON notes.id = notes_tags.note
#    JOIN tags
#    ON tags.id = notes_tags.tag
#    """

#    db.execute(select_string)
#    results = db.cursor.fetchall()

#    [print(result) for result in results]

app = Flask(__name__)
app.secret_key = "This key is required for `flash()`."


@app.route("/", methods=["GET"])
def index():
    tag_index = create_tag_index(db)
    tag_index_tuple_sum = sum([tag[1] for tag in tag_index])
    note_index = create_note_index(db)
    return render_template(
        "index.html", tag_index_tuple=tag_index, tag_index_tuple_sum=tag_index_tuple_sum, notes=note_index
    )


app.run(debug=True, host="0.0.0.0", port=5000)
