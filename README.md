# yamc (Yet Another Markdown Converter)

`yamc` は、複数のパーサーバックエンドを切り替えて Markdown を HTML に変換できる、モダンで軽量な CLI ツールおよび Python ライブラリです。

---

## 特徴

- **マルチバックエンド対応**:
  - `markdown` (Python-Markdown: 拡張機能 `extra`, `codehilite` を標準サポート)
  - `mistune` (Mistune v3: 高速パーサー、`table`, `strikethrough` プラグイン標準対応)
  - `markdown-it` (markdown-it-py: CommonMark / GFM 互換パーサー)
  - `markdown2` (python-markdown2: `fenced-code-blocks`, `tables`, `strike` を標準サポート)
- **柔軟な入出力インターフェース**:
  - ファイルの直接指定はもちろん、標準入力（stdin）や標準出力（stdout）を用いたパイプライン処理に対応。
- **完全な HTML ドキュメント生成 (`--full-html`)**:
  - 断片的な HTML だけでなく、DOCTYPE、`<head>`、`<meta charset="utf-8">`、`<title>` を含む完全な HTML 骨格をワンタッチで生成可能。
- **モダンで型安全な設計**:
  - Python 3.10+ 対応、型ヒントを完備（mypy strict 準拠）。
  - PEP 8 および Ruff の厳しい品質基準をクリアした高品質なコードベース。

---

## ディレクトリ構成

```text
yamc/
├── LICENSE                   # MIT ライセンスファイル
├── README.md                 # 本ドキュメント
├── pyproject.toml            # プロジェクト設定および依存関係定義
├── src/
│   └── yamc/
│       ├── __init__.py       # yamc パッケージ本体・CLI および変換ロジック
│       └── __main__.py       # python -m yamc 実行時のエントリーポイント
└── tests/
    ├── __init__.py           # テストパッケージ定義
    └── test_yamc.py          # CLI および変換関数のユニットテストスイート
```

---

## 動作要件

- **Python**: 3.10 以上
- **OS**: Windows / macOS / Linux

---

## インストール

### 通常インストール

リポジトリをクローンまたはダウンロードし、以下のコマンドでインストールします。

```bash
pip install .
```

### 開発用インストール

ユニットテストや Linter / Formatter を実行するための開発用依存パッケージを含めてインストールする場合は、以下を実行します。

```bash
pip install -e ".[dev]"
```

---

## 使い方

### 1. コマンドラインでの利用 (CLI)

#### 基本的なファイル変換
Markdown ファイルを指定すると、変換結果の HTML が標準出力に出力されます。

```bash
yamc input.md
```

#### 出力先ファイルの指定 (`-o`, `--output`)
`-o` または `--output` オプションで変換後の HTML をファイルに保存できます。

```bash
yamc input.md -o output.html
```

#### 標準入出力を用いたパイプライン処理
入力ファイルを指定せず、標準入力からパイプでテキストを渡すことができます。

```bash
cat input.md | yamc > output.html
```

Windows PowerShell の場合:
```powershell
Get-Content input.md | yamc | Set-Content output.html
```

#### パーサーバックエンドの選択 (`-b`, `--backend`)
`-b` または `--backend` オプションで、使用する Markdown 変換エンジンを選択できます（大文字・小文字は区別されません）。

```bash
# Python-Markdown を使用 (デフォルト)
yamc input.md -b markdown

# Mistune を使用
yamc input.md -b mistune

# markdown-it-py を使用
yamc input.md -b markdown-it

# markdown2 を使用
yamc input.md -b markdown2
```

#### 完全な HTML ドキュメントの生成 (`-f`, `--full-html`)
`-f` または `--full-html` を指定すると、HTML の骨格（`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`）でラップされた完全な HTML を出力します。タイトルタグには入力ファイルのファイル名（標準入力の場合は `Document`）が自動設定されます。

```bash
yamc README.md -f -o README.html
```

#### バージョンおよびヘルプの表示
```bash
# バージョン表示
yamc --version
# または
yamc -V

# ヘルプ表示
yamc --help
```

---

### コマンドラインオプション一覧

| オプション / 引数 | 短縮形 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- |
| `input_file` | - | なし | 変換元の Markdown ファイルパス。省略時は標準入力から読み取ります。 |
| `--output` | `-o` | なし (stdout) | 出力先 HTML ファイルパス。省略時は標準出力に出力します。 |
| `--backend` | `-b` | `markdown` | 使用する変換エンジン (`markdown`, `mistune`, `markdown-it`, `markdown2`)。 |
| `--full-html` | `-f` | `False` | 結果を `<html>`, `<head>`, `<body>` タグで囲んだ完全な HTML 文書として出力します。 |
| `--version` | `-V` | - | バージョン情報を表示して終了します。 |
| `--help` | - | - | ヘルプメッセージを表示して終了します。 |

---

### 2. Python スクリプトからのライブラリ利用

`yamc` の変換機能は、Python スクリプト内から直接インポートして利用することも可能です。

```python
from yamc import Backend, convert_markdown

# Markdown 文字列の定義
markdown_text = """
# タイトル
これは **yamc** による変換テストです。
"""

# バックエンドを指定して HTML に変換
html = convert_markdown(markdown_text, backend=Backend.PYTHON_MARKDOWN)
print(html)
```

---

## 開発・テスト

コード品質チェックおよびユニットテストは以下のコマンドで実行できます。

```bash
# Linter による静的解析チェック
ruff check src tests

# フォーマッタによるスタイリングチェック
ruff format --check src tests

# コードの自動フォーマット適用
ruff format src tests

# 型チェック (mypy strict モード)
mypy src tests

# ユニットテストおよびカバレッジレポートの実行
pytest
```

---

## ライセンス

本プロジェクトは [MIT License](LICENSE) のもとで公開されています。
