#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import time
import urllib.request

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
TRANSLATABLE_EXTENSIONS = {".md", ".txt"}
EXCLUDED_DIRS = {".git", "target", "node_modules", "book"}

SYSTEM_PROMPT = (
    "You are a careful translator. Translate English text into the target language while preserving markdown formatting, code blocks, embedded links, YAML front matter, tables, and inline code exactly. "
    "Do not alter code fences, markdown link targets, or non-text structural elements."
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Translate repository markdown/text files with Deepseek API."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root or folder to scan for files to translate.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Deepseek base URL (default: https://api.deepseek.com).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Deepseek model to use (default: deepseek-v4-flash).",
    )
    parser.add_argument(
        "--lang",
        default="Simplified Chinese",
        help="Target language for translation (default: Simplified Chinese).",
    )
    parser.add_argument(
        "--suffix",
        default=".zh",
        help="Output filename suffix before the extension (default: .zh).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be translated without calling the API.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original files instead of creating new files with the suffix.",
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=7000,
        help="Maximum characters per translation chunk (default: 7000).",
    )
    args = parser.parse_args(argv)
    args.root = pathlib.Path(args.root).resolve()

    if not args.dry_run and "DEEPSEEK_API_KEY" not in os.environ:
        parser.error("DEEPSEEK_API_KEY is required unless --dry-run is set.")
    if args.max_chunk_chars <= 0:
        parser.error("--max-chunk-chars must be greater than 0.")
    if not args.root.exists():
        parser.error(f"--root does not exist: {args.root}")
    if not args.root.is_dir():
        parser.error(f"--root must be a directory: {args.root}")
    return args


def discover_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        current_dir = pathlib.Path(dirpath)
        for filename in filenames:
            path = current_dir / filename
            if path.suffix.lower() in TRANSLATABLE_EXTENSIONS:
                files.append(path)
    return sorted(files)


def chunk_text(text, max_chars=7000):
    paragraphs = text.split("\n\n")
    chunks = []
    current = []
    current_len = 0

    for paragraph in paragraphs:
        block = paragraph.rstrip() + "\n\n"
        if current and current_len + len(block) > max_chars:
            chunks.append("".join(current).rstrip())
            current = [block]
            current_len = len(block)
        else:
            current.append(block)
            current_len += len(block)

    if current:
        chunks.append("".join(current).rstrip())
    return chunks


def translate_chunk(text, api_key, base_url, model, target_language):
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Translate the following text into {target_language}, preserving markdown formatting, code fences, tables, links, and inline code exactly. "
                    f"Only translate natural language portions and leave code examples unmodified.\n\n{text}"
                ),
            },
        ],
        "temperature": 0.1,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected Deepseek response: {data}")
    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise RuntimeError(f"Unexpected Deepseek response: {data}")
    choice = choices[0]
    if not isinstance(choice, dict):
        raise RuntimeError(f"Unexpected Deepseek response: {data}")
    message = choice.get("message")
    if not isinstance(message, dict):
        raise RuntimeError(f"Unexpected Deepseek response: {data}")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"Unexpected Deepseek response: {data}")
    return content.strip()


def translate_file(path, api_key, base_url, model, target_language, max_chunk_chars):
    source_text = path.read_text(encoding="utf-8")
    chunks = chunk_text(source_text, max_chars=max_chunk_chars)
    translated_chunks = []
    for index, chunk in enumerate(chunks, start=1):
        translated = translate_chunk(
            chunk,
            api_key,
            base_url,
            model,
            target_language,
        )
        translated_chunks.append(translated)
        if index < len(chunks):
            time.sleep(1.0)
    return "\n\n".join(translated_chunks)


def output_path(path, suffix, overwrite):
    if overwrite:
        return path
    stem = path.stem + suffix
    return path.with_name(stem + path.suffix)


def main():
    args = parse_args()
    files = discover_files(args.root)

    if not files:
        print("No translatable files found.")
        return

    print(f"Found {len(files)} file(s) to translate.")
    for path in files:
        out_path = output_path(path, args.suffix, args.overwrite)
        print(f"- {path.relative_to(args.root)} -> {out_path.name}")
        if args.dry_run:
            continue

        translated = translate_file(
            path,
            os.environ["DEEPSEEK_API_KEY"],
            args.base_url,
            args.model,
            args.lang,
            args.max_chunk_chars,
        )

        out_path.write_text(translated + "\n", encoding="utf-8")
        print(f"  translated: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
