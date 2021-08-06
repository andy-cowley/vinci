# Vinci Notes

[![CircleCI](https://circleci.com/gh/andy-cowley/vinci/tree/master.svg?style=svg)](https://circleci.com/gh/andy-cowley/vinci/tree/master)

Vinci is a fast and simple markdown indexer and viewer that is designed to be run in a docker container. It started
because I couldn't find something that fitted my particular needs.

## Features

It consists of a simple Flask server that converts markdown to html on the fly, with a very light touch of styling
with Bootstrap. It also creates a simple metadata schema and prepends it to the markdown file using Frontmatter. This
metadata allows for freeform string tags which are collected by Vinci, and the associations collated in a disposable
SQLite database. This database is recreated every time Vinci starts so no need for any persistence.

There is also a simple free test search feature, backed by Ripgrep, so it's FAST. As it's Ripgrep, it also supports
Regex.

## How Do I Fly This Thing?

As above, this is designed to be run in Docker, but feel free to run it from source if you don't want to use Docker.
I've got no particular intention of smartening it up for that, so happy to receive PRs for that.

### How to Run in Docker


```bash
docker run -d -p 5000:5000 -v /path/to/your/notes/root/directory:/app/notes andycowley/vinci:latest
```

You'll then be able to see your notes at [http://localhost:5000](http://localhost:5000).

### Switches

Vinci also supports the following switches:

- `--nopen` -- By default, Vinci starts a browser instance when running outside of Docker. This switch stops that
- `--port` -- Default port is `5000`, you can choose whatever you fancy though. Don't forget to modify your `docker
run` though
- `--debug` -- Sets debug logging and Flask debug

## WARNING: Vinci Makes Changes to Your Files!

Without any ceremony, when Vinci first starts, it will query your notes for existing metadata. If it doesn't find any,
it will write the default schema at the top of your files like so:

```yaml
---
author: No-one
modified: Never
tags:
- untagged
title: <filename.md>
---
```

If it finds any existing metadata, it will try and use it, but will probably fail unless it mostly conforms to the
schema. One day, I'll make that better.

> It is strongly advised that you back up your notes directory and try it out on there first! I accept no
> responsibility for screw-ups.

### Troubleshooting Metadata

The easiest thing to do is delete any existing metadata. If you're really attached to it though, makes sure you have
a `title` field and a list of `tags` in the root of the embedded YAML. Vinci can handle that, though it will spew
warnings about missing metadata into the logs.

Again, I want to handle this better, but it works for me now...

## Contributing

Yeah, I know the code is shonky, this was a learning exercise more than anything. However, it turned out pretty nice
and quick so I thought I'd share.

I am TOTALLY accepting PRs, so go for it. I'll try and address any bugs and features if I think they're worth the time.
If you want to get in touch:

[andy.m.cowley@gmail.com]
