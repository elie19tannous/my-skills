# Document Analysis — Extract Requirements from Any File

> Parse design files, specs, and documents into actionable mobile implementation tasks.

## Supported Formats

| Format | How to Read | Use Case |
|--------|------------|----------|
| **Images** (PNG, JPG, WebP) | Read tool (multimodal) | UI mockups, wireframes, screenshots |
| **PDF** | Read tool (pages param, max 20/request) | PRD, API docs, design specs |
| **DOCX** | Convert to text first | Requirements, user stories |
| **XML** | Read tool directly | Android layouts, config, API response |
| **JSON** | Read tool directly | API contracts, config, mock data |
| **YAML** | Read tool directly | CI/CD config, OpenAPI specs |
| **Figma** | URL → WebFetch | Design tokens, component specs |

## Analysis Protocol

### Step 1: Identify Document Type

```
DOCUMENT TYPE:
  Image (mockup/wireframe)  → UI Analysis Protocol
  PDF/DOCX (requirements)   → Requirements Extraction Protocol
  XML/JSON (API contract)   → Data Model Protocol
  Figma URL                 → Design Token Protocol
```

### Step 2: Extract by Type

#### UI Analysis (Images)

```
FROM IMAGE, EXTRACT:
  1. LAYOUT
     - Screen structure (header, body, footer, tabs)
     - Component hierarchy (parent → child)
     - Spacing pattern (uniform? 8px grid? 16px?)

  2. COMPONENTS
     - List all visible UI elements
     - Map to framework components:
       Button, TextInput, FlatList, Image, Card, Modal, etc.
     - Note interactive elements (tap, swipe, scroll)

  3. STYLING
     - Colors (primary, secondary, background, text)
     - Typography (heading size, body size, font weight)
     - Border radius, shadows, elevation
     - Dark mode indicators (if visible)

  4. STATES (infer from design)
     - Loading: where to show skeleton/shimmer?
     - Empty: what if list has no items?
     - Error: where to show error message?

OUTPUT → Component tree + style constants + state handling plan
```

#### Requirements Extraction (PDF/DOCX)

```
FROM DOCUMENT, EXTRACT:
  1. USER STORIES
     - "As a [user], I want [action], so that [benefit]"
     - Priority: must-have / nice-to-have
     - Acceptance criteria

  2. SCREENS / FLOWS
     - List all screens mentioned
     - Map navigation flow (Screen A → Screen B → Screen C)
     - Identify entry points and exit points

  3. DATA REQUIREMENTS
     - What data does each screen need?
     - API endpoints mentioned
     - Data relationships (user has many orders)

  4. BUSINESS RULES
     - Validation rules (email format, password strength)
     - Permission levels (admin, user, guest)
     - Edge cases mentioned

  5. NON-FUNCTIONAL
     - Performance requirements (load time, offline support)
     - Platform requirements (iOS min version, Android min SDK)
     - Accessibility requirements

OUTPUT → Feature list + screen map + data model + API contract
```

#### Data Model Protocol (XML/JSON)

```
FROM API CONTRACT, EXTRACT:
  1. ENDPOINTS
     - Method + URL + description
     - Request params / body
     - Response shape

  2. MODELS / TYPES
     - Generate TypeScript interfaces / Dart classes / Swift structs / Kotlin data classes
     - Include optional fields, enums, nested objects
     - Add serialization annotations if needed

  3. ERROR RESPONSES
     - Error code mapping
     - Error message display strategy

OUTPUT → Type definitions + API service layer + error handling
```

## Document → Code Pipeline

```
STEP 1: READ DOCUMENT
  - Image: Read tool (visual analysis)
  - PDF: Read tool with pages param
  - DOCX/XML/JSON: Read tool directly
  - Large PDF (>20 pages): Read in chunks (pages: "1-20", "21-40", etc.)

STEP 2: EXTRACT REQUIREMENTS
  - Run appropriate extraction protocol above
  - Output structured summary

STEP 3: MAP TO FEATURES
  - Group requirements into features
  - Identify dependencies between features
  - Prioritize: auth → core screens → secondary features

STEP 4: SCAFFOLD
  - Use Feature Scaffold Protocol from SKILL.md
  - Create features in dependency order
  - Wire navigation between screens

STEP 5: VERIFY
  - Cross-check: every requirement has matching code
  - Cross-check: every screen in doc has matching screen file
  - Cross-check: every API endpoint has matching service method
```

## Quick Commands

```
"Read mockup.png and implement this screen"
  → UI Analysis → Component tree → Generate code

"Read requirements.pdf pages 1-10 and list all features"
  → Requirements Extraction → Feature list

"Read api.json and generate all models and services"
  → Data Model Protocol → Types + Services

"Read wireframe.png and create navigation flow"
  → UI Analysis (focus on navigation) → Router setup

"Read spec.docx and estimate feature scope"
  → Requirements Extraction → Feature count + complexity
```

## Tips

- **Large PDFs**: Always specify page range. Read table of contents first (page 1-2) to find relevant sections.
- **Multiple mockups**: Read all screens first, identify shared components, create shared components first.
- **API docs**: Generate types/models first, then services, then UI. Types are the foundation.
- **Incomplete specs**: Flag missing information. Ask user before assuming.
- **Conflicting info**: Document wins over assumption. If doc says X but code says Y, ask user which is correct.
