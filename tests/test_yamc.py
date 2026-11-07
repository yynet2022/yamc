"""yamc パッケージのユニットテストモジュール。"""

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer.testing
from typer.testing import CliRunner

from yamc import Backend, __version__, app, convert_markdown, main

runner = CliRunner()


class TestConvertMarkdown:
    """convert_markdown 関数のテストクラス。"""

    @pytest.mark.parametrize(
        "backend",
        [
            Backend.PYTHON_MARKDOWN,
            Backend.MISTUNE,
            Backend.MARKDOWN_IT,
            Backend.MARKDOWN2,
        ],
    )
    def test_convert_markdown_backends(self, backend: Backend) -> None:
        """各バックエンドで Markdown が HTML に変換されることを検証する。"""
        markdown_text = "# Hello World\n\nThis is **yamc**."
        result = convert_markdown(markdown_text, backend)

        assert "<h1" in result
        assert "Hello World" in result
        assert "<strong>yamc</strong>" in result

    def test_convert_markdown_unsupported_backend(self) -> None:
        """サポート外のバックエンドで ValueError を送出することを検証する。"""
        with pytest.raises(ValueError, match="Unsupported backend"):
            convert_markdown("# test", "unknown_backend")  # type: ignore[arg-type]

    def test_convert_markdown_mistune_non_str(self) -> None:
        """Mistune が非文字列を返した場合に文字列化を検証。"""
        mock_parser = MagicMock(return_value=["mocked", "list"])
        with patch("mistune.create_markdown", return_value=mock_parser):
            result = convert_markdown("# test", Backend.MISTUNE)
            assert result == "['mocked', 'list']"


class TestCli:
    """yamc CLI コマンドのテストクラス。"""

    def test_help(self) -> None:
        """--help オプションでヘルプメッセージが表示されることを検証する。"""
        result = runner.invoke(app, ["--help"], prog_name="yamc")
        assert result.exit_code == 0
        assert "Usage: yamc [OPTIONS] [input_file]" in result.stdout
        assert "--help" in result.stdout

    @pytest.mark.parametrize("flag", ["--version", "-V"])
    def test_version(self, flag: str) -> None:
        """--version および -V でバージョンが表示されることを検証する。"""
        result = runner.invoke(app, [flag])
        assert result.exit_code == 0
        assert f"yamc {__version__}" in result.stdout

    def test_file_input_to_stdout(self, tmp_path: Path) -> None:
        """ファイルから読み込んで標準出力へ出力することを検証する。"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Title", encoding="utf-8")

        result = runner.invoke(app, [str(md_file)])
        assert result.exit_code == 0
        assert "<h1" in result.stdout
        assert "Test Title" in result.stdout

    def test_file_input_to_file_output(self, tmp_path: Path) -> None:
        """ファイルから読み込んで別のファイルへ書き込むことを検証する。"""
        md_file = tmp_path / "input.md"
        out_file = tmp_path / "output.html"
        md_file.write_text("## Subtitle", encoding="utf-8")

        result = runner.invoke(app, [str(md_file), "-o", str(out_file)])
        assert result.exit_code == 0
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "<h2" in content
        assert "Subtitle" in content

    def test_stdin_input_to_stdout(self) -> None:
        """標準入力から読み込んで標準出力へ出力することを検証する。"""
        result = runner.invoke(app, input="* Item 1\n* Item 2\n")
        assert result.exit_code == 0
        assert "<ul" in result.stdout
        assert "Item 1" in result.stdout

    @pytest.mark.parametrize(
        "backend_name",
        ["markdown", "mistune", "markdown-it", "markdown2"],
    )
    def test_backend_option(self, backend_name: str) -> None:
        """--backend オプションで各種パーサーを指定できることを検証する。"""
        result = runner.invoke(
            app,
            ["-b", backend_name],
            input="# Backend Test",
        )
        assert result.exit_code == 0
        assert "<h1" in result.stdout
        assert "Backend Test" in result.stdout

    def test_full_html_option_with_file(self, tmp_path: Path) -> None:
        """--full-html 指定時のタイトル自動設定を検証する。"""
        md_file = tmp_path / "sample_doc.md"
        md_file.write_text("Hello Full HTML", encoding="utf-8")

        result = runner.invoke(app, [str(md_file), "--full-html"])
        assert result.exit_code == 0
        assert "<!DOCTYPE html>" in result.stdout
        assert '<html lang="ja">' in result.stdout
        assert "<title>sample_doc</title>" in result.stdout
        assert "Hello Full HTML" in result.stdout

    def test_full_html_option_with_stdin(self) -> None:
        """標準入力からの --full-html でのタイトル設定を検証。"""
        result = runner.invoke(app, ["-f"], input="Stdin content")
        assert result.exit_code == 0
        assert "<!DOCTYPE html>" in result.stdout
        assert "<title>Document</title>" in result.stdout
        assert "Stdin content" in result.stdout

    def test_no_input_error(self) -> None:
        """ファイルも標準入力もない場合にエラー終了することを検証する。"""
        with patch.object(
            typer.testing._NamedTextIOWrapper, "isatty", return_value=True
        ):
            result = runner.invoke(app, [])
            assert result.exit_code == 1
            assert (
                "Error: No input provided via file or stdin." in result.output
            )

    def test_non_existent_file(self, tmp_path: Path) -> None:
        """存在しないファイルパスが渡された場合にエラーとなることを検証する。"""
        non_existent = tmp_path / "does_not_exist.md"
        result = runner.invoke(app, [str(non_existent)])
        assert result.exit_code != 0

    def test_invalid_backend(self) -> None:
        """存在しないバックエンドが渡された場合にエラーとなることを検証する。"""
        result = runner.invoke(app, ["-b", "invalid_backend"], input="# text")
        assert result.exit_code != 0


class TestEntrypoints:
    """エントリーポイントのテストクラス。"""

    def test_main_function(self) -> None:
        """Main 関数が app を呼び出すことを検証する。"""
        with patch("yamc.app") as mock_app:
            main()
            mock_app.assert_called_once()

    def test_module_execution(self) -> None:
        """__main__.py が直接実行できることを検証する。"""
        with (
            patch("yamc.main") as mock_main,
            patch.object(runpy, "__name__", "__main__"),
        ):
            runpy.run_module("yamc.__main__", run_name="__main__")
            mock_main.assert_called_once()

    def test_module_import(self) -> None:
        """__main__.py がインポート時に main を呼ばないことを検証。"""
        with patch("yamc.main") as mock_main:
            if "yamc.__main__" in sys.modules:
                importlib.reload(sys.modules["yamc.__main__"])
            else:
                importlib.import_module("yamc.__main__")
            mock_main.assert_not_called()
