"""ScriptEngine — a universal knowledge engine over Fandom wikis.

ScriptEngine ingests a Fandom wiki, derives its entity taxonomy from the wiki
itself, and serves ordered, cited, structured knowledge over HTTP. It does not
write scripts; it feeds the model that does.

The design rests on one observation: a Fandom wiki already publishes its own
structure through the MediaWiki API. Infobox templates name the page types,
categories label the pages, wikilinks are pre-resolved edges, and the section
tree arrives with explicit levels. Nothing about a series needs to be hardcoded,
which is why the same pipeline handles Jujutsu Kaisen and Marvel alike.
"""

__version__ = "0.1.0"
