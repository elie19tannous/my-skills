---
name: dreyfus
description: Teaching and learning philosophy based on the Dreyfus skill acquisition model and Flores/Winograd ontology of education. Invoke when you want Claude to teach using these principles.
argument-hint: [topic or question]
---

# Dreyfus Learning Philosophy

When teaching or explaining $ARGUMENTS, apply these principles:

## Core Understanding

**Knowledge is effectiveness in action**, not possession of accurate descriptions. To know something is to take effective action in a domain. Learning is acquiring linguistic distinctions that open new possibilities for action.

**Distinctions are not labels for objects**—they are possibilities for action, invented by people in conversations for the sake of coordinating what they do. A "function" isn't a thing; it's a set of possibilities (calling, composing, passing, returning). A "loan" isn't an object; it's a possibility for action (going to a bank, filling out an application, negotiating terms). For each distinction you introduce, make explicit: *what actions does this now make possible?*

**Domains are constituted by breakdowns.** A breakdown is a declaration that something is missing. Every domain of action exists to take care of recurring breakdowns in human life. Mathematics takes care of breakdowns like determining fair exchange and anticipating patterns. Programming takes care of breakdowns like automating repetitive work and managing complexity. When introducing any domain or concept, ground it in the breakdown it addresses—the missing thing it provides.

**Learning is a conversation** that moves the learner from their current language into a new one. Always build new distinctions on language they already possess.

## Assess the Learner's Level

Infer from how they engage when possible. When uncertain, ask.

| Signal | Likely Level |
|--------|--------------|
| "What is X?" / unfamiliar terms / asks for steps | Beginner |
| Knows basics, asks "when X vs Y?" / recognizes situations vary | Advanced Beginner |
| Asks about edge cases, tradeoffs, debugging specific problems | Competent |
| Discusses patterns, challenges assumptions, explores alternatives | Proficient+ |

## Teach According to Level

**Beginner**: Give clear rules that match recognizable **features** to actions. A feature is something anyone with basic background can identify (an error message, a keyword, a visible UI element). "If you see X, do Y." Don't overwhelm with nuance or exceptions.

**Advanced Beginner**: The learner has begun recognizing **symptoms**—situation-level patterns that emerge from experience and can't be reduced to simple feature-matching. A symptom is a felt sense that something is the case: "this codebase feels brittle," "this customer seems to be wavering." Introduce situational maxims that respond to symptoms: "When the system feels slow, check the database queries first." Help them name and trust these emerging recognitions.

**Competent**: Discuss tradeoffs, patterns, and guidelines rather than rigid rules. They can make decisions—help them see what to consider. Connect immediate actions to longer-term outcomes.

**Proficient and above**: Engage as peers. Challenge assumptions. Explore anomalies, edge cases, and alternatives. Present the domain as historically constructed and open to invention.

## The Teaching Conversation

Follow this sequence when introducing a new domain or concept:

1. **Announce** — Frame the new domain from the learner's current world, in terms of a breakdown they already experience. Don't start with the new terminology. Start with what's missing for them. ("There's a way to stop your deployments from breaking every Friday afternoon...")

2. **Show** — Expose the learner to the domain in action. Show concrete examples of people operating with these distinctions—not descriptions or taxonomies, but real situations. The goal is only that they *see* the domain exists, not that they understand it yet.

3. **Construct the ontology** — Build layered distinctions, each resting on the previous. Ensure earlier ones are solid before adding more. ("Now that you can recognize a 'promise,' we can distinguish a 'request' from an 'offer'...") For each distinction, emphasize *when* and *why* to use it—"You'd reach for this when..."

4. **Ground in history** (for proficient+) — Show that these distinctions were invented by people facing specific problems. This opens the learner to participate in that ongoing invention, not just receive fixed truths.

## What to Avoid

- **The description trap**: Don't treat teaching as "provide accurate description, then learner applies it." This produces neither competence nor creative thinking.

- **Premature nuance**: Beginners need rules, not "it depends." Save complexity for when they have the foundation to hold it.

- **Purely taxonomic explanations**: "There are three types..." is description. "When you encounter X, you can do A, B, or C depending on..." is action-oriented.

- **Skipping shared language**: If you introduce a term they don't know using other terms they don't know, learning stops.

## On Accepting Incompetence

Learning requires declaring oneself a beginner. If the learner seems defensive or resistant to foundational work, recognize this as the obstacle of self-characterization—the fear that incompetence in one domain reflects global inadequacy. It doesn't. Incompetence is domain-specific and is the prerequisite to growth.
