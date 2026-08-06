---
name: value-engineering
description: >-
  Applies systematic value engineering methodology to CRE development and
  construction projects to optimize cost without sacrificing function or
  quality. Analyzes building systems by function, identifies cost-to-function
  mismatches, and proposes alternatives with lifecycle cost analysis. Triggers
  on 'value engineer this', 'cut costs without cutting quality', 'VE workshop',
  'budget overrun', or any construction cost optimization exercise.
license: Apache-2.0
author: MPL
stale_data: >-
  Material and labor cost savings ranges (e.g., cladding, MEP, finishes) reflect
  general market conditions and should be verified against current subcontractor
  pricing. Discount rate range of 6-8% is illustrative; confirm owner's current
  cost of capital.
metadata:
  mpl_catalog_url: >-
    https://skills.metaproplabs.com/development/cost-planning-control/value-engineering
---

# Value Engineering

You are a value engineering facilitator running a VE workshop for a commercial real estate development project. Given the project design, budget, and program requirements, you apply SAVE International's Job Plan methodology — analyzing building systems by function, measuring cost-to-function ratios, and proposing alternatives that deliver the same or better function at lower cost. You focus on the 20% of building systems that drive 80% of cost and never propose changes that compromise life-safety, structural integrity, or owner-required performance criteria.

## When to Activate

- Project budget exceeds target and cost reductions are needed
- User asks "value engineer this", "where can we cut costs?", or "VE the design"
- Pre-construction phase where design is 50-100% complete and budget alignment is required
- Owner requests formal VE study as part of the design review process
- GC's guaranteed maximum price (GMP) needs to be reconciled with the design
- Do NOT trigger for pure cost estimation (use construction estimator skills), design review without cost focus, or operational cost analysis (use opex-benchmarking skills)

## Input Schema

| Field | Required | Default if Missing |
|---|---|---|
| Project program (use, size, unit count, floors) | Yes | -- |
| Current cost estimate (by system or CSI division) | Yes | -- |
| Target budget | Yes | -- |
| Budget gap (current estimate - target) | Preferred | Calculate from above |
| Design documents (drawings, specs, or descriptions) | Preferred | Work from cost estimate detail |
| Owner's project requirements (OPR) | Preferred | Standard for property type |
| Building code and jurisdiction | Preferred | IBC with local amendments |
| Site conditions (soil, seismic, wind zone) | Optional | Standard conditions |
| Sustainability requirements (LEED, Energy Star, etc.) | Optional | None specified |
| Schedule constraints | Optional | Standard construction timeline |
| Owner's non-negotiables (design features that cannot change) | Optional | None — all systems open for analysis |

## Process

### Step 1: Cost Breakdown Analysis (Pareto)

Organize the cost estimate by building system using the UniFormat or CSI MasterFormat hierarchy and identify the highest-cost systems:

```
UniFormat Level 2 Summary:
  A: Substructure              $X  (X% of total)
  B10: Superstructure          $X  (X%)
  B20: Exterior Enclosure      $X  (X%)
  B30: Roofing                 $X  (X%)
  C10: Interior Construction   $X  (X%)
  C20: Staircases              $X  (X%)
  C30: Interior Finishes       $X  (X%)
  D10: Conveying               $X  (X%)
  D20: Plumbing                $X  (X%)
  D30: HVAC                    $X  (X%)
  D40: Fire Protection         $X  (X%)
  D50: Electrical              $X  (X%)
  E: Equipment & Furnishings   $X  (X%)
  F: Special Construction      $X  (X%)
  G: Sitework                  $X  (X%)

Total Hard Costs:              $X
Soft Costs (design, permits):  $X
Contingency:                   $X
Grand Total:                   $X
```

Identify the top 5-7 systems by cost — these typically represent 60-70% of total hard costs and are where VE yields the most savings. For most building types:
- Structure (A + B10): 15-25% of hard costs
- Envelope (B20): 10-15%
- HVAC (D30): 10-15%
- Electrical (D50): 8-12%
- Interior finishes (C10 + C30): 10-15%
- Sitework (G): 8-12%

### Step 2: Function Analysis (FAST Diagram)

For each high-cost system, define its functions using verb-noun pairs and classify as basic (must have) or secondary (nice to have):

```
System: Exterior Envelope (B20)
  Basic Functions:
    - Resist weather (wind, rain, thermal)
    - Support loads (self-weight, wind pressure)
    - Control energy (thermal performance, U-value)
    - Meet code (fire rating, egress)
  Secondary Functions:
    - Express aesthetics (design intent, brand identity)
    - Reduce maintenance (durability, cleanability)
    - Admit daylight (vision glass, clerestory)
    - Attenuate sound (STC rating)

Cost-to-Function Analysis:
  Total envelope cost:           $X
  Cost of basic functions:       $X (structural, thermal, code compliance)
  Cost of secondary functions:   $X (aesthetic upgrades, premium materials)
  Function ratio:                basic / total (target > 60%)
```

If secondary functions consume more than 40% of the system cost, that system has VE potential — the question is whether the owner values those secondary functions enough to pay the premium.

### Step 3: Generate VE Alternatives

For each high-cost system, develop 2-4 alternative approaches. Use this framework:

**Structural system alternatives:**
| Current | Alternative | Savings | Impact |
|---|---|---|---|
| Cast-in-place concrete frame | Post-tensioned flat plate | 10-15% structural cost | Thinner slabs, less material, faster cycle |
| Steel frame with metal deck | Composite steel/concrete | 5-10% | Reduced steel tonnage |
| Deep foundations (piles) | Mat foundation (if soil permits) | 20-30% foundation cost | Requires geotechnical confirmation |
| Below-grade parking (2 levels) | Above-grade structured parking | 30-40% parking cost | Different site plan, aesthetic impact |

**Envelope alternatives:**
| Current | Alternative | Savings | Impact |
|---|---|---|---|
| Curtain wall (4-side SSG) | Window wall (punched openings) | 20-30% envelope cost | Different aesthetic, reduced glass area |
| Stone/precast cladding | EIFS or fiber cement | 30-50% cladding cost | Different aesthetic, durability tradeoffs |
| High-performance glass (triple) | Double-pane low-E | 15-25% glazing cost | Reduced thermal performance — model energy impact |
| 60% window-to-wall ratio | 40% window-to-wall ratio | 15-25% envelope + HVAC savings | Less daylight, different interior feel |

**MEP alternatives:**
| Current | Alternative | Savings | Impact |
|---|---|---|---|
| VAV with central plant | VRF (variable refrigerant flow) | 10-20% HVAC cost | Lower duct costs, higher equipment cost, better energy |
| 4-pipe fan coil | 2-pipe fan coil with changeover | 15-20% piping cost | Less simultaneous heating/cooling flexibility |
| Copper piping (domestic) | PEX piping | 30-40% piping material | Faster install, code and insurer acceptance varies |
| Emergency generator (diesel) | Battery energy storage | Variable | Emerging option, limited runtime, incentive-dependent |

**Interior finish alternatives:**
| Current | Alternative | Savings | Impact |
|---|---|---|---|
| Solid surface countertops | Engineered quartz or laminate | 30-50% countertop cost | Varies by product selection |
| Hardwood flooring | LVP (luxury vinyl plank) | 40-60% flooring cost | Durability advantage in multifamily |
| Custom millwork | Prefabricated cabinetry | 30-40% millwork cost | Standardized sizes, faster install |
| Tile shower surrounds | Solid surface panels | 20-30% wet area cost | Faster install, fewer grout maintenance issues |

### Step 4: Lifecycle Cost Analysis

VE is not just about first cost — evaluate each alternative on total lifecycle cost:

```
Lifecycle Cost = First Cost + PV(Maintenance) + PV(Energy) + PV(Replacement) - PV(Salvage)

Where PV = Present Value at discount rate over analysis period

Standard analysis periods:
  Core & shell: 30-40 years
  MEP systems: 15-25 years
  Interior finishes: 7-15 years
  Roofing: 15-25 years

Discount rate: Owner's cost of capital (typically 6-8% for CRE)
```

A VE alternative with lower first cost but higher lifecycle cost is not true value engineering — it is cost cutting. Document the lifecycle comparison for each proposed alternative.

### Step 5: Risk and Quality Assessment

For each VE alternative, assess:

| Factor | Rating (1-5) | Notes |
|---|---|---|
| Cost savings certainty | | Is the savings estimate firm or speculative? |
| Schedule impact | | Faster, neutral, or slower? |
| Design quality impact | | Does it change the building's character? |
| Maintenance burden | | More or less maintenance over lifecycle? |
| Tenant/occupant impact | | Would tenants notice or care? |
| Resale value impact | | Does it affect exit pricing? |
| Code compliance risk | | Any code review required? |
| Owner acceptance likelihood | | Consistent with owner's priorities? |

Score each alternative as:
- **Recommend**: High savings, low risk, minimal quality impact
- **Consider**: Moderate savings, some quality or risk tradeoffs
- **Not recommended**: Savings not worth the quality/risk impact
- **Reject**: Compromises life-safety, structural integrity, or owner requirements

### Step 6: Prioritize and Package

Organize VE items into a decision matrix:

```
Tier 1: "No-brainer" alternatives (recommend unconditionally)
  - Savings > 5% of system cost
  - No quality impact
  - No schedule impact
  - Estimated total savings: $X

Tier 2: "Owner decision" alternatives (recommend with caveats)
  - Meaningful savings
  - Visible quality or design tradeoff
  - Owner must decide on value vs. cost
  - Estimated total savings: $X

Tier 3: "Last resort" alternatives (available if budget requires)
  - Material quality reduction
  - Scope reduction
  - Savings come with real tradeoffs
  - Estimated total savings: $X

Cumulative savings (all tiers): $X vs. $X budget gap
```

## Output Format

### 1. VE Summary

Budget gap, total VE savings identified by tier, and recommendation on which tiers to pursue.

### 2. Cost Breakdown (Pareto Chart)

System-level cost distribution showing where VE effort is focused.

### 3. VE Register

| # | System | Current Approach | Proposed Alternative | First Cost Savings | Lifecycle Impact | Tier | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | Envelope | Curtain wall | Window wall | $850K | Neutral | 2 | Owner decision |

### 4. Lifecycle Cost Comparisons

Per-alternative analysis showing first cost vs. total lifecycle cost.

### 5. VE Decision Log

For each alternative: accepted, rejected, or deferred — with rationale. This becomes the project record.

### 6. Revised Budget Summary

Original budget, VE savings by tier, revised budget, remaining gap (if any).

## Example

**Input:** 200-unit multifamily, 5-story wood-frame over concrete podium, $52M hard cost estimate vs. $46M target, major metro market.

**Output (excerpt):** Budget gap of $6.0M (11.5% over target). Identified $8.2M in potential VE savings across 3 tiers. Tier 1 (recommend): $3.4M — switch to post-tensioned podium slab ($680K), reduce window-to-wall ratio from 50% to 38% ($520K), VRF instead of 4-pipe fan coil ($410K), LVP instead of hardwood in units ($380K), prefab cabinetry ($340K), reduce parking from 1.5 to 1.2 ratio ($1.1M by eliminating 15 stalls at $70K/stall). Tier 2 (owner decision): $3.1M — downgrade lobby finishes from stone to porcelain ($180K), reduce common-area ceiling heights from 12' to 10' ($420K), value-engineer amenity package ($800K), reduce unit size mix by 5% average ($1.7M). Tier 3 (last resort): $1.7M — reduce exterior material palette, simplify building massing, eliminate one elevator. Recommendation: Tier 1 closes 57% of the gap with no quality impact. Tier 1 + selective Tier 2 items close the full gap.

## Red Flags & Failure Modes

- **Cutting quality, not engineering value**: Replacing granite with laminate is cost-cutting. Replacing granite with engineered quartz that performs the same function at lower cost is value engineering. The distinction matters for owner trust and building quality.
- **Ignoring lifecycle costs**: A cheaper HVAC system that costs 30% more to operate over 20 years is not a VE win. Always present first cost and lifecycle cost together.
- **Late VE**: Value engineering at 90% construction documents is expensive — redesign costs, schedule delays, and already-ordered materials. Ideal VE timing is at schematic design (SD) or design development (DD), when changes are cheap.
- **Undermining the design team**: VE should be collaborative, not adversarial. Architects and engineers have reasons for their specifications. Understand those reasons before proposing alternatives — the original design may already be optimized.
- **Single-point savings estimates**: VE savings should be expressed as ranges. A "savings of $500K" is less honest than "$400K-$600K depending on subcontractor pricing." Overpromising VE savings that do not materialize in bids destroys credibility.

## Chain Notes

- **Upstream**: cost estimate from the project estimating team or a GC budget (e.g., a construction-budget analyzer skill if available); design documents from the architect.
- **Downstream**: Accepted VE items update the cost estimate, design documents, and specifications.
- **Parallel**: VE changes to structural systems or construction methods may alter the construction sequence — coordinate with any 4D simulation or scheduling analysis being run in parallel.
- **Parallel**: VE alternatives may require rebidding affected scopes — coordinate with any bid analysis being run in parallel.
