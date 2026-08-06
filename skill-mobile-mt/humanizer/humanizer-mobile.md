# Humanizer — Mobile Copy & Text

> Invoke with: @humanizer-mobile
> Use for: app store descriptions, release notes, error messages, onboarding copy, push notifications, UI labels

---

## What this does

Removes AI-generated writing patterns from mobile app text. Makes copy sound like a real person wrote it — not a language model.

**Rule:** Sterile, voiceless writing is just as obvious as slop.

---

## The 24 AI Patterns to Kill

### Content
| Pattern | Example | Fix |
|---------|---------|-----|
| Inflated significance | "This significantly enhances the overall user experience" | "Checkout is now 3 steps instead of 7" |
| Notability inflation | "A powerful, robust, feature-rich solution" | Just describe what it does |
| Promotional language | "Seamlessly integrates with your workflow" | "Connects to Slack and Notion" |
| Superficial -ing analysis | "By leveraging cutting-edge technology..." | State what the tech actually does |

### Language
| Pattern | Example | Fix |
|---------|---------|-----|
| Copula avoidance | "The app, being designed for..." | "The app works for..." |
| Negative parallelism | "Not only fast, but also reliable, and furthermore secure" | Pick the one that matters most |
| Rule of three | "Simple, powerful, and intuitive" | Say which one is actually true |
| Elegant variation | "application... software... platform... tool..." | Pick one word and use it |

### Style
| Pattern | Example | Fix |
|---------|---------|-----|
| Em dash overuse | "Our app — designed for professionals — helps you..." | Rewrite the sentence |
| Unnecessary bold | "This **feature** allows **users** to **manage** their **tasks**" | Bold nothing or bold the one key thing |
| Inline headers mid-paragraph | "**Key features:** The app includes..." | Just write the features |
| Emoji decoration | "🚀 Fast • 💪 Powerful • ✨ Beautiful" | Use 0 or 1 emoji max, never as decoration |

### Communication (chatbot artifacts)
| Pattern | Example | Fix |
|---------|---------|-----|
| "I hope this helps" | Any form of it | Delete |
| "Feel free to..." | "Feel free to reach out" | "Contact us" |
| "Please note that" | "Please note that this feature requires..." | "This feature requires..." |
| Knowledge cutoff disclaimer | "As of my last update..." | Never use in app copy |
| "Delve into" | "Delve into your analytics" | "Check your analytics" |
| "Leverage" | "Leverage our AI" | "Use our AI" |
| "Streamline" | "Streamline your workflow" | Say what actually gets faster |
| "Robust" | "A robust solution" | Say what makes it strong |
| "Seamlessly" | "Seamlessly integrates" | "Works with" or just remove |
| "Intuitive" | "Intuitive interface" | Show don't tell — describe the UX |
| "Comprehensive" | "Comprehensive dashboard" | Say what's in the dashboard |

---

## Mobile-Specific Rewrites

### App Store Description

```
❌ AI:
TaskFlow is a powerful, comprehensive task management application that seamlessly
integrates with your existing workflow. By leveraging cutting-edge AI technology,
it significantly enhances productivity and streamlines your daily operations.

✅ Human:
TaskFlow keeps your team's work in one place. Add tasks, assign them, set
deadlines — everything syncs in real time. Works with Slack, Google Calendar,
and Notion.
```

### Release Notes

```
❌ AI:
Version 2.1.0 introduces significant enhancements to the overall user experience,
including robust improvements to performance and reliability.

✅ Human:
2.1.0
- Faster load times on older Android devices (was 4s, now 1.2s)
- Fixed crash when opening notifications while offline
- Dark mode now remembers your setting between sessions
```

### Error Messages

```
❌ AI:
We apologize for the inconvenience. An unexpected error has occurred while
processing your request. Please try again later.

✅ Human:
Couldn't save your changes — no internet connection.
[Try again] [Save for later]
```

### Onboarding Copy

```
❌ AI:
Welcome to our powerful platform! By leveraging our intuitive interface,
you'll be able to seamlessly manage all your tasks efficiently.

✅ Human:
Where do you want to start?
[Import from Trello] [Start from scratch] [Use a template]
```

### Push Notifications

```
❌ AI:
You have received a new message from a team member regarding an important update.

✅ Human:
Alex commented on "Landing page redesign"
```

### Empty States

```
❌ AI:
No items found. Get started by creating your first item to begin
leveraging the full power of the platform.

✅ Human:
No tasks yet.
[Add your first task]
```

---

## Two-Pass Process

### Pass 1 — Rewrite
1. Find all patterns from the table above
2. Replace each with direct, specific language
3. Remove filler words: "overall", "various", "multiple", "utilize", "leverage"
4. Cut sentence length by 30%

### Pass 2 — Anti-AI Audit
Ask: *"What makes this obviously AI-generated?"*
- Does it make a claim without evidence? → Add a number or cut the claim
- Does it use an adjective where a verb would work? → Use the verb
- Could this describe any app in the category? → Make it specific to THIS app
- Would a person actually say this out loud? → If no, rewrite it

---

## Mobile Copy Principles

```
1. SPECIFIC BEATS VAGUE
   ❌ "significantly faster"
   ✅ "loads in under 1 second"

2. VERBS BEAT ADJECTIVES
   ❌ "intuitive navigation"
   ✅ "swipe left to archive"

3. SHORT SENTENCES FOR MOBILE
   Max 12 words for notifications
   Max 2 sentences for error messages
   Max 3 sentences for onboarding screens

4. SHOW DON'T TELL
   ❌ "powerful search"
   ✅ "search by name, tag, due date, or assignee"

5. USER BENEFIT, NOT FEATURE
   ❌ "real-time sync enabled"
   ✅ "your team sees changes instantly"
```

---

## App Store Character Limits

```
iOS App Store:
  Title:          30 chars  → short, keyword-rich, no taglines
  Subtitle:       30 chars  → 1 benefit, not a repeat of title
  Description:   4000 chars → first 3 lines show before "More", make them count
  Keywords:       100 chars → comma-separated, no spaces, no repeats from title
  What's New:    4000 chars → bullet points, plain language, no marketing

Google Play:
  Title:          30 chars
  Short desc:     80 chars  → shows in search results
  Full desc:     4000 chars
  What's New:    500 chars
```

```
❌ Title: "TaskFlow - Ultimate Productivity & Task Management Solution"
✅ Title: "TaskFlow: Team Tasks & Projects"

❌ Subtitle: "The most powerful way to manage your workflow seamlessly"
✅ Subtitle: "Shared tasks with real-time sync"

❌ What's New: "This update introduces significant improvements to the overall
user experience with enhanced performance and reliability."
✅ What's New:
• Fixed crash on iPhone 14 when swiping between projects
• Dark mode now loads instantly instead of flashing white
• Added swipe-to-complete on task cards
```

---

## Permission Request Copy

```
❌ AI default (iOS):
"[App] Would Like to Access Your Camera"
(No context, user taps Don't Allow)

✅ Custom NSCameraUsageDescription:
"To scan receipts and attach photos to expenses"

❌ "Notifications" permission with no context

✅ Request at the right moment + explain:
"Get notified when teammates comment on your tasks"
[Allow] [Not now]
```

Common permission descriptions:
| Permission | Bad | Good |
|------------|-----|------|
| Camera | "Access camera" | "Scan QR codes to join a workspace" |
| Location | "Use your location" | "Show nearby team members on the map" |
| Contacts | "Access contacts" | "Invite teammates by name instead of email" |
| Notifications | "Send notifications" | "Alert you when your order ships" |
| Microphone | "Access microphone" | "Record voice notes on tasks" |

---

## Rating Prompt Copy

```
❌ AI default:
"Are you enjoying [App Name]? Rate us 5 stars!"

✅ Human — ask a real question first:
"Is [App] helping you get things done?"
[Yes!] [Not really]

If Yes → "Mind leaving a review? It helps us a lot."
         [Sure] [Maybe later]
If No  → "What's getting in the way?"
         [Give feedback]
```

---

## Subscription & Paywall Copy

```
❌ AI:
"Unlock the full potential of our comprehensive premium features
to seamlessly enhance your productivity experience."

✅ Human — state what unlocks:
"Go Pro
• Unlimited projects (free plan: 3)
• Team sharing
• Priority support"
[Start 7-day free trial]
[See what's included]

❌ CTA: "Subscribe Now" / "Upgrade Today" / "Get Premium"
✅ CTA: "Start free trial" / "Unlock [specific feature]" / "Try Pro free"

❌ After trial ends: "Your trial has expired. Please subscribe to continue."
✅ "Your free trial ended. Pick a plan to keep your 12 projects."
```

---

## Word Blacklist (delete on sight)

```
seamlessly / robust / powerful / comprehensive / intuitive / streamline /
leverage / utilize / cutting-edge / state-of-the-art / innovative /
revolutionary / game-changing / transformative / holistic / synergy /
delve / Furthermore / Additionally / Moreover / In conclusion /
It is worth noting / Please note that / Feel free to /
experience the difference / take your [X] to the next level /
designed with you in mind / your one-stop solution
```
