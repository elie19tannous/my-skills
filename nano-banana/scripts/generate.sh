#!/bin/bash
# Nano-Banana (Gemini Image Generation) script
# Supports both Flash (fast) and Pro (high-res) models
# Runs in background with notification on completion

set -e

# Parse arguments
PROMPT=""
OUTPUT=""
ASPECT="1:1"
SIZE="1K"
MODEL="pro"  # pro (default) or flash
REFERENCE=""  # Reference image for image-to-image

while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --aspect)
      ASPECT="$2"
      shift 2
      ;;
    --size)
      SIZE="$2"
      shift 2
      ;;
    --pro)
      MODEL="pro"
      shift
      ;;
    --flash)
      MODEL="flash"
      shift
      ;;
    --reference)
      REFERENCE="$2"
      shift 2
      ;;
    *)
      if [[ -z "$PROMPT" ]]; then
        PROMPT="$1"
      else
        PROMPT="$PROMPT $1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Usage: generate.sh \"prompt\" [options]"
  echo ""
  echo "Options:"
  echo "  --output PATH      Save to specific path (default: ~/Pictures/nano-banana/)"
  echo "  --aspect RATIO     Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:4 (default: 1:1)"
  echo "  --size SIZE        Resolution: 1K, 2K, 4K (default: 1K, Pro model only for 2K/4K)"
  echo "  --pro              Use Pro model (slower, higher quality, supports 2K/4K)"
  echo "  --flash            Use Flash model (faster, default)"
  echo "  --reference IMAGE  Reference image for character consistency (image-to-image)"
  exit 1
fi

# Validate reference image if provided
if [[ -n "$REFERENCE" && ! -f "$REFERENCE" ]]; then
  echo "Error: Reference image not found: $REFERENCE"
  exit 1
fi

# Force pro model for high-res
if [[ "$SIZE" == "2K" || "$SIZE" == "4K" ]]; then
  MODEL="pro"
fi

# Check for API key - try env var first, then Keychain
if [[ -z "$GEMINI_API_KEY" ]]; then
  GEMINI_API_KEY=$(security find-generic-password -a "$USER" -s "GEMINI_API_KEY" -w 2>/dev/null)
fi

if [[ -z "$GEMINI_API_KEY" ]]; then
  echo "Error: GEMINI_API_KEY not found"
  echo "Set it via:"
  echo "  1. Environment variable: export GEMINI_API_KEY=your-key"
  echo "  2. Keychain: security add-generic-password -a \"\$USER\" -s \"GEMINI_API_KEY\" -w \"your-key\""
  exit 1
fi

# Set model endpoint
if [[ "$MODEL" == "pro" ]]; then
  MODEL_ID="gemini-3-pro-image-preview"
  MODEL_DISPLAY="Pro (Nano-Banana Pro / Gemini 3)"
else
  MODEL_ID="gemini-2.5-flash-image"
  MODEL_DISPLAY="Flash (Nano-Banana)"
fi

# Set output path
OUTPUT_DIR="$HOME/Pictures/nano-banana"
mkdir -p "$OUTPUT_DIR"

if [[ -z "$OUTPUT" ]]; then
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  OUTPUT="$OUTPUT_DIR/$TIMESTAMP.png"
fi

ERROR_LOG="$HOME/.claude/skills/nano-banana/last-error.log"

echo "Generating image in background..."
echo "Prompt: $PROMPT"
echo "Model: $MODEL_DISPLAY"
echo "Size: $SIZE"
echo "Aspect: $ASPECT"
if [[ -n "$REFERENCE" ]]; then
  echo "Reference: $REFERENCE"
fi
echo "Output: $OUTPUT"

# Run generation in background
(
  # Build the request body
  if [[ -n "$REFERENCE" ]]; then
    # Image-to-image: include reference image
    REF_BASE64=$(base64 -i "$REFERENCE" | tr -d '\n')
    REF_MIME="image/png"
    if [[ "$REFERENCE" == *.jpg || "$REFERENCE" == *.jpeg ]]; then
      REF_MIME="image/jpeg"
    fi
    REQUEST_BODY="{
      \"contents\": [{
        \"parts\": [
          {\"text\": \"$PROMPT\"},
          {\"inlineData\": {\"mimeType\": \"$REF_MIME\", \"data\": \"$REF_BASE64\"}}
        ]
      }],
      \"generationConfig\": {
        \"responseModalities\": [\"IMAGE\", \"TEXT\"]
      }
    }"
  else
    # Text-to-image: no reference
    REQUEST_BODY="{
      \"contents\": [{
        \"parts\": [{\"text\": \"$PROMPT\"}]
      }],
      \"generationConfig\": {
        \"responseModalities\": [\"IMAGE\", \"TEXT\"]
      }
    }"
  fi

  RESPONSE=$(curl -s -X POST \
    "https://generativelanguage.googleapis.com/v1beta/models/$MODEL_ID:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY" 2>"$ERROR_LOG")

  # Helper function for notifications
  notify() {
    local msg="$1"
    local title="$2"
    osascript -e "display notification \"$msg\" with title \"$title\"" 2>/dev/null || true
  }

  # Check for errors
  ERROR=$(echo "$RESPONSE" | jq -r '.error.message // empty' 2>/dev/null)
  if [[ -n "$ERROR" ]]; then
    echo "$RESPONSE" > "$ERROR_LOG"
    notify "Generation failed - check logs" "Nano-Banana"
    exit 1
  fi

  # Extract and decode image
  IMAGE_DATA=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data' 2>/dev/null)

  if [[ -z "$IMAGE_DATA" || "$IMAGE_DATA" == "null" ]]; then
    echo "$RESPONSE" > "$ERROR_LOG"
    notify "No image in response" "Nano-Banana"
    exit 1
  fi

  echo "$IMAGE_DATA" | base64 -d > "$OUTPUT"

  # Notify and open
  FILENAME=$(basename "$OUTPUT")
  notify "Saved: $FILENAME" "Nano-Banana"
  open "$OUTPUT"
) &

echo ""
echo "Image generation started in background."
echo "You'll get a notification when it's done."
