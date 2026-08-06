# Financial Reporting Templates — Small Operator PM

Templates for Workflow 6: Financial Reporting. Populate each template from user-provided tenant and property data.

---

## Monthly Rent Roll

```
Rent Roll -- [Property Name] -- [Month Year]

| Unit | Type | SF | Tenant | Lease Start | Lease End | Market Rent | Actual Rent | Variance | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1A | 2BR/1BA | 850 | J. Smith | 06/01/25 | 05/31/26 | $1,850 | $1,800 | -$50 | Occupied |
| 1B | 1BR/1BA | 650 | M. Garcia | 09/01/25 | 08/31/26 | $1,700 | $1,650 | -$50 | Occupied |
| 2A | 2BR/1BA | 850 | K. Johnson | 01/01/26 | 12/31/26 | $1,900 | $1,900 | $0 | Occupied |
| 2B | 2BR/2BA | 950 | -- | -- | -- | $2,000 | $0 | -$2,000 | Vacant |

Summary:
  Total units: 4
  Occupied: 3 (75%)
  Vacancy loss: $2,000/month ($24,000 annualized)
  Gross potential rent: $7,450/month
  Actual collected: $5,350/month
  Collection rate vs occupied units: 100%
  Average rent per SF: $2.12/SF
  Average rent vs market: -$33/unit (1.8% below market)
```

---

## Monthly P&L by Property

```
Profit & Loss -- [Property Name] -- [Month Year]

INCOME:
  Rental income (collected)          $5,350
  Late fees collected                $0
  Pet rent                           $75
  Laundry income                     $120
  Parking income                     $0
  Other income                       $0
  TOTAL INCOME                       $5,545

EXPENSES:
  Mortgage (P&I)                     $2,800
  Property taxes                     $450
  Insurance                          $180
  Water/sewer                        $220
  Common area electric               $85
  Trash removal                      $60
  Landscaping                        $150
  Repairs & maintenance              $325
  Property management fee            $0 (self-managed)
  Advertising/marketing              $50
  Legal/professional                 $0
  Accounting/bookkeeping             $0
  Miscellaneous                      $25
  TOTAL EXPENSES                     $4,345

NET OPERATING INCOME (before mortgage): $2,745
NET CASH FLOW (after mortgage):         $1,200

Key metrics:
  Operating expense ratio: 27.9% (expenses ex-mortgage / gross potential rent)
  Debt service coverage ratio: 1.98x (NOI / mortgage payment)
  Cash-on-cash return: [requires equity input]
  Break-even occupancy: 78.4% ([expenses] / [gross potential rent])
```

---

## Annual Tax Summary (Schedule E)

```
Annual Tax Summary -- [Property Name] -- [Tax Year]

SCHEDULE E INPUTS:
  Gross rents received:              $66,540
  Other income (late fees, laundry): $2,340
  Total income:                      $68,880

  Advertising:                       $600
  Auto and travel:                   $480
  Cleaning and maintenance:          $3,900
  Commissions:                       $0
  Insurance:                         $2,160
  Legal and professional:            $350
  Management fees:                   $0
  Mortgage interest:                 $18,400
  Other interest:                    $0
  Repairs:                           $4,200
  Supplies:                          $360
  Property taxes:                    $5,400
  Utilities:                         $4,380
  Depreciation:                      $[per CPA / cost seg study]
  Other:                             $300
  Total expenses:                    $40,530

  Net rental income (loss):          $28,350

  Note: provide this summary to your CPA along with all receipts.
  Track mileage for property visits separately (IRS standard rate applies).
```

---

## Chart of Accounts for Small Landlords

```
4000 - Rental Income
4100 - Late Fee Income
4200 - Pet Rent
4300 - Laundry/Vending Income
4400 - Parking Income
4900 - Other Income
5000 - Mortgage Interest
5100 - Property Taxes
5200 - Insurance
5300 - Utilities (Water, Electric, Gas, Trash)
5400 - Repairs & Maintenance
5500 - Capital Improvements (not expensed -- depreciated)
5600 - Management Fees
5700 - Advertising & Marketing
5800 - Legal & Professional
5900 - Auto & Travel
6000 - Office & Supplies
6100 - Landscaping
6900 - Miscellaneous
```

---

## Capital Reserve Tracker

```
Capital Reserve Fund -- [Property Name]

Target reserve: $[500-1,000 per unit per year]
Current balance: $[amount]
Monthly contribution: $[amount]

  | Date | Description | Deposit | Withdrawal | Balance |
  |---|---|---|---|---|
  | 01/01 | Opening balance | | | $8,000 |
  | 01/15 | Monthly contribution | $400 | | $8,400 |
  | 02/01 | Water heater replacement (Unit 2A) | | $1,200 | $7,200 |
  | 02/15 | Monthly contribution | $400 | | $7,600 |
  | 03/15 | Monthly contribution | $400 | | $8,000 |

Reserve adequacy check:
  Recommended reserve: $500/unit/year * 4 units = $2,000/year (minimum)
  Better target: $1,000/unit/year * 4 units = $4,000/year
  Current annual contribution: $4,800 (adequate)
  Major upcoming expenses:
    - Roof (estimated remaining life: 8 years, replacement cost: $15,000)
    - HVAC (estimated remaining life: 5 years, replacement cost: $6,000/unit)
    - Parking lot reseal (every 3 years, cost: $2,000)
```
