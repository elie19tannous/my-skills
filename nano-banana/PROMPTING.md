# Nano-Banana Prompt Engineering Guide

Use this guide to enhance user prompts for higher quality image generation.

## Prompt Structure Formula

**[Subject] + [Style/Medium] + [Lighting] + [Camera/Composition] + [Quality Modifiers]**

### Example Transformations

| User says | Enhanced prompt |
|-----------|-----------------|
| "a cat" | "A fluffy orange tabby cat with bright green eyes, photorealistic, soft natural window lighting, shallow depth of field, rule of thirds composition" |
| "cyberpunk city" | "A neon-lit cyberpunk metropolis at night, rain-slicked streets reflecting holographic advertisements, cinematic wide shot, Blade Runner aesthetic, volumetric fog, 85mm lens perspective" |
| "portrait of a woman" | "Editorial portrait of a woman with flowing auburn hair, Vanity Fair style, three-point studio lighting with soft key light at 45 degrees, Canon EOS R5, f/2.8, neutral background" |

## Style Keywords by Category

### Photography Styles
- `photorealistic`, `editorial photography`, `fashion photography`
- `street photography`, `portrait photography`, `macro photography`
- `documentary style`, `Pulitzer prize-winning photo`
- `Vanity Fair cover`, `National Geographic style`

### Art Styles
- `oil painting`, `watercolor`, `digital art`, `concept art`
- `3D render`, `Pixar style`, `Studio Ghibli style`
- `art nouveau`, `art deco`, `impressionist`
- `hyperrealistic`, `surrealist`, `minimalist`

### Cinematic Styles
- `film noir`, `cinematic`, `anamorphic lens flare`
- `IMAX quality`, `35mm film grain`, `Kodak Portra 400`
- `Christopher Nolan style`, `Wes Anderson aesthetic`

## Lighting Keywords

| Effect | Keywords |
|--------|----------|
| Soft/Natural | `soft diffused light`, `overcast lighting`, `natural window light` |
| Dramatic | `chiaroscuro`, `Rembrandt lighting`, `hard shadows` |
| Golden | `golden hour`, `warm sunset glow`, `magic hour` |
| Studio | `three-point lighting`, `softbox`, `rim light`, `key light at 45°` |
| Neon/Stylized | `neon glow`, `cyberpunk lighting`, `volumetric light rays` |
| Specific | `neutral diffuse 3PM lighting`, `backlighting`, `side lighting` |

## Camera & Composition Keywords

### Lens & Technical
- `85mm portrait lens`, `35mm wide angle`, `macro lens`
- `f/1.4 shallow depth of field`, `f/8 sharp throughout`
- `bokeh background`, `tilt-shift effect`
- `Canon EOS R5`, `Hasselblad medium format`

### Angles & Framing
- `eye level`, `low angle`, `bird's eye view`, `Dutch angle`
- `extreme close-up`, `medium shot`, `wide establishing shot`
- `rule of thirds`, `centered composition`, `negative space`
- `leading lines`, `frame within frame`, `symmetrical`

## Quality Modifiers

### DO Use
- `highly detailed`, `intricate details`, `sharp focus`
- `professional quality`, `award-winning`, `museum quality`
- `8K resolution`, `ultra HD`, `crystal clear`

### DON'T Use (outdated spam)
- ~~`4k, trending on artstation, masterpiece`~~ (Nano Banana understands natural language)
- ~~`best quality, ultra detailed`~~ (be specific instead)

## Advanced Techniques

### Use Capitalization for Emphasis
```
"A cat MUST be orange. The background MUST be a garden."
```

### Use Hex Colors for Precision
```
"A sports car in #FF4500 orange with #1A1A1A matte black accents"
```

### Use Markdown Lists for Multiple Requirements
```
"Create an image with ALL of the following:
- A woman in a red dress
- Standing in a wheat field
- Golden hour lighting
- Wind blowing her hair to the left"
```

### Negative Prompts (Exclusions)
```
"...NEVER include text, watermarks, or logos. Avoid cluttered backgrounds."
```

### Text in Images
Be explicit about text:
```
"Write the text 'HELLO WORLD' in bold, white, sans-serif font centered at the top"
```

## Prompt Templates by Use Case

### Product Photography
```
"[Product] on a [surface], professional product photography, soft studio lighting with subtle reflections, clean white background, commercial quality, sharp focus throughout"
```

### Character Portrait
```
"[Character description], [art style], dramatic rim lighting, [emotion] expression, detailed facial features, [camera angle], professional portrait composition"
```

### Landscape/Environment
```
"[Scene description], [time of day], [weather/atmosphere], [art style], epic wide shot, volumetric lighting, highly detailed environment, cinematic composition"
```

### UI/Mockup
```
"[Device] displaying [content], minimalist setting, soft gradient background, professional tech photography, clean shadows, Apple-style product shot"
```

### Fantasy/Sci-Fi
```
"[Subject] in [setting], [genre] aesthetic, dramatic volumetric lighting, intricate details, concept art style, epic scale, [mood] atmosphere"
```

## Common Fixes

| Problem | Solution |
|---------|----------|
| Blurry/soft | Add `sharp focus`, `highly detailed`, specific lens like `85mm f/1.8` |
| Wrong colors | Use hex codes: `#FF5733` instead of "orange-red" |
| Cluttered | Add `clean composition`, `negative space`, `minimalist` |
| Wrong style | Be more specific: `oil painting on canvas` not just `painting` |
| Bad lighting | Specify: `soft diffused lighting from upper left` |
| Text issues | Be explicit: `"TEXT HERE" in bold white Arial font` |

## Sources

- [Google's Official Nano Banana Pro Tips](https://blog.google/products/gemini/prompting-tips-nano-banana-pro/)
- [Max Woolf's Prompt Engineering Guide](https://minimaxir.com/2025/11/nano-banana-prompts/)
