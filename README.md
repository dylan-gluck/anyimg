# AnyImg - Cli to generate images with Nano Banana

CLI for generating images using `Google Gemini 2.5 Flash` aka Nano Banana.

**Usage**
```bash
# CLI Command Structure:
anyimg [options] [prompt]

# Options:
--in        string    Image paths, comma separated  (optional)
--out       string    Save path                     (optional, default is current directory anyimg_$timestamp.png)
--batch     number    Number of times to run        (optional, default is 1)

# Example
anyimg --in ghost.png,frankenstein.png,haunted_house.png --out spooky-card.png "Spooky halloween card. Text to include: \"Have a SpoOoOky Halloween!\". Colors: Black, White, Orange, Purple. Size: 3x4"

anyimg --batch 5 "Cartoon jack-o-lantern with glowing eyes on black background"
```

*Note: `GEMINI_API_KEY` env variable required for use. Can be passed in at runtime or set globally. Eg: `GEMINI_API_KEY=sk... anyimg [options]`*

## References

Demo Project:
- /home/d/workspace/projects/logo-designer

Gemini Docs:
- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/video
