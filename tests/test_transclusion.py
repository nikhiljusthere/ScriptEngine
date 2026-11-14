"""Reading an article's infobox from the page it is transcluded from.

Some wikis keep each article's infobox on a page of its own, and the article
says only `{{Infobox}}`. Measured on the first wiki crawled that works this way,
1,453 of 7,794 articles stored zero facts, every character page among them,
because the ten characters the crawler fetched were all there was to parse.

The same wiki links through its redirects (`[[Sasuke]]`, not `[[Sasuke
Uchiha|Sasuke]]`), and no page had ever recorded which titles redirect to it:
67.4% of its links resolved, against a 70% floor.

Everything here runs without the network. What the wiki returns is its
business; which pages are asked for, what is spliced where, and what a request
that fails does to the batch are this project's, and that is what these cover.
"""

from __future__ import annotations

import asyncio

import pytest

from scriptengine.config import Settings, SeriesPaths
from scriptengine.ingest.crawler import FetchFailed, WikiCrawler, load_pages
from scriptengine.ingest.transclusion import (
    PageTransclusion,
    as_transcluded,
    bare_calls,
    declared_transclusions,
    inline,
    targets,
)

RULES = (PageTransclusion(template="infobox", page="Infobox:{title}"),)
DECLARED = {"transcluded_pages": [{"template": "Infobox", "page": "Infobox:{title}"}]}

ARTICLE = "{{Infobox}}\n'''Blue B''' was a shinobi.<ref name=\"db4\"/>\n\n== Background ==\nText."
DATA_PAGE = (
    "{{Infobox/Naruto/Character\n|kanji=ブルービー\n|affiliations=Kumogakure\n"
    "|ref=<ref name=\"db4\">Fourth Databook, page 208</ref>\n}}"
)


class TestDeclaredTransclusions:
    def test_reads_the_rule(self):
        assert declared_transclusions(DECLARED) == RULES

    @pytest.mark.parametrize("overrides", [None, {}, {"transcluded_pages": []}])
    def test_a_series_declaring_nothing_inlines_nothing(self, overrides):
        """Off unless asked for: every other wiki writes its infobox in place."""
        assert declared_transclusions(overrides) == ()

    def test_the_template_prefix_and_case_do_not_matter(self):
        rules = declared_transclusions(
            {"transcluded_pages": [{"template": "Template:infobox", "page": "Infobox:{title}"}]}
        )
        assert rules == RULES

    def test_a_page_that_does_not_name_the_article_is_refused(self):
        """Without `{title}` one page would be spliced into every article making
        the call. That is a list template, and `template_lists:` handles it."""
        assert declared_transclusions(
            {"transcluded_pages": [{"template": "Infobox", "page": "Infobox:Shared"}]}
        ) == ()

    def test_half_a_rule_is_dropped(self):
        assert declared_transclusions(
            {"transcluded_pages": [{"template": "Infobox"}, {"page": "Infobox:{title}"}, "x"]}
        ) == ()


class TestBareCalls:
    def test_finds_the_bare_call(self):
        assert [rule for _s, _e, rule in bare_calls(ARTICLE, RULES)] == [RULES[0]]

    def test_spacing_and_case_are_the_wikis_not_ours(self):
        assert len(bare_calls("{{ infobox }}", RULES)) == 1

    def test_a_call_with_parameters_is_an_infobox_written_in_place(self):
        """The shape every other wiki uses. Replacing it would throw away the
        parameters the parser is about to read."""
        assert bare_calls("{{Infobox|name=Todo|grade=1}}", RULES) == []

    def test_a_direct_transclusion_of_another_page_is_not_this_rule(self):
        """`{{Infobox:Asuma Sarutobi Stats}}` names its page outright. Reading
        it as the bare call would fetch `Infobox:<article>` in its place."""
        assert bare_calls("{{Infobox:Asuma Sarutobi Stats}}", RULES) == []

    def test_a_sub_template_is_not_the_call(self):
        assert bare_calls("{{Infobox/Naruto/Character}}", RULES) == []

    def test_nothing_declared_finds_nothing(self):
        assert bare_calls(ARTICLE, ()) == []


class TestTargets:
    def test_the_page_is_named_after_the_article(self):
        assert targets("Blue B", ARTICLE, RULES) == ["Infobox:Blue B"]

    def test_a_title_with_braces_survives(self):
        """Why the slot is replaced literally: `str.format` would raise here."""
        assert targets("A {B}", "{{Infobox}}", RULES) == ["Infobox:A {B}"]

    def test_two_calls_ask_once(self):
        assert targets("X", "{{Infobox}} and {{Infobox}}", RULES) == ["Infobox:X"]


class TestAsTranscluded:
    def test_noinclude_stays_behind(self):
        assert as_transcluded("{{Box|a=1}}<noinclude>[[Category:Infoboxes]]</noinclude>") == "{{Box|a=1}}"

    def test_includeonly_is_unwrapped(self):
        assert as_transcluded("<includeonly>{{Box|a=1}}</includeonly>") == "{{Box|a=1}}"

    def test_onlyinclude_wins(self):
        assert as_transcluded("doc <onlyinclude>{{Box|a=1}}</onlyinclude> more doc") == "{{Box|a=1}}"

    def test_an_unclosed_noinclude_runs_to_the_end(self):
        assert as_transcluded("{{Box|a=1}}<noinclude>docs never closed") == "{{Box|a=1}}"


class TestInline:
    def test_the_call_becomes_the_page(self):
        text, missing = inline("Blue B", ARTICLE, RULES, {"Infobox:Blue B": DATA_PAGE})
        assert missing == []
        assert text.startswith("{{Infobox/Naruto/Character")
        assert "{{Infobox}}" not in text
        assert "'''Blue B''' was a shinobi." in text

    def test_a_missing_page_leaves_the_call_as_written(self):
        """Visible in the stored text, and named, rather than silently erased."""
        text, missing = inline("Blue B", ARTICLE, RULES, {})
        assert text == ARTICLE
        assert missing == ["Infobox:Blue B"]

    def test_a_second_pass_changes_nothing(self):
        once, _ = inline("Blue B", ARTICLE, RULES, {"Infobox:Blue B": DATA_PAGE})
        twice, missing = inline("Blue B", once, RULES, {"Infobox:Blue B": DATA_PAGE})
        assert twice == once
        assert missing == []

    def test_the_parser_reads_what_was_spliced(self):
        """The point of doing it before parsing: the article is typed, its
        facts are read and its named references resolve, all from one text."""
        from scriptengine.ingest.wikitext import collect_ref_tag_definitions, find_infobox

        text, _ = inline("Blue B", ARTICLE, RULES, {"Infobox:Blue B": DATA_PAGE})
        name, params = find_infobox(text) or ("", {})
        assert name == "Infobox/Naruto/Character"
        assert params["affiliations"] == "Kumogakure"
        assert collect_ref_tag_definitions(text)["db4"] == "Fourth Databook, page 208"


# ── the crawler ──────────────────────────────────────────────────────────────


class FakeWiki(WikiCrawler):
    """Answers the API from a dictionary instead of the network."""

    def __init__(self, articles: dict[str, str], data: dict[str, str] | None = None,
                 redirects: dict[str, list[str]] | None = None, down: set[str] | None = None):
        super().__init__(Settings(crawl_delay_seconds=0, crawl_stall_seconds=60))
        self.articles = articles
        self.data = data or {}
        self.redirects = redirects or {}
        self.down = down or set()
        self.calls: list[dict] = []

    async def _get(self, base, params):  # type: ignore[override]
        self.calls.append(params)
        if params.get("list") == "allpages":
            names = [] if params["apnamespace"] == "10" else sorted(self.articles)
            return {"query": {"allpages": [{"title": name} for name in names]}}
        if params.get("action") == "parse":
            return {"parse": {"properties": {}}}

        asked = params["titles"].split("|")
        if params["prop"] == "redirects":
            if "redirects" in self.down:
                return None
            return {"query": {"pages": [
                {"title": t, "redirects": [{"ns": 0, "title": n} for n in self.redirects.get(t, [])]}
                for t in asked
            ]}}
        if params["prop"] == "revisions":
            if "data" in self.down:
                return None
            return {"query": {"pages": [
                {"title": t, "revisions": [{"slots": {"main": {"content": self.data[t]}}}]}
                if t in self.data else {"title": t, "missing": True}
                for t in asked
            ]}}
        return {"query": {"pages": [
            {"title": t, "pageid": index + 1,
             "revisions": [{"revid": 7, "slots": {"main": {"content": self.articles[t]}}}],
             "categories": [{"title": "Category:Characters"}], "templates": []}
            for index, t in enumerate(asked) if t in self.articles
        ]}}


def crawl(tmp_path, wiki: FakeWiki, overrides: dict | None) -> tuple[dict, dict]:
    paths = SeriesPaths(name="sample", root=tmp_path / "sample")
    manifest = asyncio.run(
        wiki._crawl("https://sample.fandom.com/wiki/Main", paths, 0, overrides)
    )
    return manifest, {page.title: page for page in load_pages(paths)}


class TestCrawlInlinesTheDataPage:
    def test_the_article_gets_its_facts(self, tmp_path):
        wiki = FakeWiki({"Blue B": ARTICLE}, data={"Infobox:Blue B": DATA_PAGE})
        manifest, pages = crawl(tmp_path, wiki, DECLARED)

        page = pages["Blue B"]
        assert page.fact("affiliations").value == "Kumogakure"
        assert "{{Infobox}}" not in page.wikitext
        assert manifest["transcluded_pages"] == {"inlined_this_run": 1, "missing": []}

    def test_undeclared_the_crawl_is_what_it_always_was(self, tmp_path):
        """No extra request, the article stored as written, and a manifest with
        the keys it has always had."""
        wiki = FakeWiki({"Blue B": ARTICLE}, data={"Infobox:Blue B": DATA_PAGE},
                        redirects={"Blue B": ["Fukai"]})
        manifest, pages = crawl(tmp_path, wiki, {})

        assert pages["Blue B"].wikitext == ARTICLE
        assert pages["Blue B"].redirects == []
        assert "transcluded_pages" not in manifest
        assert "redirects_recorded_this_run" not in manifest
        assert not [c for c in wiki.calls if c.get("prop") in {"revisions", "redirects"}]

    def test_an_article_without_a_data_page_is_named(self, tmp_path):
        wiki = FakeWiki({"Blue B": ARTICLE})
        manifest, pages = crawl(tmp_path, wiki, DECLARED)

        assert pages["Blue B"].wikitext == ARTICLE
        assert manifest["transcluded_pages"]["missing"] == ["Infobox:Blue B"]

    def test_a_request_that_fails_fails_the_batch(self, tmp_path):
        """Throttled is not the same as absent. Writing the article without its
        infobox would look, on disk, exactly like an article that has none."""
        wiki = FakeWiki({"Blue B": ARTICLE}, data={"Infobox:Blue B": DATA_PAGE}, down={"data"})
        manifest, pages = crawl(tmp_path, wiki, DECLARED)

        assert pages == {}
        assert manifest["failed"] == ["Blue B"]

    def test_fetch_wikitext_raises_rather_than_returning_short(self):
        wiki = FakeWiki({}, down={"data"})
        with pytest.raises(FetchFailed):
            asyncio.run(wiki.fetch_wikitext("https://sample.fandom.com/api.php", ["Infobox:X"]))


class TestCrawlRecordsRedirects:
    def test_the_titles_that_land_on_a_page_become_its_names(self, tmp_path):
        wiki = FakeWiki({"Sasuke Uchiha": "'''Sasuke''' is a shinobi.\n\n== Background ==\nText."},
                        redirects={"Sasuke Uchiha": ["Sasuke", "Uchiha Sasuke"]})
        manifest, pages = crawl(tmp_path, wiki, {"redirect_aliases": True})

        page = pages["Sasuke Uchiha"]
        assert page.redirects == ["Sasuke", "Uchiha Sasuke"]
        assert {"Sasuke", "Uchiha Sasuke"} <= set(page.aliases)
        assert manifest["redirects_recorded_this_run"] == 2

    def test_a_long_list_is_followed_to_its_end(self):
        """The wiki caps one response at 500 redirects across the whole batch.
        Stopping there gives the first articles their names and the last none."""

        class Paged(FakeWiki):
            async def _get(self, base, params):  # type: ignore[override]
                self.calls.append(params)
                if "rdcontinue" not in params:
                    return {"continue": {"rdcontinue": "2|0", "continue": "||"},
                            "query": {"pages": [{"title": "A", "redirects": [{"title": "A1"}]}]}}
                return {"query": {"pages": [{"title": "A", "redirects": [{"title": "A2"}]},
                                            {"title": "B", "redirects": [{"title": "B1"}]}]}}

        wiki = Paged({})
        found = asyncio.run(wiki.fetch_redirects("https://sample.fandom.com/api.php", ["A", "B"]))
        assert found == {"A": ["A1", "A2"], "B": ["B1"]}
        assert len(wiki.calls) == 2

    def test_a_request_that_fails_fails_the_batch(self, tmp_path):
        wiki = FakeWiki({"Sasuke Uchiha": "'''Sasuke''' is a shinobi."}, down={"redirects"})
        manifest, pages = crawl(tmp_path, wiki, {"redirect_aliases": True})

        assert pages == {}
        assert manifest["failed"] == ["Sasuke Uchiha"]
