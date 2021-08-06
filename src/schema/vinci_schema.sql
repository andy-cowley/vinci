
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
