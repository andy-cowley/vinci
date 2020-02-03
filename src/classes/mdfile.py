import frontmatter
import logging
import os

from datetime import datetime
from io import BytesIO
from schema import Schema, SchemaError


class MDFile:
    def __init__(self, md_file):
        self.file_obj = md_file
        self.md_file = open(md_file, "r")
        self.path = self.md_file.name.split("/")
        self.parent = self.path[-2] if len(self.path) > 1 else "."
        self.md = frontmatter.load(md_file)
        self.edited = 0

        self.schema = Schema({"title": str, "author": str, "tags": [str], "last_updated": str})

        if len(self.md.metadata) == 0:
            self.md.metadata["title"] = self.path[-1]
            self.md.metadata["author"] = "No-one"
            self.md.metadata["tags"] = ["untagged"]
            self.md.metadata["last_updated"] = "never"
            self.edited = 1

        if not self.schema.is_valid(self.md.metadata):
            logging.warning(f"Invalid metadata in {self.file_obj}")
            try:
                self.schema.validate(self.md.metadata)
            except SchemaError as e:
                logging.warning(e)

        modified_date = datetime.fromtimestamp(os.stat(md_file).st_mtime)
        # Not having a 'last_updated' tag was problematic so this is a hacky way to ensure it's there
        # and easier than parsing the schema validation error. This is mostly an issue with how I had my notes though
        # And probably unnecessary.
        if "last_updated" not in self.md.metadata:
            self.md.metadata["last_updated"] = datetime.isoformat(modified_date)
        elif self.md.metadata["last_updated"] == "never":
            self.md.metadata["last_updated"] = datetime.isoformat(modified_date)
        last_updated_property = datetime.fromisoformat(self.md.metadata["last_updated"])
        if last_updated_property > modified_date:
            self.md.metadata["last_updated"] = datetime.isoformat(modified_date)

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
