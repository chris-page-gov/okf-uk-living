#!/usr/bin/env python3
"""Render curated Explore OKF Markdown as deterministic static HTML."""

from __future__ import annotations

import base64
import hashlib
import html
import os
import posixpath
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import SplitResult, quote, unquote, urlsplit, urlunsplit


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GITHUB_BLOB_BASE = "https://github.com/chris-page-gov/okf-uk-living/blob/main/"
DEFAULT_HOME_PATH = Path("index.html")
DEFAULT_EXPLORE_PATH = Path("explore/index.html")
DEFAULT_LEARN_PATH = Path("learn/index.html")

# The string is inserted byte for byte between the style tags. The CSP hash is
# calculated from this exact value during rendering.
STYLE = """\
:root {
  color-scheme: light;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  line-height: 1.6;
  --ink: #17212b;
  --soft-ink: #465766;
  --paper: #fbfaf6;
  --surface: #ffffff;
  --line: #c8d3cf;
  --teal: #006b62;
  --teal-dark: #004d47;
  --teal-pale: #e2f4f0;
  --amber: #9c4d00;
  --amber-pale: #fff1d8;
}

* { box-sizing: border-box; }
html { background: var(--paper); }
body { min-width: 19rem; margin: 0; color: var(--ink); background: var(--paper); }
a { color: var(--teal-dark); text-decoration-thickness: 0.1em; text-underline-offset: 0.16em; }
a:hover { text-decoration-thickness: 0.16em; }
:focus-visible { outline: 0.2rem solid #ffbf47; outline-offset: 0.18rem; }
.skip-link { position: absolute; top: 0.5rem; left: 0.5rem; padding: 0.6rem 0.9rem; color: #fff; background: var(--ink); transform: translateY(-180%); }
.skip-link:focus { transform: translateY(0); }
.site-header { color: #fff; border-bottom: 0.3rem solid #21b39e; background: #103c39; }
.header-inner, main, .footer-inner { width: min(100% - 2rem, 52rem); margin-inline: auto; }
.header-inner { display: flex; flex-wrap: wrap; gap: 0.8rem 2rem; align-items: baseline; justify-content: space-between; padding-block: 1.1rem; }
.brand { color: #fff; font-size: 1.15rem; font-weight: 750; text-decoration: none; }
.primary-nav { display: flex; flex-wrap: wrap; gap: 0.35rem 1.1rem; }
.primary-nav a { color: #fff; }
main { padding-block: clamp(2rem, 6vw, 4.5rem); }
.review-state { margin: 0 0 1.2rem; padding: 0.7rem 0.9rem; color: #513000; border-left: 0.3rem solid var(--amber); background: var(--amber-pale); }
.markdown-body { overflow-wrap: anywhere; }
h1, h2, h3, h4, h5, h6 { margin: 2rem 0 0.65rem; line-height: 1.18; scroll-margin-top: 1rem; }
h1 { margin-top: 0; font-size: clamp(2rem, 7vw, 3.5rem); letter-spacing: -0.035em; }
h2 { padding-bottom: 0.25rem; border-bottom: 1px solid var(--line); font-size: clamp(1.5rem, 4vw, 2.15rem); }
h3 { font-size: 1.35rem; }
p, ul, ol, blockquote, pre, table { margin: 0 0 1.2rem; }
ul, ol { padding-left: 1.6rem; }
li + li { margin-top: 0.3rem; }
blockquote { padding: 0.15rem 0 0.15rem 1rem; color: var(--soft-ink); border-left: 0.3rem solid var(--teal); }
blockquote > :last-child { margin-bottom: 0; }
code { padding: 0.1em 0.3em; border-radius: 0.2rem; background: var(--teal-pale); font-family: ui-monospace, "SFMono-Regular", Consolas, monospace; font-size: 0.92em; }
pre { overflow-x: auto; padding: 1rem; color: #f4f7f6; border-radius: 0.35rem; background: #172b2a; }
pre code { padding: 0; color: inherit; background: transparent; font-size: 0.88rem; }
.table-wrap { max-width: 100%; overflow-x: auto; margin-bottom: 1.2rem; }
table { width: 100%; border-collapse: collapse; background: var(--surface); }
th, td { padding: 0.55rem 0.65rem; text-align: left; vertical-align: top; border: 1px solid var(--line); }
th { background: var(--teal-pale); }
.align-centre { text-align: center; }
.align-right { text-align: right; }
.image-omitted { color: var(--soft-ink); }
.site-footer { border-top: 1px solid var(--line); color: var(--soft-ink); background: var(--surface); }
.footer-inner { padding-block: 1.3rem; }
.footer-inner p { margin: 0; }
"""

_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([A-Za-z0-9_+.-]*)[ \t]*$")
_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_QUOTE = re.compile(r"^ {0,3}>[ \t]?(.*)$")
_UNORDERED = re.compile(r"^ {0,3}[-+*][ \t]+(.+)$")
_ORDERED = re.compile(r"^ {0,3}(\d+)[.)][ \t]+(.+)$")
_TABLE_DIVIDER = re.compile(r"^:?-{3,}:?$")
_BAD_PERCENT = re.compile(r"%(?![0-9A-Fa-f]{2})")
_UNSAFE_URL_CHARACTERS = frozenset("\"'<>\\^`{|}")
_ESCAPABLE = frozenset(r"\\`*{}_[]()#+-.!|>")


@dataclass(frozen=True)
class _InlineResult:
    markup: str
    plain: str


@dataclass(frozen=True)
class _ResolvedLink:
    href: str | None
    external: bool = False


def _has_unsafe_url_characters(value: str, *, allow_space: bool = False) -> bool:
    for character in value:
        if ord(character) < 0x20 or ord(character) == 0x7F:
            return True
        if character in _UNSAFE_URL_CHARACTERS:
            return True
        if character.isspace() and not allow_space:
            return True
    return bool(_BAD_PERCENT.search(value))


def _decode_url_component(value: str, *, allow_space: bool = False) -> str | None:
    if _has_unsafe_url_characters(value, allow_space=allow_space):
        return None
    try:
        decoded = unquote(value, encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        return None
    if _has_unsafe_url_characters(decoded, allow_space=allow_space):
        return None
    return decoded


def _normalise_public_path(value: Path, *, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts:
        raise ValueError(f"{label} must be a non-empty repository-relative path")
    if any(part in {"", ".", ".."} or "\\" in part for part in path.parts):
        raise ValueError(f"{label} contains an unsafe path component")
    return Path(*path.parts)


def _validated_authored_source_path(value: Path) -> Path:
    """Return a contained, regular Markdown source without following symlinks."""

    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPOSITORY_ROOT / candidate
    lexical_path = Path(os.path.abspath(candidate))
    try:
        relative_path = lexical_path.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError("authored Markdown source must be inside the repository") from error

    current = REPOSITORY_ROOT
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("authored Markdown source must not contain symbolic links")

    try:
        resolved_path = lexical_path.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise ValueError("authored Markdown source must be a regular file") from error
    try:
        resolved_path.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError("authored Markdown source must be inside the repository") from error
    if not resolved_path.is_file():
        raise ValueError("authored Markdown source must be a regular file")
    return resolved_path


def _public_relative_href(public_path: Path, target_path: Path) -> str:
    start = public_path.parent.as_posix()
    if start in {"", "."}:
        start = "."
    relative = posixpath.relpath(target_path.as_posix(), start=start)
    return quote(relative, safe="/-._~")


def _normalise_navigation_href(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("navigation links must be non-empty strings")
    if _has_unsafe_url_characters(value, allow_space=False):
        raise ValueError("navigation link is unsafe")
    try:
        parsed = urlsplit(value)
    except ValueError as error:
        raise ValueError("navigation link is unsafe") from error
    if parsed.scheme or parsed.netloc or parsed.query:
        raise ValueError("navigation links must be local paths without a query")
    decoded_path = _decode_url_component(parsed.path, allow_space=True)
    decoded_fragment = _decode_url_component(parsed.fragment, allow_space=True)
    if decoded_path is None or decoded_fragment is None or "\\" in decoded_path:
        raise ValueError("navigation link is unsafe")
    href = quote(decoded_path, safe="/-._~")
    if parsed.fragment:
        href += "#" + quote(decoded_fragment, safe="-._~")
    if not href:
        raise ValueError("navigation links must not resolve to an empty URL")
    return href


class _MarkdownRenderer:
    def __init__(
        self,
        source_path: Path,
        public_path: Path,
        public_mapping: dict[Path, Path],
    ) -> None:
        self.source_path = source_path.resolve()
        self.public_path = _normalise_public_path(public_path, label="public_path")
        self.public_mapping: dict[Path, Path] = {}
        for source, target in public_mapping.items():
            source_key = Path(source)
            if not source_key.is_absolute():
                source_key = REPOSITORY_ROOT / source_key
            resolved_source = source_key.resolve()
            public_target = _normalise_public_path(
                Path(target), label=f"public mapping target for {source}"
            )
            previous = self.public_mapping.get(resolved_source)
            if previous is not None and previous != public_target:
                raise ValueError(f"public mapping contains conflicting targets for {source}")
            self.public_mapping[resolved_source] = public_target
        self.heading_counts: dict[str, int] = {}
        self.document_title = self.source_path.stem.replace("-", " ").strip().title()

    def render(self, markdown: str) -> str:
        lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if lines and lines[0].startswith("\ufeff"):
            lines[0] = lines[0].lstrip("\ufeff")
        lines = self._without_front_matter(lines)
        self.heading_counts.clear()
        self._set_document_title(lines)
        return self._render_blocks(lines)

    @staticmethod
    def _without_front_matter(lines: list[str]) -> list[str]:
        if not lines or lines[0].strip() != "---":
            return lines
        for index in range(1, len(lines)):
            if lines[index].strip() in {"---", "..."}:
                return lines[index + 1 :]
        # A document that starts like front matter but never closes is safer to
        # omit than to publish as review prose.
        return []

    def _set_document_title(self, lines: list[str]) -> None:
        for line in lines:
            match = _HEADING.match(line)
            if match:
                plain = self._render_inline(match.group(2)).plain.strip()
                if plain:
                    self.document_title = plain
                return

    def _render_blocks(self, lines: list[str]) -> str:
        output: list[str] = []
        index = 0
        while index < len(lines):
            if not lines[index].strip():
                index += 1
                continue

            fence = _FENCE.match(lines[index])
            if fence:
                block, index = self._render_fence(lines, index, fence)
                output.append(block)
                continue

            heading = _HEADING.match(lines[index])
            if heading:
                level = len(heading.group(1))
                content = self._render_inline(heading.group(2))
                heading_id = self._unique_heading_id(content.plain)
                output.append(
                    f'<h{level} id="{heading_id}">{content.markup}</h{level}>'
                )
                index += 1
                continue

            if self._is_table_start(lines, index):
                block, index = self._render_table(lines, index)
                output.append(block)
                continue

            quote_match = _QUOTE.match(lines[index])
            if quote_match:
                quoted: list[str] = []
                while index < len(lines):
                    current = _QUOTE.match(lines[index])
                    if current is None:
                        break
                    quoted.append(current.group(1))
                    index += 1
                output.append("<blockquote>\n" + self._render_blocks(quoted) + "\n</blockquote>")
                continue

            list_match = self._list_match(lines[index])
            if list_match is not None:
                block, index = self._render_list(lines, index, list_match[0])
                output.append(block)
                continue

            paragraph_lines = [lines[index].strip()]
            index += 1
            while index < len(lines) and lines[index].strip():
                if self._is_block_start(lines, index):
                    break
                paragraph_lines.append(lines[index].strip())
                index += 1
            paragraph = self._render_inline(" ".join(paragraph_lines))
            output.append(f"<p>{paragraph.markup}</p>")

        return "\n".join(output)

    def _render_fence(
        self, lines: list[str], index: int, opening: re.Match[str]
    ) -> tuple[str, int]:
        delimiter = opening.group(1)
        language = opening.group(2)
        index += 1
        code_lines: list[str] = []
        closing = re.compile(
            rf"^ {{0,3}}{re.escape(delimiter[0])}{{{len(delimiter)},}}[ \t]*$"
        )
        while index < len(lines) and not closing.match(lines[index]):
            code_lines.append(lines[index])
            index += 1
        if index < len(lines):
            index += 1
        code = "\n".join(code_lines)
        if code_lines:
            code += "\n"
        class_name = f' class="language-{html.escape(language, quote=True)}"' if language else ""
        return f"<pre><code{class_name}>{html.escape(code, quote=False)}</code></pre>", index

    def _unique_heading_id(self, label: str) -> str:
        ascii_label = (
            unicodedata.normalize("NFKD", label)
            .encode("ascii", "ignore")
            .decode("ascii")
            .casefold()
        )
        base = re.sub(r"[^a-z0-9]+", "-", ascii_label).strip("-") or "section"
        count = self.heading_counts.get(base, 0) + 1
        self.heading_counts[base] = count
        return base if count == 1 else f"{base}-{count}"

    @staticmethod
    def _list_match(line: str) -> tuple[str, re.Match[str]] | None:
        unordered = _UNORDERED.match(line)
        if unordered:
            return "ul", unordered
        ordered = _ORDERED.match(line)
        if ordered:
            return "ol", ordered
        return None

    def _render_list(
        self, lines: list[str], index: int, list_type: str
    ) -> tuple[str, int]:
        items: list[str] = []
        start = 1
        while index < len(lines):
            match = self._list_match(lines[index])
            if match is None or match[0] != list_type:
                if items and re.match(r"^ {2,}\S", lines[index]):
                    items[-1] += " " + lines[index].strip()
                    index += 1
                    continue
                break
            marker = match[1]
            if list_type == "ol" and not items:
                start = int(marker.group(1))
                content = marker.group(2)
            else:
                content = marker.group(1) if list_type == "ul" else marker.group(2)
            items.append(content)
            index += 1

        start_attribute = f' start="{start}"' if list_type == "ol" and start != 1 else ""
        body = "\n".join(
            f"  <li>{self._render_inline(item).markup}</li>" for item in items
        )
        return f"<{list_type}{start_attribute}>\n{body}\n</{list_type}>", index

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        value = line.strip()
        cells: list[str] = []
        current: list[str] = []
        code_delimiter = ""
        index = 0
        while index < len(value):
            character = value[index]
            if character == "\\" and index + 1 < len(value):
                current.extend((character, value[index + 1]))
                index += 2
                continue
            if character == "`":
                run_end = index
                while run_end < len(value) and value[run_end] == "`":
                    run_end += 1
                run = value[index:run_end]
                if not code_delimiter:
                    code_delimiter = run
                elif code_delimiter == run:
                    code_delimiter = ""
                current.append(run)
                index = run_end
                continue
            if character == "|" and not code_delimiter:
                cells.append("".join(current).strip())
                current = []
            else:
                current.append(character)
            index += 1
        cells.append("".join(current).strip())
        if value.startswith("|") and cells:
            cells.pop(0)
        if value.endswith("|") and cells:
            cells.pop()
        return cells

    def _is_table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines) or "|" not in lines[index]:
            return False
        header = self._split_table_row(lines[index])
        divider = self._split_table_row(lines[index + 1])
        return bool(
            header
            and len(header) == len(divider)
            and all(_TABLE_DIVIDER.fullmatch(cell.strip()) for cell in divider)
        )

    def _render_table(self, lines: list[str], index: int) -> tuple[str, int]:
        headers = self._split_table_row(lines[index])
        dividers = self._split_table_row(lines[index + 1])
        alignments = []
        for divider in dividers:
            if divider.startswith(":") and divider.endswith(":"):
                alignments.append("centre")
            elif divider.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")
        index += 2
        rows: list[list[str]] = []
        while index < len(lines) and lines[index].strip() and "|" in lines[index]:
            cells = self._split_table_row(lines[index])
            cells = (cells + [""] * len(headers))[: len(headers)]
            rows.append(cells)
            index += 1

        head_cells = []
        for position, cell in enumerate(headers):
            class_name = (
                f' class="align-{alignments[position]}"'
                if alignments[position] != "left"
                else ""
            )
            head_cells.append(
                f"      <th scope=\"col\"{class_name}>{self._render_inline(cell).markup}</th>"
            )
        body_rows = []
        for row in rows:
            rendered_cells = []
            for position, cell in enumerate(row):
                class_name = (
                    f' class="align-{alignments[position]}"'
                    if alignments[position] != "left"
                    else ""
                )
                rendered_cells.append(
                    f"      <td{class_name}>{self._render_inline(cell).markup}</td>"
                )
            body_rows.append("    <tr>\n" + "\n".join(rendered_cells) + "\n    </tr>")
        body = "\n".join(body_rows)
        tbody = f"\n  <tbody>\n{body}\n  </tbody>" if body_rows else ""
        table = (
            '<div class="table-wrap">\n'
            "<table>\n"
            "  <thead>\n"
            "    <tr>\n"
            + "\n".join(head_cells)
            + "\n    </tr>\n"
            "  </thead>"
            + tbody
            + "\n</table>\n</div>"
        )
        return table, index

    def _is_block_start(self, lines: list[str], index: int) -> bool:
        list_match = self._list_match(lines[index])
        list_interrupts_paragraph = bool(
            list_match is not None
            and (
                list_match[0] == "ul"
                or int(list_match[1].group(1)) == 1
            )
        )
        return bool(
            _FENCE.match(lines[index])
            or _HEADING.match(lines[index])
            or _QUOTE.match(lines[index])
            or list_interrupts_paragraph
            or self._is_table_start(lines, index)
        )

    @staticmethod
    def _is_escaped(value: str, index: int) -> bool:
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and value[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        return backslashes % 2 == 1

    def _parse_link(self, value: str, start: int, *, image: bool) -> tuple[str, str, int] | None:
        label_start = start + (2 if image else 1)
        depth = 1
        cursor = label_start
        while cursor < len(value):
            if value[cursor] == "\\":
                cursor += 2
                continue
            if value[cursor] == "[":
                depth += 1
            elif value[cursor] == "]":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        if depth or cursor + 1 >= len(value) or value[cursor + 1] != "(":
            return None

        destination_start = cursor + 2
        destination_cursor = destination_start
        parentheses = 1
        while destination_cursor < len(value):
            character = value[destination_cursor]
            if character == "\\":
                destination_cursor += 2
                continue
            if character == "(":
                parentheses += 1
            elif character == ")":
                parentheses -= 1
                if parentheses == 0:
                    destination = value[destination_start:destination_cursor].strip()
                    if destination.startswith("<") and destination.endswith(">"):
                        destination = destination[1:-1]
                    return value[label_start:cursor], destination, destination_cursor + 1
            destination_cursor += 1
        return None

    def _find_emphasis_close(self, value: str, delimiter: str, start: int) -> int:
        cursor = start
        while cursor < len(value):
            found = value.find(delimiter, cursor)
            if found < 0:
                return -1
            if self._is_escaped(value, found):
                cursor = found + len(delimiter)
                continue
            before = value[found - 1] if found else ""
            after_index = found + len(delimiter)
            after = value[after_index] if after_index < len(value) else ""
            if before and not before.isspace():
                if delimiter.startswith("_") and after.isalnum():
                    cursor = found + len(delimiter)
                    continue
                return found
            cursor = found + len(delimiter)
        return -1

    def _render_inline(self, value: str, *, allow_links: bool = True) -> _InlineResult:
        markup: list[str] = []
        plain: list[str] = []
        index = 0
        while index < len(value):
            character = value[index]

            if character == "\\" and index + 1 < len(value) and value[index + 1] in _ESCAPABLE:
                literal = value[index + 1]
                markup.append(html.escape(literal, quote=False))
                plain.append(literal)
                index += 2
                continue

            if character == "`":
                end_of_run = index
                while end_of_run < len(value) and value[end_of_run] == "`":
                    end_of_run += 1
                delimiter = value[index:end_of_run]
                closing = value.find(delimiter, end_of_run)
                if closing >= 0:
                    code = value[end_of_run:closing].replace("\n", " ")
                    if len(code) >= 2 and code.startswith(" ") and code.endswith(" ") and code.strip():
                        code = code[1:-1]
                    markup.append(f"<code>{html.escape(code, quote=False)}</code>")
                    plain.append(code)
                    index = closing + len(delimiter)
                    continue

            if value.startswith("![", index):
                parsed_image = self._parse_link(value, index, image=True)
                if parsed_image is not None:
                    label, _destination, end = parsed_image
                    alt = self._render_inline(label, allow_links=False).plain
                    visible = f"Image omitted: {alt}" if alt else "Image omitted"
                    markup.append(
                        '<span class="image-omitted">'
                        + html.escape(visible, quote=False)
                        + "</span>"
                    )
                    plain.append(visible)
                    index = end
                    continue

            if character == "[":
                parsed_link = self._parse_link(value, index, image=False)
                if parsed_link is not None:
                    label, destination, end = parsed_link
                    rendered_label = self._render_inline(label, allow_links=False)
                    resolved = self._resolve_link(destination) if allow_links else _ResolvedLink(None)
                    if resolved.href is None:
                        markup.append(rendered_label.markup)
                    else:
                        attributes = ""
                        if resolved.external:
                            attributes = ' rel="noopener noreferrer external" referrerpolicy="no-referrer"'
                        markup.append(
                            f'<a href="{html.escape(resolved.href, quote=True)}"{attributes}>'
                            f"{rendered_label.markup}</a>"
                        )
                    plain.append(rendered_label.plain)
                    index = end
                    continue

            strong_delimiter = ""
            if value.startswith("**", index):
                strong_delimiter = "**"
            elif value.startswith("__", index):
                previous = value[index - 1] if index else ""
                if not previous.isalnum():
                    strong_delimiter = "__"
            if strong_delimiter and index + 2 < len(value) and not value[index + 2].isspace():
                closing = self._find_emphasis_close(value, strong_delimiter, index + 2)
                if closing >= 0:
                    inner = self._render_inline(
                        value[index + 2 : closing], allow_links=allow_links
                    )
                    markup.append(f"<strong>{inner.markup}</strong>")
                    plain.append(inner.plain)
                    index = closing + 2
                    continue

            if character in {"*", "_"}:
                previous = value[index - 1] if index else ""
                following = value[index + 1] if index + 1 < len(value) else ""
                may_open = bool(following and not following.isspace())
                if character == "_" and previous.isalnum():
                    may_open = False
                if may_open:
                    closing = self._find_emphasis_close(value, character, index + 1)
                    if closing >= 0:
                        inner = self._render_inline(
                            value[index + 1 : closing], allow_links=allow_links
                        )
                        markup.append(f"<em>{inner.markup}</em>")
                        plain.append(inner.plain)
                        index = closing + 1
                        continue

            markup.append(html.escape(character, quote=False))
            plain.append(character)
            index += 1

        return _InlineResult("".join(markup), "".join(plain))

    def _resolve_link(self, destination: str) -> _ResolvedLink:
        if not destination or _BAD_PERCENT.search(destination):
            return _ResolvedLink(None)
        if _has_unsafe_url_characters(destination, allow_space=True):
            return _ResolvedLink(None)
        try:
            parsed = urlsplit(destination)
        except ValueError:
            return _ResolvedLink(None)

        if parsed.scheme or parsed.netloc:
            return self._resolve_external_link(parsed)

        if parsed.query:
            return _ResolvedLink(None)
        decoded_fragment = _decode_url_component(parsed.fragment, allow_space=True)
        if decoded_fragment is None:
            return _ResolvedLink(None)
        fragment = (
            "#" + quote(decoded_fragment, safe="-._~") if parsed.fragment else ""
        )
        if not parsed.path:
            return _ResolvedLink(fragment or None)

        decoded_path = _decode_url_component(parsed.path, allow_space=True)
        if decoded_path is None or "\\" in decoded_path:
            return _ResolvedLink(None)
        if decoded_path.startswith("/"):
            target = REPOSITORY_ROOT / decoded_path.lstrip("/")
        else:
            target = self.source_path.parent / decoded_path
        resolved_target = target.resolve()

        mapped_target = self.public_mapping.get(resolved_target)
        if mapped_target is not None:
            href = _public_relative_href(self.public_path, mapped_target)
            return _ResolvedLink(href + fragment)

        try:
            repository_path = resolved_target.relative_to(REPOSITORY_ROOT)
        except ValueError:
            return _ResolvedLink(None)
        if not resolved_target.is_file():
            return _ResolvedLink(None)
        encoded_path = quote(repository_path.as_posix(), safe="/-._~")
        return _ResolvedLink(GITHUB_BLOB_BASE + encoded_path + fragment, external=True)

    @staticmethod
    def _resolve_external_link(parsed: SplitResult) -> _ResolvedLink:
        if parsed.scheme.casefold() != "https" or not parsed.netloc:
            return _ResolvedLink(None)
        if parsed.username or parsed.password or not parsed.hostname:
            return _ResolvedLink(None)
        try:
            port = parsed.port
            parsed.hostname.encode("idna")
        except (UnicodeError, ValueError):
            return _ResolvedLink(None)
        if port is not None and not 1 <= port <= 65535:
            return _ResolvedLink(None)
        for component in (parsed.netloc, parsed.path, parsed.query, parsed.fragment):
            if _decode_url_component(component, allow_space=False) is None:
                return _ResolvedLink(None)
        return _ResolvedLink(urlunsplit(parsed), external=True)


def _style_hash() -> str:
    digest = hashlib.sha256(STYLE.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def render_markdown_content(
    source_path: Path,
    markdown: str,
    public_path: Path,
    public_mapping: dict[Path, Path],
    *,
    home_href: str | None = None,
    explore_href: str | None = None,
    learn_href: str | None = None,
    document_status: str | None = None,
) -> str:
    """Render supplied Markdown as a self-contained HTML page.

    ``public_path`` and all mapping values are paths relative to the published
    site root. Mapping keys may be absolute paths or repository-relative paths.
    The optional navigation values must be local URLs; when omitted, links to
    the site-root home, journey explorer and learning library are calculated
    from the page's public location.
    """

    path = _validated_authored_source_path(Path(source_path))
    renderer = _MarkdownRenderer(path, Path(public_path), public_mapping)
    article = renderer.render(markdown)

    default_home = _public_relative_href(renderer.public_path, DEFAULT_HOME_PATH)
    default_explore = _public_relative_href(
        renderer.public_path, DEFAULT_EXPLORE_PATH
    )
    default_learn = _public_relative_href(renderer.public_path, DEFAULT_LEARN_PATH)
    default_notice = _public_relative_href(
        renderer.public_path, Path("generated/browser/NOTICE.html")
    )
    safe_home = _normalise_navigation_href(
        default_home if home_href is None else home_href
    )
    safe_explore = _normalise_navigation_href(
        default_explore if explore_href is None else explore_href
    )
    safe_learn = _normalise_navigation_href(
        default_learn if learn_href is None else learn_href
    )
    safe_notice = _normalise_navigation_href(default_notice)
    title = html.escape(renderer.document_title, quote=False)
    status_text = ""
    if document_status is not None:
        if not isinstance(document_status, str) or not document_status.strip():
            raise ValueError("document_status must be a non-empty string")
        status_text = (
            " Document status: <strong>"
            + html.escape(document_status.strip(), quote=False)
            + "</strong>."
        )
    csp = "; ".join(
        (
            "default-src 'none'",
            "script-src 'none'",
            "script-src-attr 'none'",
            f"style-src 'sha256-{_style_hash()}'",
            "style-src-attr 'none'",
            "img-src 'none'",
            "font-src 'none'",
            "connect-src 'none'",
            "media-src 'none'",
            "object-src 'none'",
            "frame-src 'none'",
            "worker-src 'none'",
            "manifest-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        )
    )

    return f"""<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="{csp}">
  <title>{title} — Explore OKF review library</title>
  <style>{STYLE}</style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{html.escape(safe_home, quote=True)}">A Life in the UK</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="{html.escape(safe_explore, quote=True)}">Explore journeys</a>
        <a href="{html.escape(safe_learn, quote=True)}">Learning library</a>
      </nav>
    </div>
  </header>
  <main id="main-content">
    <p class="review-state"><strong>Review material.</strong>{status_text} This is exploratory research, not an authoritative service or released data product.</p>
    <article class="markdown-body">
{article}
    </article>
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p>Check the cited official source before making a decision.
      Repository-authored documentation is available under the MIT licence.
      See the <a href="{html.escape(safe_notice, quote=True)}">licence and attribution notices</a>.</p>
    </div>
  </footer>
</body>
</html>
"""


def render_markdown_document(
    source_path: Path,
    public_path: Path,
    public_mapping: dict[Path, Path],
    *,
    home_href: str | None = None,
    explore_href: str | None = None,
    learn_href: str | None = None,
    document_status: str | None = None,
) -> str:
    """Render one curated Markdown document as a self-contained HTML page."""

    path = _validated_authored_source_path(Path(source_path))
    return render_markdown_content(
        path,
        path.read_text(encoding="utf-8"),
        public_path,
        public_mapping,
        home_href=home_href,
        explore_href=explore_href,
        learn_href=learn_href,
        document_status=document_status,
    )


__all__ = ["render_markdown_content", "render_markdown_document"]
