---
name: israeli-debt-collection-hotzaa-lapoal
description: Guide creditors and debtors through Israeli debt collection and enforcement via the Execution and Collection Authority (Hotza'a LaPo'al / RASHUT HaAchifa VeHaGviya). Use when a user asks how to collect an unpaid debt, enforce a judgment (psak din) or a promissory note (shtar), open an execution file (tik hotza'a lapoal), respond to a collection file opened against them, deal with a garnishment (ikul) on wages or bank accounts, a lien/attachment, a debtor's asset declaration (tatzhir), the "mugbal emtza'im" (limited-means debtor) track, restrictions on a debtor (hagbalot such as passport or license), or the halicha achida (unified) debt-consolidation track. Covers filing, opposition (hitnagdut), interest and linkage, and payment arrangements. Do NOT use for tax debts to the ITA/VAT (separate collection), criminal fines (use israeli-fines-fighter), or the initial lawsuit on the merits (use israeli-small-claims-court for small claims).
license: MIT
compatibility: No network required. Works offline with reference data. Fees, interest rates, and protected-income floors change periodically; verify load-bearing numbers against the primary source.
---

# Israeli Debt Collection (Hotza'a LaPo'al)

## Instructions

### Step 1: Legal & Institutional Framework
Enforcement in Israel runs through the Execution and Collection Authority, governed by:

| Law / Body | Hebrew | Role |
|------------|--------|------|
| Execution Law | חוק ההוצאה לפועל | 5727-1967 | Core statute governing enforcement of debts and judgments |
| Execution and Collection Authority | רשות האכיפה והגבייה | The agency that operates the execution offices (lishkot hotza'a lapoal) |
| Registrar of Execution | רשם ההוצאה לפועל | Quasi-judicial officer who decides motions within an execution file |
| Adjudication of Interest and Linkage Law | חוק פסיקת ריבית והצמדה | 1961 | Governs interest and CPI linkage added to the debt |
| Insolvency and Economic Rehabilitation Law | חוק חדלות פירעון ושיקום כלכלי | 2018 | Governs individual insolvency (replaced the old pshitat regel) |

**What you can enforce through an execution file:**

| Instrument | Hebrew | Notes |
|-----------|--------|-------|
| Court judgment | פסק דין | Money judgment from any Israeli court |
| Promissory note / check / bill | שטר / המחאה / שטר חוב | Enforced directly without a prior lawsuit (execution of a shtar) |
| Conditioned obligation deed | תביעה על סכום קצוב | A "fixed-sum claim" on a written, liquidated debt up to a statutory ceiling, filed directly at the execution office |
| Secured obligation (mortgage/pledge) | משכנתא / משכון | Realization of collateral |

### Step 2: Opening an Execution File (Creditor Side)
Steps for a creditor to open a file (tik):

| Step | Details |
|------|---------|
| 1. Choose the track | Judgment enforcement, execution of a shtar, or a fixed-sum claim (tviah al sechum katzuv) |
| 2. File the request | Online via the Authority portal or at a lishka, with the underlying instrument attached |
| 3. Pay the opening fee | An opening fee applies; it is generally added to the debt and recoverable from the debtor |
| 4. Warning to the debtor | The debtor receives a warning (azhara) and a period (commonly ~20-30 days) to pay or act |
| 5. Enforcement measures | After the warning period, request measures: garnishment (ikul), asset seizure, restrictions |

**Interest and linkage:** the debt accrues CPI linkage (hatzmada) and interest from the judgment/instrument date. The execution file computes the running balance (yitrat chov) including accrued interest, linkage, and fees.

### Step 3: Enforcement Measures the Creditor Can Request

| Measure | Hebrew | Effect |
|---------|--------|--------|
| Third-party garnishment | עיקול צד ג' | Freeze/collect from bank accounts, employers (wages), tenants, or other debtors of the debtor |
| Asset attachment | עיקול מיטלטלין/נכסים | Seize and sell movable property or register a lien on real estate |
| Vehicle immobilization | עיקול/שעבוד רכב | Lien or clamp on a vehicle |
| Restrictions on the debtor | הגבלות | Passport/exit restriction, driving-licence restriction, restricted customer at the bank, block on founding/managing a company |
| Debtor investigation / asset declaration | חקירת יכולת / תצהיר נכסים | Compel the debtor to disclose income and assets under oath |
| Arrest warrant (limited) | צו הבאה | In narrow circumstances for a debtor who evades a payment order |

**Protected income and property (debtor safeguards):** wages and benefits enjoy a protected minimum that cannot be garnished; basic household necessities are exempt from seizure. The protected-income floor is set periodically — verify the current figure.

### Step 4: Responding to a File Opened Against You (Debtor Side)
A debtor who receives a warning has options, and deadlines matter:

| Response | Hebrew | When |
|----------|--------|------|
| Pay in full | תשלום מלא | Closes the file; request a confirmation and file closure |
| Opposition to a shtar / fixed-sum claim | התנגדות | For a shtar or a fixed-sum claim, the debtor can file an opposition within the statutory window (commonly ~30 days of service); this moves the dispute to court |
| Request a payment arrangement | בקשה לצו תשלומים | Ask the Registrar to set affordable monthly instalments based on ability to pay |
| Ability-to-pay hearing | חקירת יכולת | Present income/expenses; the Registrar sets or revises the payment order |
| Limited-means debtor (mugbal emtza'im) | חייב מוגבל באמצעים | A debtor who cannot pay the standard order may be declared limited-means, capping monthly payments but triggering restrictions |
| Unified/consolidated file | תיק איחוד / הליך איחוד | Consolidate multiple execution files into one payment order (halicha achida) |
| Individual insolvency | חדלות פירעון (יחיד) | For deep, unmanageable debt, a court/official-receiver process for a discharge (hefter) |

**Do NOT ignore a warning.** Failing to respond to a shtar or fixed-sum claim within the opposition window generally forfeits the right to contest the debt on the merits, and enforcement proceeds.

### Step 5: Payment Arrangements and the Limited-Means Track

| Concept | Details |
|---------|---------|
| Payment order (tzav tashlumim) | The Registrar fixes a monthly payment matching the debtor's ability, based on the ability-to-pay investigation |
| Standard automatic order | Opening a file can trigger a default monthly order (a fraction of the debt) until the debtor proves a different ability to pay |
| Limited-means declaration | Caps the monthly payment for a debtor genuinely unable to pay the standard order, but imposes restrictions (e.g., exit restriction) and a consolidation of files |
| Missed payments | Falling behind on the order revives full enforcement measures and can escalate restrictions |

### Step 6: Debt Consolidation and Insolvency

| Route | Hebrew | Use |
|-------|--------|-----|
| File consolidation (ichud tikim) | איחוד תיקים | Debtor with several execution files pays one consolidated monthly order across all creditors |
| Individual insolvency (2018 law) | חדלות פירעון ושיקום כלכלי | For a debtor whose total debt is unmanageable; leads to a rehabilitation plan and potentially a discharge of remaining debt |
| Creditor's insolvency petition | בקשת נושה | A creditor above a debt threshold can petition to open insolvency proceedings against the debtor |

The 2018 Insolvency and Economic Rehabilitation Law replaced the former bankruptcy (pshitat regel) regime for individuals; do not cite the old framework.

## Examples

### Example 1: Collecting on a Bounced Check
**Input:** "A client gave me a check for 12,000 NIS that bounced. How do I collect?"
**Output:** A check is a shtar and can be enforced directly at the Execution Office without first suing. Open an execution file for "execution of a shtar," attaching the dishonored check and the bank's return notice. Pay the opening fee (added to the debt). The debtor receives a warning and ~30 days to pay or file an opposition. If no opposition is filed, request enforcement measures: a third-party garnishment on the debtor's bank account or wages, and, if needed, restrictions. The balance accrues interest and CPI linkage from the check's due date.

### Example 2: Wage Garnishment Leaves Nothing to Live On
**Input:** "The execution office is garnishing my whole salary, I can't pay rent."
**Output:** Wages enjoy a protected minimum that cannot be garnished; a garnishment cannot lawfully take the protected floor. File a motion to the Registrar to correct the garnishment to respect the protected-income floor, attaching pay slips and proof of essential expenses (rent, dependents). Simultaneously request an ability-to-pay hearing to set a realistic monthly payment order (tzav tashlumim). If you genuinely cannot meet the standard order, ask to be declared a limited-means debtor (mugbal emtza'im) — this caps payments but imposes restrictions such as an exit ban.

### Example 3: Multiple Collection Files
**Input:** "I have five different execution files from five creditors and can't keep track."
**Output:** Request file consolidation (ichud tikim) so all files merge into a single monthly payment order spread across creditors, based on your ability to pay. This stops competing enforcement actions and gives one predictable payment. Prepare a full income-and-expense picture for the ability-to-pay investigation. If the total debt is genuinely unmanageable even consolidated, consider individual insolvency under the 2018 law, which can lead to a rehabilitation plan and a discharge.

### Example 4: A Fixed-Sum Claim Arrived
**Input:** "I got a 'tviah al sechum katzuv' from a phone company for 3,000 NIS I dispute."
**Output:** A fixed-sum claim (tviah al sechum katzuv) is filed directly at the Execution Office for a liquidated debt. You have a limited window (commonly ~30 days from service) to file an opposition (hitnagdut). Filing the opposition moves the dispute to court where you can contest the debt on the merits. If you miss the window, the claim becomes enforceable and measures follow. Because you dispute the debt, file the opposition promptly with your grounds and evidence, and keep proof of the filing date.

## Bundled Resources

### References
- `references/creditor-playbook.md` -- Step-by-step for a creditor: which track to open (judgment / shtar / fixed-sum), documents needed, the sequence of enforcement measures, and how interest and linkage accrue. Consult when a user wants to collect a debt.
- `references/debtor-defense-guide.md` -- Step-by-step for a debtor: deadlines to file an opposition, how to request a payment order, the limited-means track, file consolidation, protected income, and when insolvency makes sense. Consult when a file is opened against a user.

### Scripts
- `scripts/debt-balance.py` -- Estimates the running balance of a debt with CPI linkage and interest between two dates (illustrative; the official file balance is authoritative). Run: `python scripts/debt-balance.py --help`

## Gotchas

- A shtar (check, promissory note, bill) and a "fixed-sum claim" (tviah al sechum katzuv) can be enforced directly at the Execution Office without a prior lawsuit. Agents sometimes wrongly insist a creditor must first win a court case.
- The debtor's opposition window is short (commonly ~30 days from service) and dispositive. Missing it generally forfeits the right to contest the debt on the merits. Agents that treat the warning as "just a notice" mislead debtors into losing their defense.
- Wages and benefits have a protected minimum that cannot be garnished, and basic household necessities are exempt from seizure. The floor is updated periodically — verify the current figure rather than asserting a fixed number.
- Being declared a limited-means debtor (mugbal emtza'im) lowers payments but is not cost-free: it triggers restrictions such as an exit ban and consolidates the debtor's files. Agents sometimes present it as pure relief.
- Israel replaced individual bankruptcy (pshitat regel) with the 2018 Insolvency and Economic Rehabilitation Law. Do not advise under the old pshitat-regel framework.
- The debt balance is not static: CPI linkage, interest, opening fees, and per-action fees accrue and compound over time. A debtor who ignores a file watches the balance grow well beyond the original principal.
- Tax debts (Income Tax, VAT, National Insurance) are collected through their own statutory mechanisms, not the general Execution Office track. Do not route those here.
- The Registrar of Execution is a quasi-judicial officer, not a full court. Substantive disputes over whether the debt is owed usually belong in court (via an opposition), while collection mechanics stay with the Registrar.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Execution and Collection Authority | https://www.gov.il/he/departments/eca | Open/manage files, fees, forms, debtor and creditor guidance |
| Execution Law text | https://www.nevo.co.il | Chok HaHotza'a LaPo'al, 5727-1967 |
| Kol Zchut: Execution proceedings | https://www.kolzchut.org.il/he/הוצאה_לפועל | Plain-language debtor rights, protected income, payment orders |
| Insolvency and Economic Rehabilitation Law | https://www.gov.il/he/departments/topics/insolvency | Individual insolvency process replacing pshitat regel |

## Recommended MCP Servers

These Model Context Protocol servers, available in the skills-il directory, pair well with this skill:

- **israel-law**: programmatic access to Israeli primary legislation. Use it to pull the current text of the Execution Law, 5727-1967 and the Insolvency and Economic Rehabilitation Law, 2018 when you need to confirm an exact provision such as opposition windows or enforcement measures.
- **kolzchut**: access to Kol Zchut, Israel's plain-language rights portal. Use it to retrieve up-to-date practical guidance on protected income, payment orders, the limited-means track, and file consolidation.
- **boi-exchange**: Bank of Israel data. Use it to confirm current interest and CPI-linkage figures when estimating an accruing debt balance.

Always confirm load-bearing numbers (opening fees, protected-income floor, interest/linkage rates, opposition windows) against the primary source, since amounts and thresholds change.

## Troubleshooting

### Error: "Debtor claims they never received the warning"
Cause: Service (mesira) may have failed, or the address on file is stale.
Solution: Proper service is a precondition to enforcement. A debtor who was not properly served can move the Registrar to set aside measures and reopen the opposition window. A creditor should ensure valid service (personal or substitute service per the rules) and keep the service confirmation, or enforcement can be unwound.

### Error: "Garnishment took protected income"
Cause: A third-party garnishment on wages was applied without respecting the protected-income floor.
Solution: File a motion to the Registrar to correct the garnishment to the lawful protected minimum, attaching pay slips and proof of essential expenses. Overtaken amounts should be released back to the debtor.

### Error: "The creditor won't close the file after full payment"
Cause: Administrative lag or a dispute over residual fees/interest.
Solution: The debtor requests a full-balance printout (yitrat chov) and pays it, then files a motion to close the file (sgirat tik) and lift all restrictions. If the creditor refuses despite full payment, the Registrar can order closure and removal of restrictions.
