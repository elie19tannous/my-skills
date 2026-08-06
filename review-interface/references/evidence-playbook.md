# Evidence playbook

A useful finding connects a confirmed condition to user impact and a testable outcome. Anything weaker is an observation, preference, or question.

## Candidate lifecycle

Move every candidate through the same sequence:

```text
observe → locate → reproduce → check intent → classify owner → consolidate → rank → report
              ↘ cannot reproduce or insufficient evidence → reject
```

Keep a scratch ledger during review. Do not publish directly from the first pass.

## Write the evidence before the recommendation

Capture:

- exact file and line, screen and state, or interaction sequence;
- current implementation or visible result;
- data, width, input method, theme, and preference settings;
- expected behavior from a project requirement, platform convention, or owning skill rule;
- observed user cost.

If the expected behavior is merely your aesthetic preference, reject the candidate.

## Choose the root cause

Symptoms often share one owner:

| Symptoms | Likely root cause |
| --- | --- |
| Several cards clip long copy | Fixed-height shared card primitive |
| Focus disappears on many controls | Global reset or missing focus token |
| Three dialogs use different button order | No dialog composition contract |
| Dark mode failures repeat across screens | Semantic token mapping, not leaf colors |
| Empty and error states both dead-end | Missing state model for the flow |

Report the cause once and list the confirmed reach. Do not inflate the report with one row per affected file.

## Assign ownership

Use the rule owner, not the most visible symptom:

- Task priority, state communication, layout, color, and interaction craft → interface design.
- React lifecycle, state boundaries, rendering, data flow, and web implementation → React engineering.
- Native platform behavior, list/thread performance, device permissions, and app lifecycle → React Native engineering.
- Authentication, authorization, data exposure, threat controls, and supply chain → security.

Mention secondary effects in `Why`; do not duplicate the finding across reviews.

## Severity decision

Ask in order:

1. Can the user complete the task?
2. Can the user understand the current state and consequence?
3. Can the user recover without losing work?
4. Does the failure repeat through a shared system?
5. Does it affect a supported input method, viewport, appearance, or accessibility need?
6. Is the remaining issue isolated polish?

Use the highest supported impact, not the most alarming label. A theoretical problem with no reachable path is not HIGH.

## Recommendation quality

A recommendation states an observable end condition:

| Weak | Strong |
| --- | --- |
| Improve responsiveness | At 320 CSS pixels, keep the primary action visible and let the field group wrap without horizontal page scroll |
| Fix focus | Restore a visible focus indicator on every toolbar control and verify it is not obscured in the sticky header |
| Use better copy | Name the failed save, preserve the draft, and provide a retry beside the error |
| Make loading nicer | Keep the last successful data visible, mark refresh as busy, and prevent duplicate submission |

Do not prescribe a new dependency, component API, or token name unless evidence makes that implementation choice necessary.

## Rejected candidates

Reject when:

- runtime behavior is required but unavailable;
- the current choice is intentional, coherent, and usable;
- the owning standard permits multiple valid patterns;
- the proposed change would break consistency for a local preference;
- another root finding already owns the symptom;
- the cost exceeds the limited user benefit;
- the issue lies outside the declared scope.

Record the real evidence and reason. “Looked fine” is not a reason.

## Approval integrity

`Approve` means:

- the primary path was exercised;
- high-risk states relevant to the change were inspected;
- no actionable finding survived vetting;
- critical automated checks passed or were not applicable;
- the report names any platform, device, or state outside coverage.

If a critical path is unavailable, the most accurate verdict is `Not verified`, which prevents `Approve` under this skill's contract.
