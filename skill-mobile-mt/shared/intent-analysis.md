# Intent Analysis — Deep Understanding Protocols

> On-demand module. Loaded when user input is multi-part, vague, rambling, non-technical, or ambiguous.
> Trigger: Task Router detects complexity signals → reads this file → applies matching protocol.

---

## Task Extraction Protocol (MANDATORY for multi-part requests)

**BEFORE any code: parse the user's FULL message and extract ALL tasks.**

```
⛔ NEVER start coding after reading only the first sentence.
⛔ NEVER say "done" when only 1 of N tasks is complete.
✅ ALWAYS re-read the original message after finishing to verify ALL tasks done.

STEP 1: EXTRACT — Read the ENTIRE user message. List every distinct task:
  Example user input (any language):
    "fix login UI, fix crash on back press, add loading state to profile"
    "sửa UI login, fix lỗi crash khi bấm back, thêm loading state cho profile"
  → TASK 1: Fix UI login screen
  → TASK 2: Fix crash on back press
  → TASK 3: Add loading state to profile screen

STEP 2: CLASSIFY each task:
  [UI]     → visual / layout / style / component changes
  [BUG]    → crash / error / wrong behavior
  [FEAT]   → new functionality
  [REFACTOR] → code improvement without behavior change
  [TEST]   → add / fix tests

STEP 3: ORDER by dependency:
  → Which tasks depend on other tasks? Do dependencies first.
  → Independent tasks can be done in any order.
  → If unsure, ask user: "Which task should I prioritize first?"

  Example:
    TASK 2 (crash fix) → do FIRST (may affect TASK 1)
    TASK 1 (UI fix)    → do SECOND
    TASK 3 (loading)   → do THIRD (independent)

STEP 4: TRACK progress as you work:
  ✅ TASK 2: Fixed crash on back press (HomeScreen.tsx:45)
  🔄 TASK 1: Fixing UI login (in progress)
  ⬜ TASK 3: Add loading state (pending)

STEP 5: RE-CHECK after "all done":
  → Re-read the original user message
  → Check EACH extracted task against actual changes
  → If any task was missed → do it now
  → Only say "done" when ALL tasks verified
```

### Multi-Part Detection (auto-trigger)

```
TRIGGER this protocol when user message contains ANY of:
  - Multiple sentences with different requests
  - List format ("1. ... 2. ... 3. ...")
  - Comma-separated requests ("fix A, fix B, add C")
  - Multi-language patterns (e.g., "sửa ... rồi ... xong ... thêm ...")
  - Quantity words in any language (e.g., "nhiều chỗ", "several places", "multiple files")
  - References to multiple files/screens/components

SINGLE TASK (skip this protocol):
  - "Fix the login button" → 1 task → go straight to Task Router
  - "Add dark mode" → 1 task → go straight to Task Router
```

---

## Scope Clarification Protocol (for vague / rambling input)

**BEFORE coding: detect if the request is vague. If yes → clarify scope first.**

```
⛔ NEVER start coding on a vague request.
⛔ NEVER guess what the user means by "make it better".
✅ ALWAYS set clear completion criteria BEFORE writing code.

═══ STEP 1: DETECT VAGUE INPUT ═══

VAGUE (must clarify):
  - "Make it better" → better HOW? performance? UI? code quality?
  - "Fix the UI" → which screen? which component? what's wrong?
  - "Improve this" → improve what aspect?
  - "It doesn't look right" → compared to what? which part?
  - "Fix everything" → everything = what scope?
  - "Clean up the code" → which files? what kind of cleanup?
  - "Something is wrong" → what symptom? which screen?

CLEAR (proceed directly):
  - "Fix the login button — it doesn't respond to tap" → specific target + symptom
  - "Add loading spinner to ProfileScreen" → specific component + screen
  - "Change header color from blue to red" → specific property + value
  - "The app crashes when I press back on OrderScreen" → specific screen + action + symptom

═══ STEP 2: EXTRACT INTENT FROM RAMBLING ═══

When user writes a long, unfocused message:

  1. READ the entire message — do not stop at first sentence
  2. EXTRACT the core intent:
     → What does the user actually WANT changed?
     → What is the SYMPTOM they're describing?
     → Which SCREEN / COMPONENT / FILE are they talking about?
  3. IGNORE filler words — focus on nouns (screen names, component names)
     and verbs (fix, add, change, remove, update, move)
  4. SUMMARIZE back to user:
     "I understand you want me to:
      1. [extracted task 1]
      2. [extracted task 2]
      Is this correct?"

  Example:
    User: "so basically the thing is when I go to the home screen it's like
           the button at the bottom is too small and also the text overlaps
           with the image and I think the color might be wrong too but I'm
           not sure, and also on the profile page there's this thing where
           it loads forever"

    AI extracts:
      1. HomeScreen — button too small (bottom)
      2. HomeScreen — text overlaps with image
      3. HomeScreen — color might be wrong (needs clarification)
      4. ProfileScreen — infinite loading (never resolves)

    AI responds:
      "I found 4 issues in your message:
       1. HomeScreen: bottom button too small
       2. HomeScreen: text overlapping image
       3. HomeScreen: color issue — which color/element specifically?
       4. ProfileScreen: loading never finishes
       Should I fix all 4? And can you clarify #3?"

═══ STEP 3: SET COMPLETION CRITERIA ═══

Before starting work, define WHEN you're done:

  VAGUE REQUEST          → CLARIFIED CRITERIA
  ─────────────────────────────────────────────────
  "Make it better"       → "Better" means: [list specific improvements]
  "Fix the UI"           → Fix: [component A], [component B] on [screen]
  "Improve performance"  → Target: [specific metric, e.g., list render < 16ms]
  "Clean up code"        → Clean: [specific files], changes: [refactor X, remove Y]
  "Fix everything"       → Fix: [list every issue found after scanning]

  If user confirms → proceed with those criteria
  If user changes scope → update criteria before coding
  When ALL criteria met → done. Do NOT keep "improving" beyond scope.

═══ STEP 4: STOP CONDITION ═══

⛔ DO NOT keep improving endlessly.
✅ STOP when all completion criteria are met.

  WRONG:
    User: "Fix the UI"
    AI: fixes button → fixes padding → fixes font → refactors stylesheet
        → adds animations → rewrites entire component...
    (never stops)

  RIGHT:
    User: "Fix the UI"
    AI: "Which screen and what's wrong specifically?"
    User: "HomeScreen — button and text overlap"
    AI: fixes button size + text overlap → verifies → done.
    "Fixed 2 issues on HomeScreen. Need anything else?"

═══ SCOPE ESCALATION ═══

If during work you discover MORE issues than originally scoped:
  → STOP — do NOT silently fix extra issues
  → REPORT: "While fixing [A], I also found [B] and [C]."
  → ASK: "Want me to fix those too, or just [A] for now?"
  → Only proceed with extras if user confirms

  This prevents:
  - Unexpected changes user didn't ask for
  - Breaking things by "fixing" working code
  - Wasting time on low-priority issues
  - AI deciding scope instead of user
```

---

## Intent Understanding Protocol

**Go beyond keyword matching — understand what the user actually means.**

```
═══ 1. IMPLICIT INTENT DETECTION ═══

User does NOT always say exactly what they want. Detect the REAL intent:

  USER SAYS (surface)              → REAL INTENT (hidden)
  ──────────────────────────────────────────────────────────────────
  "This is slow"                   → Fix performance (which screen/action?)
  "This doesn't feel right"        → UI/UX issue (layout? animation? spacing?)
  "It's broken"                    → Something crashes or shows wrong data
  "Can you take a look at this?"   → Review code / find bugs (which area?)
  "I don't like how this works"    → UX redesign (which flow?)
  "This used to work"              → Regression bug (what changed recently?)
  "Users are complaining about X"  → Bug or UX issue affecting real users (priority: high)
  "Is this okay?"                  → Code review / validation request
  "Almost done, just need to..."   → Final polish tasks (specific list)
  "I keep getting this..."         → Recurring error (needs root cause, not band-aid)

  HOW TO HANDLE:
    1. Detect implicit intent from context clues
    2. CONFIRM your interpretation: "It sounds like [X]. Is that right?"
    3. Only proceed after user confirms
    ⛔ NEVER silently assume — always confirm ambiguous intent

═══ 2. CONVERSATION CONTEXT TRACKING ═══

User may reference something from earlier in the conversation:

  "Fix that"           → "that" = last thing discussed
  "Same for this one"  → apply same fix to different target
  "The other screen"   → the screen mentioned before
  "Do it again"        → repeat last action on new target
  "Like before"        → use same approach as previous fix
  "Undo that"          → revert the last change made
  "What about X?"      → X from earlier context, not new topic

  HOW TO HANDLE:
    1. RESOLVE the reference — what does "that/this/it" point to?
    2. If clear → proceed with resolved reference
    3. If ambiguous → ASK: "You mean [A] or [B]?"
    ⛔ NEVER guess when a pronoun could refer to multiple things

  TRACKING RULES:
    - Keep track of: last file edited, last function discussed, last error fixed
    - "That bug" = the most recently discussed bug
    - "That screen" = the most recently discussed screen
    - "The same issue" = same error type, different location

═══ 3. NON-TECHNICAL LANGUAGE MAPPING ═══

User may describe technical problems in everyday language:

  NON-TECHNICAL                    → TECHNICAL MEANING
  ──────────────────────────────────────────────────────────────────
  "Button doesn't work"            → onPress handler broken / not wired
  "Screen is blank/white"          → Render error / data not loaded / crash
  "It freezes / hangs"             → Main thread blocked / infinite loop / deadlock
  "It flickers / flashes"          → Re-render loop / layout thrashing
  "Text is cut off"                → Container overflow / missing flex / numberOfLines
  "Things jump around"             → Layout shift / async content loading without placeholder
  "It takes forever"               → Slow API / no loading state / no caching
  "The app closes itself"          → Crash (check logs for stack trace)
  "It goes back to start"          → Navigation reset / session expired / auth issue
  "Keeps asking me to login"       → Token not persisted / refresh token broken
  "Shows old data"                 → Cache stale / no refetch / optimistic update broken
  "Works on mine, not on theirs"   → Device-specific / OS version / screen size
  "Weird characters showing"       → Encoding issue / i18n / font missing
  "Colors are wrong"               → Theme not applied / dark mode / platform default
  "Can't scroll"                   → ScrollView missing / gesture conflict / fixed height

  HOW TO HANDLE:
    1. MAP the non-technical description to technical possibilities (1-3 most likely)
    2. SEARCH the project code for the affected area
    3. NARROW DOWN to the actual cause by reading code
    4. FIX the actual cause, not just the symptom
    ⛔ NEVER ask user to "provide the error message" if they clearly don't have one
    ✅ Instead, investigate the code yourself based on their description

═══ 4. CONTRADICTORY REQUEST DETECTION ═══

User may ask for conflicting things without realizing:

  CONTRADICTION                    → HOW TO HANDLE
  ──────────────────────────────────────────────────────────────────
  "Add animation but keep it fast" → Explain trade-off: "Heavy animation may cause
                                     frame drops on older devices. Options:
                                     (A) Light animation (opacity/translate) — smooth
                                     (B) Complex animation (Lottie) — richer but heavier"

  "Make it simple but add all      → Explain: "Adding all features increases complexity.
   these features"                    Which features are must-have vs nice-to-have?"

  "Don't change the architecture   → Explain: "The current architecture doesn't support X
   but add X"                         cleanly. Options:
                                     (A) Fit X into current arch (works but messy)
                                     (B) Small refactor to support X properly"

  "Make it secure but don't add    → Explain: "Security requires validation.
   validation"                        Which inputs can we trust vs must validate?"

  HOW TO HANDLE:
    1. DETECT the conflict (two goals that oppose each other)
    2. EXPLAIN the trade-off clearly (not lecture — 2-3 sentences max)
    3. PRESENT options with pros/cons
    4. LET USER DECIDE — never silently pick one side
    ⛔ NEVER ignore contradictions — they lead to broken implementations

═══ 5. PRIORITY / URGENCY DETECTION ═══

User signals urgency differently. Adjust behavior accordingly:

  SIGNAL                           → BEHAVIOR
  ──────────────────────────────────────────────────────────────────
  "URGENT / ASAP / production      → Priority: CRITICAL
   is down / users affected"         → Skip nice-to-haves, fix the core issue
                                     → Minimal viable fix FIRST, refactor later
                                     → Communicate progress at every step

  "Fix this before release /       → Priority: HIGH
   deadline / blocker"               → Focus on this task only, no side-quests
                                     → Skip non-essential improvements
                                     → Verify fix works, move on

  "When you get a chance /         → Priority: LOW
   not urgent / nice to have /       → Can batch with other tasks
   someday / backlog"                → Thorough approach (refactor OK)
                                     → Ask clarifying questions freely

  "Quick fix / just make it work / → Priority: MEDIUM (but user wants speed)
   hack is fine for now"             → Working solution > perfect solution
                                     → Add TODO comment for later cleanup
                                     → Warn about technical debt if significant

  NO URGENCY SIGNAL                → Priority: NORMAL
                                     → Standard workflow (all protocols apply)
                                     → Balance speed and quality

  HOW TO HANDLE:
    1. DETECT urgency signals in user message
    2. ADJUST depth of work:
       CRITICAL → fix only, skip review/refactor
       HIGH     → fix + basic verify, skip extras
       NORMAL   → full workflow
       LOW      → thorough approach, explore options
    3. COMMUNICATE your approach: "Since this is urgent, I'll do a minimal
       fix now. We can refactor later."
    ⛔ NEVER add "while I'm at it" improvements during CRITICAL/HIGH tasks
```

---

## Spec Analysis Protocol (for vague feature requests)

**When user describes a feature/screen/flow loosely, ANALYZE before coding.**

```
⛔ NEVER start building a feature from a vague description.
⛔ NEVER assume missing details — ask.
✅ ALWAYS present a structured spec back to user for confirmation.

═══ WHEN TO TRIGGER ═══

  - User describes a new screen/feature/flow in plain language
  - User says "build X like other apps" / "something similar to Y"
  - User gives a list of requirements without clear structure
  - User pastes a design screenshot or mockup without detailed spec
  - User says "you know what I mean" / "the usual" / "standard"

═══ STEP 1: PARSE — Extract everything from user's description ═══

  Read the FULL message. Extract:
    → SCREEN/COMPONENT name (what are we building?)
    → DATA FIELDS (what information is shown?)
    → USER ACTIONS (what can user do? tap, edit, swipe, submit?)
    → NAVIGATION (where does user come from? where do they go next?)
    → DEPENDENCIES (API endpoints? existing services? shared components?)

═══ STEP 2: CLASSIFY into 3 buckets ═══

  ✅ UNDERSTOOD — clear from user's description, no ambiguity
  ❓ NEEDS CLARIFICATION — mentioned but vague, multiple interpretations
  ⚠️ MISSING — not mentioned but required for a complete implementation

═══ STEP 3: PRESENT structured spec back to user ═══

  FORMAT:
  ┌─────────────────────────────────────────┐
  │ 📋 Spec Analysis — [FeatureName]        │
  ├─────────────────────────────────────────┤
  │                                         │
  │ ✅ UNDERSTOOD:                          │
  │   1. [clear requirement]                │
  │   2. [clear requirement]                │
  │                                         │
  │ ❓ NEEDS CLARIFICATION:                 │
  │   3. "[vague part]" — did you mean:     │
  │      (A) [interpretation 1]             │
  │      (B) [interpretation 2]             │
  │   4. "[missing detail]" — options:      │
  │      (A) [option 1] (recommended)       │
  │      (B) [option 2]                     │
  │                                         │
  │ ⚠️ MISSING (needed for implementation): │
  │   5. [gap 1] — suggest: [default]       │
  │   6. [gap 2] — suggest: [default]       │
  │                                         │
  │ 📐 Suggested structure:                 │
  │   Screen: [Name]Screen.tsx              │
  │   Hook: use[Name].ts                    │
  │   Service: [name]Service.ts (if API)    │
  │   Types: [name].types.ts                │
  │                                         │
  │ Please confirm or adjust.               │
  └─────────────────────────────────────────┘

═══ STEP 4: WAIT for user confirmation ═══

  → User confirms → proceed with Feature Scaffold Protocol
  → User adjusts → update spec → re-present if major changes
  → User adds more → merge into spec → re-classify
  ⛔ NEVER start coding while ❓ items are unresolved
  ✅ If user says "just do it" → use your recommended defaults for ❓ items, but LOG them

═══ STEP 5: USE confirmed spec as completion criteria ═══

  → Each ✅ item = a checklist item for Completion Re-check
  → When ALL items implemented → verify against spec → done
  → If scope changes mid-implementation → update spec → re-confirm

═══ COMMON GAPS TO CHECK (auto-fill checklist) ═══

  Every screen/feature MUST address these (even if user didn't mention):
    □ Loading state — what shows while data loads?
    □ Error state — what shows if API/data fails?
    □ Empty state — what shows when no data exists?
    □ Success state — the normal view
    □ Validation — what are the input rules? (required, format, length)
    □ Navigation — how does user get here? where do they go after?
    □ Permissions — does this need auth? role check?
    □ Offline — does this work without network?
    □ Platform — any iOS vs Android differences?
    □ Accessibility — labels, touch targets, screen reader support

═══ EXAMPLE ═══

  User: "I need a profile page with avatar, name, basic info, editable,
         like other apps"

  AI presents:
    ✅ UNDERSTOOD:
      1. ProfileScreen with user avatar
      2. Display user name
      3. Display basic info fields
      4. User can edit their profile

    ❓ NEEDS CLARIFICATION:
      5. "Basic info" — which fields?
         (A) email, phone, birthday, bio (recommended)
         (B) email, phone only (minimal)
         (C) custom fields — please list
      6. Edit mode — how?
         (A) Edit button → fields become editable inline (recommended)
         (B) Tap "Edit" → navigate to separate EditProfileScreen
      7. Avatar — can user change it?
         (A) Yes — camera + gallery picker (recommended)
         (B) Display only — no change
      8. "Like other apps" — reference app?
         (A) Standard social app profile (Instagram/Facebook style)
         (B) Settings-style list (iOS Settings style)

    ⚠️ MISSING:
      9. API endpoint — does /api/profile exist? GET + PUT?
      10. Avatar upload — max size? format? (suggest: 5MB, jpg/png)
      11. Loading → show skeleton screen
      12. Error → show retry button
      13. Empty → show "Complete your profile" prompt
      14. Logout button — include on profile? (common pattern: yes)

    📐 Suggested structure:
      ProfileScreen.tsx, useProfile.ts, profileService.ts, profile.types.ts

    Please confirm or adjust before I start building.
```
