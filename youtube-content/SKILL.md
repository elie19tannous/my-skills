---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Listing a channel's recent videos (with dates, no auth)

`yt-dlp --flat-playlist` returns `upload_date` as `NA`, and a full `yt-dlp` metadata pull triggers the bot-block (see below). To get the latest ~15 videos WITH real publish dates and no auth, use the channel RSS feed:

```bash
# 1. Resolve channel id (UC...) from the handle/page
curl -s "https://www.youtube.com/@HANDLE" -A "Mozilla/5.0" -L | grep -oE 'UC[a-zA-Z0-9_-]{22}' | head -1

# 2. Pull the RSS feed (last ~15 videos, with <published> dates)
curl -s "https://www.youtube.com/feeds/videos.xml?channel_id=UC_xxxxx" | python3 -c "
import sys,re
d=sys.stdin.read()
for e in re.findall(r'<entry>.*?</entry>', d, re.S):
    vid=re.search(r'<yt:videoId>(.*?)</yt:videoId>', e)
    pub=re.search(r'<published>(.*?)</published>', e)
    title=re.search(r'<title>(.*?)</title>', e)
    print((vid and vid.group(1)),'|',(pub and pub.group(1)[:10]),'|',(title and title.group(1)))
"
```

Note: `?user=NAME` form of the feed 404s for most channels — always use `?channel_id=UC...`. Feed only carries ~15 newest videos; for date-windowed asks (e.g. "last 14 days") this is usually enough.

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps
- **Tactics / claims map**: a traceable catalog table extracting every technique, claim, or event across one or MORE transcripts — each row carries a verbatim quote anchor + source-file ID so a reviewer can locate it. Used for legal/research review. See `references/evidence-mapping.md`.

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
- **"Sign in to confirm you're not a bot" / "YouTube is blocking requests from your IP"**: YouTube blocks cloud-provider IPs (AWS/GCP/Azure/Hetzner). Both `yt-dlp` and `youtube-transcript-api` can hit this on a server. Before giving up or asking for a proxy, try a transcript-only HTTP fallback for public-captioned videos:
  ```bash
  curl -L "https://youtube-transcript.ai/transcript/VIDEO_ID.txt" -o transcript.txt
  ```
  In the Lawcal AI OS session this returned full transcripts for four videos when `youtube-transcript-api` was blocked. If it fails or returns non-transcript content, then use the cloud-IP workaround options in `references/cloud-ip-block.md` (paid proxy key like Webshare → `GenericProxyConfig`, or a paid transcript API).
