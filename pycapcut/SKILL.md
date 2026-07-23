---
name: pycapcut
description: Programmatically generate CapCut video drafts using pyCapCut — add video/audio/text/effects, import SRTs, use templates, and batch export
---

# pyCapCut

Python library for generating CapCut draft projects via code. Enables fully automated video editing pipelines without touching the GUI.

**Install:** `pip install pycapcut`
**Repo:** https://github.com/GuanYixuan/pyCapCut
**Note:** Drafts generated on Linux/macOS must be exported via Windows CapCut.

---

## Core Concepts

- Time is specified as strings: `"1.5s"`, `"1h3m12s"` — internally stored as microseconds
- `trange(start, duration)` — creates a `Timerange`
- Source timerange = portion of the asset to use; Target timerange = where it lands on the timeline
- Tracks are layered; higher index = visually on top

---

## Setup

```python
import pycapcut as cc

# Point to CapCut drafts folder
draft_folder = cc.DraftFolder("/path/to/CapCut/User Data/Projects/com.lveditor.draft")

# Create new draft (width, height in px)
script = draft_folder.create_draft("my_project", 1920, 1080)
```

---

## Adding Video

```python
mat = cc.VideoMaterial("clip.mp4")

# Full clip
seg = cc.VideoSegment(mat, cc.trange("0s", "10s"))

# Crop source: use seconds 2–7 of the file, place at 0–5s on timeline
seg = cc.VideoSegment(mat,
    source_timerange=cc.trange("2s", "5s"),
    target_timerange=cc.trange("0s", "5s")
)

script.add_segment(seg)
```

### Video Properties
```python
seg.rotation = 90          # degrees
seg.scale = (1.5, 1.5)     # x, y
seg.brightness = 0.2       # -1.0 to 1.0
seg.contrast = 0.1
seg.saturation = -0.3
seg.speed = 2.0            # playback speed multiplier
seg.volume = 0.8           # 0.0 to 1.0
```

---

## Adding Audio

```python
mat = cc.AudioMaterial("music.mp3")
seg = cc.AudioSegment(mat, cc.trange("0s", "30s"))

# Fade in/out
seg.fade_in = cc.trange("0s", "2s")
seg.fade_out = cc.trange("28s", "2s")

script.add_segment(seg)
```

---

## Adding Text

```python
seg = cc.TextSegment(
    text="Hello World",
    target_timerange=cc.trange("0s", "3s"),
    font=cc.FontType.文轩体,   # use cc.FontType.<name>
    font_size=10.0,
    bold=True,
    italic=False,
    color=(1.0, 1.0, 1.0),   # RGB 0–1
    position=(0.0, -0.3),    # x, y relative to center
)
script.add_segment(seg)
```

### Import SRT Subtitles
```python
script.import_srt("subtitles.srt", font_size=8.0, color=(1, 1, 1))
```

---

## Effects & Filters

```python
# Effect on a segment
seg.add_effect("Shake")

# Filter (color grade)
seg.add_filter("Vintage")

# Global filter on entire draft
script.add_filter("Film Grain", intensity=0.5)
```

---

## Animations & Keyframes

```python
# Preset animation
seg.add_animation("Fade In", duration="0.5s")

# Keyframe animation (position)
seg.add_keyframe(time="0s",  property="position", value=(0.0, 0.0))
seg.add_keyframe(time="3s",  property="position", value=(0.5, 0.3))

# Keyframe scale
seg.add_keyframe(time="0s",  property="scale", value=(1.0, 1.0))
seg.add_keyframe(time="2s",  property="scale", value=(1.5, 1.5))
```

---

## Masks

```python
seg.add_mask("circle", feather=0.1, radius=0.5)
seg.add_mask("rectangle", width=0.8, height=0.6, rotation=0)
```

---

## Tracks

By default `add_segment()` auto-assigns tracks. To control layering:

```python
track = script.add_track(cc.TrackType.VIDEO)
track.add_segment(seg)
```

Track types: `VIDEO`, `AUDIO`, `TEXT`, `EFFECT`, `FILTER`

---

## Template Mode

Use an existing draft as a template, swap assets by name:

```python
# Duplicate existing draft as template base
new_draft = draft_folder.duplicate_as_template("template_draft", "output_draft")

# Replace a video asset by its filename
new_draft.replace_material_by_name("old_clip.mp4", cc.VideoMaterial("new_clip.mp4"))

# Replace text content
new_draft.replace_text_by_index(0, "New caption here")

# Import a track from another draft
source = draft_folder.load_draft("source_draft")
new_draft.import_track(source, track_index=0)
```

---

## Batch Export

Control CapCut to export programmatically (Windows only):

```python
exporter = cc.CapCutExporter()
exporter.open_draft("my_project")
exporter.set_resolution(1920, 1080)
exporter.set_framerate(30)
exporter.export(output_path="/path/to/output.mp4")
```

---

## Full Example

```python
import pycapcut as cc

draft_folder = cc.DraftFolder("/path/to/CapCut/drafts")
script = draft_folder.create_draft("demo", 1920, 1080)

# Background video
bg = cc.VideoSegment(cc.VideoMaterial("bg.mp4"), cc.trange("0s", "10s"))
script.add_segment(bg)

# Music
music = cc.AudioSegment(cc.AudioMaterial("music.mp3"), cc.trange("0s", "10s"))
music.fade_in = cc.trange("0s", "1s")
music.fade_out = cc.trange("9s", "1s")
script.add_segment(music)

# Title text
title = cc.TextSegment(
    "My Video",
    cc.trange("1s", "3s"),
    font_size=12.0,
    bold=True,
    color=(1, 1, 0),
    position=(0.0, 0.4),
)
title.add_animation("Fade In", duration="0.5s")
script.add_segment(title)

# Subtitles
script.import_srt("subs.srt")

print("Draft created successfully.")
```

---

## Tips

- Always use absolute paths for media files — CapCut won't find relative ones
- Check `cc.FontType` members for available fonts (Chinese + Latin)
- `trange(start, duration)` not `trange(start, end)` — second arg is duration
- Draft JSON lives at `<drafts_folder>/<draft_name>/draft_content.json` — can be inspected/edited directly
- Unencrypted drafts only; CapCut cloud-synced drafts may be encrypted
