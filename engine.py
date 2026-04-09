#!/usr/bin/env python3
"""
Portrait Engine  -Unified AI image generation CLI.
Reads prompt templates from prompts.json, calls Gemini API, saves outputs.

Usage:
    python engine.py enhance photo.jpg --style studio-classic --output ./out
    python engine.py cartoon photo.jpg --style pixar,comic-pop --output ./out
    python engine.py anime photo.jpg --style ghibli,jjk --output ./out
    python engine.py generate --prompt "description" --count 3 --output ./out
    python engine.py list [--mode anime]
"""
import argparse
import json
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types

SCRIPT_DIR = Path(__file__).parent
PROMPTS_FILE = SCRIPT_DIR / "prompts.json"


class PortraitEngine:
    def __init__(self, api_key: str, prompts_path: Path = PROMPTS_FILE):
        self.client = genai.Client(api_key=api_key)
        self.prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        self.model = self.prompts["model"]

    def list_styles(self, mode: str | None = None):
        modes = self.prompts["modes"]
        if mode:
            if mode not in modes:
                print(f"ERROR: Unknown mode '{mode}'. Available: {', '.join(modes)}")
                return
            modes = {mode: modes[mode]}

        for mode_name, mode_data in modes.items():
            print(f"\n{'=' * 50}")
            print(f"  {mode_name.upper()}  -{mode_data['description']}")
            print(f"  Image required: {mode_data['requires_image']}")
            print(f"{'=' * 50}")
            if not mode_data["styles"]:
                print("  (freeform  -use --prompt)")
                continue
            for style_name, style_data in mode_data["styles"].items():
                status = style_data.get("status", "draft")
                marker = "[T]" if status == "tested" else "[ ]"
                print(f"  {marker} {style_name:20s} - {style_data['description']}")

    def generate(
        self,
        mode: str,
        input_path: Path | None = None,
        styles: list[str] | None = None,
        custom_prompt: str | None = None,
        output_dir: Path = Path("./portraits"),
        count: int = 1,
    ) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        mode_data = self.prompts["modes"].get(mode)
        if not mode_data:
            print(f"ERROR: Unknown mode '{mode}'")
            return []

        # Validate image requirement
        if mode_data["requires_image"] and not input_path:
            print(f"ERROR: Mode '{mode}' requires an input image")
            return []
        if input_path and not input_path.exists():
            print(f"ERROR: Input image not found: {input_path}")
            return []

        # Load input image if needed
        image_part = None
        if input_path:
            img_bytes = input_path.read_bytes()
            mime = "image/png" if input_path.suffix.lower() == ".png" else "image/jpeg"
            image_part = types.Part.from_bytes(data=img_bytes, mime_type=mime)

        # Build generation tasks
        tasks = []
        if mode == "generate":
            if not custom_prompt:
                print("ERROR: Mode 'generate' requires --prompt")
                return []
            for i in range(count):
                tasks.append(("custom", custom_prompt, i + 1))
        else:
            if not styles:
                print(f"ERROR: Specify --style for mode '{mode}'")
                return []
            available = mode_data["styles"]
            if styles == ["all"]:
                styles = list(available.keys())
            for style in styles:
                if style not in available:
                    print(f"WARNING: Unknown style '{style}' in mode '{mode}', skipping")
                    continue
                prompt = available[style]["prompt"]
                for i in range(count):
                    tasks.append((style, prompt, i + 1))

        # Execute
        saved = []
        for style_name, prompt, idx in tasks:
            suffix = f"_{idx}" if count > 1 else ""
            label = f"{mode}_{style_name}{suffix}"
            print(f"\nGenerating: {label}...")

            try:
                contents = [prompt]
                if image_part:
                    contents.append(image_part)

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                    ),
                )

                img_saved = False
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        data = part.inline_data.data
                        mime = part.inline_data.mime_type or "image/png"
                        ext = "png" if "png" in mime else "jpg"
                        out_path = output_dir / f"{label}.{ext}"
                        out_path.write_bytes(data)
                        size_kb = len(data) // 1024
                        print(f"  SAVED: {out_path} ({size_kb} KB)")
                        saved.append(out_path)
                        img_saved = True
                    elif part.text:
                        print(f"  Note: {part.text[:150]}")

                if not img_saved:
                    print(f"  WARNING: No image in response for {label}")

            except Exception as e:
                print(f"  ERROR: {e}")

        return saved


def main():
    parser = argparse.ArgumentParser(
        description="Portrait Engine  -AI image generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- list ---
    p_list = sub.add_parser("list", help="List available styles")
    p_list.add_argument("--mode", help="Filter by mode")

    # --- enhance ---
    p_enh = sub.add_parser("enhance", help="Professional headshot enhancement (i2i)")
    p_enh.add_argument("image", type=Path, help="Input image path")
    p_enh.add_argument("--style", required=True, help="Style(s), comma-separated or 'all'")
    p_enh.add_argument("--count", type=int, default=1, help="Variations per style")
    p_enh.add_argument("--output", type=Path, default=Path("./portraits"), help="Output dir")

    # --- cartoon ---
    p_car = sub.add_parser("cartoon", help="Cartoon style transfer (i2i)")
    p_car.add_argument("image", type=Path, help="Input image path")
    p_car.add_argument("--style", required=True, help="Style(s), comma-separated or 'all'")
    p_car.add_argument("--count", type=int, default=1, help="Variations per style")
    p_car.add_argument("--output", type=Path, default=Path("./portraits"), help="Output dir")

    # --- anime ---
    p_ani = sub.add_parser("anime", help="Anime style transfer (i2i)")
    p_ani.add_argument("image", type=Path, help="Input image path")
    p_ani.add_argument("--style", required=True, help="Style(s), comma-separated or 'all'")
    p_ani.add_argument("--count", type=int, default=1, help="Variations per style")
    p_ani.add_argument("--output", type=Path, default=Path("./portraits"), help="Output dir")

    # --- generate ---
    p_gen = sub.add_parser("generate", help="Text-to-image generation")
    p_gen.add_argument("--prompt", required=True, help="Image description")
    p_gen.add_argument("--count", type=int, default=1, help="Number of images")
    p_gen.add_argument("--output", type=Path, default=Path("./portraits"), help="Output dir")

    args = parser.parse_args()

    # API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    engine = PortraitEngine(api_key)

    if args.command == "list":
        engine.list_styles(args.mode)
        return

    if args.command == "generate":
        saved = engine.generate(
            mode="generate",
            custom_prompt=args.prompt,
            output_dir=args.output,
            count=args.count,
        )
    else:
        styles = [s.strip() for s in args.style.split(",")]
        saved = engine.generate(
            mode=args.command,
            input_path=args.image,
            styles=styles,
            output_dir=args.output,
            count=args.count,
        )

    if saved:
        print(f"\n{'=' * 50}")
        print(f"Done! {len(saved)} image(s) saved to {args.output}")
        for p in saved:
            print(f"  {p}")
        print(f"{'=' * 50}")
    else:
        print("\nNo images generated.")
        sys.exit(1)


if __name__ == "__main__":
    main()
