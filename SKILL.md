---
name: portrait
description: AI portrait generation via Gemini — enhance headshots, apply cartoon/anime styles, or generate from text. 32+ presets across 4 modes. Use when the user wants profile pictures, headshots, avatar art, anime portraits, or any AI image generation.
---

# Portrait Generator

Generate AI portraits using Google Gemini's image generation. Supports image-to-image enhancement and style transfer, plus text-to-image generation.

## When to Activate

- User says "portrait", "headshot", "profile picture", "avatar", "PFP"
- User says "cartoon me", "anime me", "make me look like", "stylize my photo"
- User says "generate an image", "create a picture", "AI image"
- User wants LinkedIn headshot, professional photo, or profile picture enhancement
- User mentions any anime style name (ghibli, jjk, edgerunners, etc.)

## Prerequisites

- `GEMINI_API_KEY` environment variable set (Google AI Studio, billed project)
- `google-genai` Python package installed (`python -m pip install google-genai`)

## Modes

| Mode | Input | Description |
|------|-------|-------------|
| `enhance` | Photo required | Professional headshot enhancement |
| `cartoon` | Photo required | Cartoon/artistic style transfer |
| `anime` | Photo required | Anime style transfer (20 styles) |
| `generate` | Text only | Freeform text-to-image |

## Style Presets

### enhance (5 styles)
| Style | Description |
|-------|-------------|
| `studio-classic` | Dark gradient backdrop, 3-point lighting, blazer + gray crew |
| `studio-warm` | Warm tones, Rembrandt lighting, suit + white shirt |
| `editorial` | Blurred office bokeh, cinematic lighting, charcoal blazer |
| `outdoor-natural` | Golden-hour warmth, soft outdoor bokeh |
| `startup-ceo` | Modern casual-professional, tech founder aesthetic |

### cartoon (7 styles)
| Style | Description |
|-------|-------------|
| `pixar` | Pixar/Disney 3D animated character |
| `comic-pop` | Bold comic book / pop art with halftone dots |
| `watercolor` | Loose watercolor painting with soft washes |
| `oil-painting` | Classical oil painting with rich impasto texture |
| `flat-vector` | Clean flat vector, modern tech company style |
| `caricature` | Exaggerated caricature, New Yorker style |
| `chibi` | Cute chibi/SD with oversized head |

### anime (20 styles)
| Style | Description |
|-------|-------------|
| `ghibli` | Warm, painterly, watercolor (Miyazaki) |
| `shinkai` | Dramatic skies, golden hour (Your Name) |
| `jjk` | Dark, neon cursed energy (Jujutsu Kaisen) |
| `demon-slayer` | Vibrant particles, patterned (Ufotable) |
| `chainsaw-man` | Gritty, desaturated, cinematic |
| `spy-x-family` | Clean, bright, expressive |
| `aot` | Dark military, intense (Attack on Titan) |
| `jojo` | Flamboyant, psychedelic (JoJo's) |
| `edgerunners` | Neon glow, punk (Studio Trigger) |
| `promare` | Geometric neon, poster art (Trigger) |
| `dbz` | Sharp angular, bold (Dragon Ball Z) |
| `sailor-moon` | Sparkles, pastels, 90s shojo |
| `akira` | Cyberpunk, gritty realism (1988) |
| `redline` | Retro-futuristic rockabilly |
| `mob-psycho` | Raw sketchy, psychic energy |
| `ping-pong` | Lo-fi, emotionally raw (Yuasa) |
| `mononoke-tv` | Ukiyo-e woodblock prints |
| `tatami-galaxy` | Pop-art chaos, geometric |
| `violet-evergarden` | Ultra-luxury, luminous (KyoAni) |
| `satoshi-kon` | Surreal, adult (Paprika) |

## Workflow

### 1. Parse the user's request

Determine: **mode**, **style(s)**, **input image path** (if i2i), **output directory**.

- If user provides an image → use `enhance`, `cartoon`, or `anime` mode
- If user just wants an image from description → use `generate` mode
- If style is unclear, show the style table and ask with `AskUserQuestion`
- Default output: `./portraits/` relative to user's working directory

### 2. Validate prerequisites

```bash
python -c "from google import genai; print('OK')"
echo $GEMINI_API_KEY
```

If missing, guide setup:
- SDK: `python -m pip install google-genai`
- Key: Go to https://aistudio.google.com/apikey — needs billed project

### 3. Run the engine

The engine lives at: `~/.claude/skills/portrait/engine.py`

```bash
# Image-to-image
python ~/.claude/skills/portrait/engine.py <mode> <image_path> --style <style> --output <output_dir>

# Text-to-image
python ~/.claude/skills/portrait/engine.py generate --prompt "<description>" --output <output_dir>

# Multiple styles (comma-separated)
python ~/.claude/skills/portrait/engine.py anime photo.jpg --style ghibli,jjk,edgerunners --output ./portraits

# All styles in a mode
python ~/.claude/skills/portrait/engine.py anime photo.jpg --style all --output ./portraits

# List available styles
python ~/.claude/skills/portrait/engine.py list [--mode anime]
```

### 4. Display results

After generation completes:
1. Read each saved image path from the engine output
2. Use the `Read` tool to display images inline to the user
3. If multiple styles, show them with labels for comparison

### 5. Iterate

If the user wants changes:
- Different style → rerun with new `--style`
- Multiple variations of same style → use `--count 2` or `--count 3`
- Custom tweaks → for `generate` mode, refine the `--prompt`

## Generate Mode — Prompt Crafting

When user asks for freeform text-to-image, craft a detailed prompt covering:
- Subject description (who/what)
- Style direction (photorealistic, illustrated, painterly, etc.)
- Lighting and atmosphere
- Color palette
- Composition and framing
- Background/environment

Pass the crafted prompt via `--prompt "..."` to the engine.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GEMINI_API_KEY not set` | `setx GEMINI_API_KEY "your-key"` then restart terminal |
| `429 RESOURCE_EXHAUSTED` | Free tier has limit=0 for image gen. Enable billing at aistudio.google.com/billing |
| `ModuleNotFoundError: google` | `python -m pip install google-genai` |
| `404 model not found` | Model name changed. Check with `engine.py list` |
