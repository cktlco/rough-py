"""
A utility script that processes JSON files containing SVG data and prompts,
then applies roughening variants to each file using a peer script `test_roughen_svg.py`.
Also generates an HTML index for easy comparison.

Prerequisite:
- Download the dataset (JSON files): https://huggingface.co/datasets/MrOvkill/svg-stack-labeled

Run it directly:
  poetry run python tests/test_svg_stack_dataset.py --help

Note:
  This isn't a typical unit test for pytest, but it lives in tests/ for convenience.
  It's best run manually or via 'pytest -s tests/test_svg_stack_dataset.py'
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

MAX_DURATION = 30  # seconds


def write_html_item_header(
    html_file, filename: str, prompt: str, original_svg: str
) -> None:
    """
    Writes the initial HTML markup for an item block, displaying a filename, prompt,
    and the 'original' SVG reference.
    """
    lines = [
        "<div class='item'>",
        f"<h3>{filename}</h3>",
        f"<p>{prompt}</p>",
        "<div class='images'>",
        f"<div><div>Original</div><img src='{original_svg}' alt='Original SVG'></div>",
    ]
    html_file.write("\n".join(lines) + "\n")
    html_file.flush()


def append_variant_to_html(html_file, gap: float, variant_svg: str) -> None:
    """
    Adds a new image variant for a specific hachure gap setting.
    """
    line = f"<div><div>Gap: {gap}</div><img src='{variant_svg}' alt='Variant SVG (gap {gap})'></div>"
    html_file.write(line + "\n")
    html_file.flush()


def close_html_item(html_file) -> None:
    """
    Ends the item block in the HTML file.
    """
    html_file.write("</div>\n</div>\n")
    html_file.flush()


def process_and_update(
    json_path: str, output_dir: str, roughness: float, html_file
) -> None:
    """
    Reads one JSON file, extracts its SVG data and prompt, writes an original SVG, then
    generates 'roughened' variants with different hachureGap values (0.3 - 3.0).
    Keeps track of runtime to abort early if slow, and updates the HTML index.
    """
    base = os.path.splitext(os.path.basename(json_path))[0]
    print(f"Processing file: {base}")

    # read JSON; get svg data and prompt
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    svg_data = data.get("svg", "")
    prompt = data.get("prompt", "")
    if "ASSISTANT:" in prompt:
        # remove any extraneous label
        prompt = prompt.split("ASSISTANT:", 1)[1].strip().replace("The image is a", "A")

    # write original SVG
    original_svg_path = os.path.join(output_dir, f"{base}.svg")
    with open(original_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_data)

    # item block in HTML
    write_html_item_header(html_file, base, prompt, os.path.basename(original_svg_path))

    # run default variant with gap=1.0, measure elapsed time
    default_variant_path = os.path.join(output_dir, f"{base}_rough_gap_1.0.svg")
    cmd_default = [
        "poetry",
        "run",
        "python",
        "tests/test_roughen_svg.py",
        "--input-svg",
        original_svg_path,
        "-o",
        default_variant_path,
        "--roughness",
        str(roughness),
        "--hachure-gap",
        "1.0",
    ]
    start_time = time.monotonic()
    subprocess.run(cmd_default, check=True)
    elapsed = time.monotonic() - start_time

    if elapsed > MAX_DURATION:
        # too slow: only include the default variant
        append_variant_to_html(html_file, 1.0, os.path.basename(default_variant_path))
    else:
        # process multiple gap variants
        for gap in [0.5, 1.0, 2.0, 3.5, 5.0]:
            print(f"Processing {base} variant with hachure-gap={gap}")
            variant_path = os.path.join(output_dir, f"{base}_rough_gap_{gap}.svg")
            cmd_variant = [
                "poetry",
                "run",
                "python",
                "tests/test_roughen_svg.py",
                "--input-svg",
                original_svg_path,
                "-o",
                variant_path,
                "--roughness",
                str(roughness),
                "--hachure-gap",
                str(gap),
            ]
            subprocess.run(cmd_variant, check=True)
            append_variant_to_html(html_file, gap, os.path.basename(variant_path))

    close_html_item(html_file)


def write_html_header(html_file) -> None:
    """
    Writes standard HTML preamble, styling, etc.
    """
    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head><meta charset='UTF-8'><title>rough-py tested on the svg-stack dataset</title>",
        "<style>",
        "body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; margin: 20px; }",
        ".item { margin: 10px 0; padding: 10px; background-color: #1e1e1e; }",
        ".images { display: flex; flex-wrap: wrap; justify-content: space-around; }",
        ".images div { margin: 5px; text-align: center; }",
        ".images img { width: 300px; height: auto; min-height: 300px; border: none; }",
        "h3 { color: #ccc; margin: 5px 0; }",
        "a { color: #82aaff; }",
        "</style></head>",
        "<body>",
        "<h1>SVG Comparison</h1>",
    ]
    html_file.write("\n".join(lines) + "\n")
    html_file.flush()


def finalize_html(html_file) -> None:
    """
    Closes out the HTML document.
    """
    html_file.write("</body>\n</html>\n")
    html_file.flush()


def main() -> None:
    """
    Processes a random subset of JSON files (default=1). For each file, extracts
    original SVG plus roughened variants. Writes an HTML summary to 'index.html'.
    """
    parser = argparse.ArgumentParser(
        description="Roughen a random subset of SVG JSON files."
    )
    parser.add_argument("input_dir", help="Directory with JSON files")
    parser.add_argument("output_dir", help="Directory for SVG files and index.html")
    parser.add_argument("--roughness", type=float, default=1.5, help="Roughness value")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=1,
        help="Number of random JSON files to process (default=1).",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        sys.exit("Input directory does not exist.")

    os.makedirs(args.output_dir, exist_ok=True)
    html_path = os.path.join(args.output_dir, "index.html")

    # gather json files, pick a subset
    all_json_files = [
        os.path.join(args.input_dir, f)
        for f in os.listdir(args.input_dir)
        if f.endswith(".json")
    ]
    if not all_json_files:
        sys.exit("No .json files found in input_dir.")

    random.shuffle(all_json_files)
    selected_json_files = all_json_files[: args.sample_size]

    with open(html_path, "w", encoding="utf-8") as html_file:
        write_html_header(html_file)
        for json_path in selected_json_files:
            try:
                process_and_update(
                    json_path, args.output_dir, args.roughness, html_file
                )
            except subprocess.CalledProcessError:
                print(f"Error processing {json_path}. Skipping.")
                continue
        finalize_html(html_file)

    # print the location for easy access
    out_file_resolved = Path(html_path).resolve()
    print(f"\nWrote file:///X:{str(out_file_resolved).replace('dev_local/', '')}")


if __name__ == "__main__":
    main()
