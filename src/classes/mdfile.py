import frontmatter
import logging

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
            print(f"Invalid metadata in {self.file_obj}")
            try:
                self.schema.validate(self.md.metadata)
            except SchemaError as e:
                logging.warning(e)

        self.md_file.close()

    def write(self):
        if self.edited:
            with open(self.file_obj, "w+") as out_file:
                f = BytesIO()
                frontmatter.dump(self.md, f)
                out_file.write(f.getvalue().decode("utf-8"))
        else:
            logging.info("Nothing to write:", self.file_obj)

    def __repr__(self):
        return self.md_file.name
