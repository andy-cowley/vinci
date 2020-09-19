import frontmatter
import logging
import os

from datetime import datetime
from io import BytesIO
from schema import Schema, SchemaError, SchemaMissingKeyError, Optional


class MDFile:
    def __init__(self, md_file):
        self.file_obj = md_file
        self.md_file = open(md_file, "r")
        self.path = self.md_file.name.split("/")
        self.parent = self.path[-2] if len(self.path) > 1 else "."
        self.md = frontmatter.load(md_file)
        self.edited = 0

        self.schema = Schema(
            {
                "title": str,
                "tags": [str],
                "modified": datetime,
                "created": datetime,
                Optional("book"): [dict],
                Optional("web"): [str],
                Optional("backlinks"): [str]
            }
        )

        if not self.schema.is_valid(self.md.metadata):
            logging.warning(f"Invalid metadata in {self.file_obj}")
            try:
                self.schema.validate(self.md.metadata)
            except SchemaMissingKeyError as e:
                logging.warning(e)
                missing_keys = e.args[0].replace("'", "").split(': ')[1].split(', ')
                for missing in missing_keys:
                    if missing == "created":
                        self.md.metadata["created"] = datetime.fromtimestamp(os.stat(md_file).st_ctime)
                    elif missing == "modified":
                        self.md.metadata["modified"] = datetime.fromtimestamp(os.stat(md_file).st_mtime)
                    elif missing == "tags":
                        self.md.metadata["tags"] = ["untagged"]
                    elif missing == "title":
                        self.md.metadata["title"] = self.path[-1]
                    self.edited = 1
            except SchemaError as e:
                logging.warning(e)
                wrong_key = e.args[0].split("'")[1]
                if wrong_key == "created":
                    self.md.metadata["created"] = datetime.fromtimestamp(os.stat(md_file).st_ctime)
                elif wrong_key == "modified":
                    self.md.metadata["modified"] = datetime.fromtimestamp(os.stat(md_file).st_mtime)
                self.edited = 1
        if self.edited:
            self.write()
        self.md_file.close()

    def write(self):
        if self.edited:
            with open(self.file_obj, "w+") as out_file:
                f = BytesIO()
                frontmatter.dump(self.md, f)
                out_file.write(f.getvalue().decode("utf-8"))
        else:
            logging.info(f"Nothing to write: {self.file_obj}")

    def __repr__(self):
        return self.md_file.name
