from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.dont_write_bytecode = True

from site_content import Author, AuthorRef, SITE, SiteData


ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_PATH = ROOT / "index.html"


def validate_site(site: SiteData) -> None:
    errors: list[str] = []

    if not site.page_title.strip():
        errors.append("page_title must not be empty")
    if not site.profile.name.strip():
        errors.append("profile.name must not be empty")
    if not site.profile.portrait_path.strip():
        errors.append("profile.portrait_path must not be empty")

    for index, publication in enumerate(site.publications, start=1):
        if not publication.title.strip():
            errors.append(f"publications[{index}].title must not be empty")
        if not publication.image_path.strip():
            errors.append(f"publications[{index}].image_path must not be empty")
        for author in publication.authors:
            if isinstance(author, AuthorRef) and not author.id.strip():
                errors.append(f"publications[{index}].authors contains an empty author id")
            if isinstance(author, str) and not author.strip():
                errors.append(f"publications[{index}].authors contains an empty author id")

    if errors:
        raise ValueError("\n".join(errors))


def resolve_author(site: SiteData, author_ref: str | AuthorRef) -> Author:
    if isinstance(author_ref, str):
        author_id = author_ref
        highlight = False
        suffixes: list[str] = []
    else:
        author_id = author_ref.id
        highlight = author_ref.highlight
        suffixes = author_ref.suffixes

    author_info = site.author_directory.get(author_id)
    if author_info is None:
        return Author(name=author_id, url=None, highlight=highlight, suffixes=suffixes)

    return Author(
        name=author_info.display_name,
        url=author_info.url,
        highlight=highlight,
        suffixes=suffixes,
    )


def resolve_site(site: SiteData) -> SiteData:
    resolved_publications = [
        replace(
            publication,
            authors=[resolve_author(site, author) for author in publication.authors],
        )
        for publication in site.publications
    ]
    return replace(site, publications=resolved_publications)


def render_site(site: SiteData) -> str:
    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template("index.html.j2")
    return template.render(site=site)


def main() -> None:
    validate_site(SITE)
    OUTPUT_PATH.write_text(render_site(resolve_site(SITE)), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
