"""Yamc パッケージのメインモジュール。

Markdown テキストを複数のパーサーバックエンドを用いて HTML に変換する
CLI ツールおよび変換機能を提供する。
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, cast

import typer

__all__ = ["Backend", "__version__", "app", "convert_markdown", "main"]

__version__ = "0.1.0"

app = typer.Typer(
    name="yamc",
    help=(
        "Yet Another Markdown Converter: CLI tool to convert Markdown to"
        " HTML using multiple backends."
    ),
    add_completion=False,
)


class Backend(str, Enum):
    """利用可能な Markdown 変換バックエンドを定義する列挙型。"""

    PYTHON_MARKDOWN = "markdown"
    MISTUNE = "mistune"
    MARKDOWN_IT = "markdown-it"
    MARKDOWN2 = "markdown2"


def convert_markdown(text: str, backend: Backend) -> str:
    """指定されたバックエンドを使用して Markdown 文字列を HTML に変換する。

    Args:
        text: 変換対象の Markdown 文字列。
        backend: 使用する Markdown 変換バックエンド。

    Returns:
        変換された HTML 文字列。

    Raises:
        ValueError: サポートされていないバックエンドが指定された場合。
    """
    if backend == Backend.PYTHON_MARKDOWN:
        import markdown

        # 一般的な拡張機能（テーブル、コードハイライトなど）を有効化
        result = markdown.markdown(text, extensions=["extra", "codehilite"])
        return cast(str, result)

    if backend == Backend.MISTUNE:
        import mistune

        # mistune v3+ では create_markdown または mistune.html を使用
        markdown_parser = mistune.create_markdown(
            plugins=["table", "strikethrough"]
        )
        result = markdown_parser(text)
        if isinstance(result, str):
            return result
        return str(result)

    if backend == Backend.MARKDOWN_IT:
        from markdown_it import MarkdownIt

        # gfm-like: GitHub Flavored Markdown 互換のプリセットを使用
        # linkify-it-py がない環境でも動作するよう linkify を False に設定
        md = MarkdownIt("gfm-like", {"linkify": False})
        result = md.render(text)
        return cast(str, result)

    if backend == Backend.MARKDOWN2:
        import markdown2

        # extras でテーブルやフェンスドコードブロックを有効化
        result = markdown2.markdown(
            text, extras=["fenced-code-blocks", "tables", "strike"]
        )
        return cast(str, result)

    raise ValueError(f"Unsupported backend: {backend}")


def version_callback(value: bool) -> None:
    """バージョン情報を表示して終了するコールバック関数。

    Args:
        value: オプションが指定されたかどうか。

    Raises:
        typer.Exit: バージョン表示後にプログラムを正常終了する。
    """
    if value:
        typer.echo(f"yamc {__version__}")
        raise typer.Exit()


@app.command()
def convert(
    input_file: Annotated[
        Path | None,
        typer.Argument(
            help=(
                "Path to the input Markdown file. Reads from stdin if omitted."
            ),
            exists=True,
            readable=True,
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to write the HTML output. Writes to stdout if omitted.",
            writable=True,
        ),
    ] = None,
    backend: Annotated[
        Backend,
        typer.Option(
            "--backend",
            "-b",
            case_sensitive=False,
            help="Markdown parsing backend to use.",
        ),
    ] = Backend.PYTHON_MARKDOWN,
    full_html: Annotated[
        bool,
        typer.Option(
            "--full-html",
            "-f",
            help="Wrap the result in <html>, <head>, and <body> tags.",
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Convert Markdown to HTML with selectable backend.

    If input_file is omitted and data is piped to stdin, yamc reads
    the Markdown content directly from standard input.
    """
    del version  # コールバックで処理されるため未使用

    if input_file is not None:
        source_text = input_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        source_text = sys.stdin.read()
    else:
        typer.echo("Error: No input provided via file or stdin.", err=True)
        raise typer.Exit(code=1)

    html_content = convert_markdown(source_text, backend)

    if full_html:
        title = input_file.stem if input_file else "Document"
        html_content = (
            f'<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
            f'  <meta charset="utf-8">\n'
            f"  <title>{title}</title>\n"
            f"</head>\n<body>\n{html_content}\n</body>\n</html>\n"
        )

    if output is not None:
        output.write_text(html_content, encoding="utf-8")
    else:
        sys.stdout.write(html_content)


def main() -> None:
    """Yamc の CLI エントリーポイント関数。"""
    app()
