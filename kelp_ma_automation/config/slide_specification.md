# Slide Specification for M&A Investment Teaser
# This file defines the EXACT structure for all 3 slides
# Template creators: Use these sections as placeholders

## Overview
- Format: 3-slide "Blind" Investment Teaser
- All slides follow brand guidelines (Kelp colors, fonts, footer)
- Content is verified against source one-pager

---

## SLIDE 1: Business Profile & Capabilities

### Fixed Sections (in order):
1. **Company Overview** (1 text box)
   - 2-3 sentence anonymized business description
   - Position: Top center, below title

2. **Products & Services** (bullet list)
   - Max 6 items
   - Source: One-pager "Product & Services" section
   - No truncation - full product names

3. **Industries Served** (bullet list)
   - Max 5 industries
   - Source: One-pager "Application areas / Industries served"

4. **Key Highlights** (bullet list)
   - Max 4 items from Key Operational Indicators
   - Awards, orders, achievements

5. **Certifications & Awards** (bullet list)
   - Max 4 certifications (ISO, AS9100, etc.)
   
6. **Metrics Bar** (bottom bar, 4 metrics)
   - Founded Year
   - Employees Count
   - Headquarters (anonymized)
   - Facility Size (if available)

### Data Required from One-Pager:
- Business Description ✓
- Products & Services ✓
- Industries Served ✓
- Key Operational Indicators ✓
- Certifications ✓
- Founded/Employees/HQ ✓

---

## SLIDE 2: Financial & Operational Performance

### Fixed Sections (in order):
1. **Revenue Chart** (native PPT chart)
   - Type: Clustered column chart
   - Data: Last 5 years revenue in Crores
   - Position: Left half

2. **EBITDA Chart** (native PPT chart)
   - Type: Line or column chart
   - Data: Last 5 years EBITDA in Crores
   - Position: Right of revenue chart

3. **Financial KPIs** (table or bullet list)
   - Revenue (latest FY with value)
   - Revenue CAGR (calculated with formula shown)
   - EBITDA Margin (calculated with formula shown)
   - RoCE (from one-pager)
   - ROE (from one-pager)
   - PAT Margin (if available)

4. **Key Shareholders** (table)
   - Top 5 shareholders with % holding
   - Source: One-pager Shareholders section

5. **Market Position** (if available from web)
   - Industry size
   - Company's market share
   - Key competitors (anonymized)

### Data Required from One-Pager:
- Financials: Revenue by year ✓
- Financials: EBITDA by year ✓
- Financials: RoCE, ROE by year ✓
- Shareholders table ✓

### Data from Web Scraping:
- Industry market size
- Sector growth rate
- Recent news/developments

---

## SLIDE 3: Investment Highlights

### Fixed Sections (in order):
1. **Investment Hooks** (3-4 callout boxes at top)
   - Each hook is a compelling one-liner
   - Based on verified metrics only
   - Examples: "15% Revenue CAGR", "Strong OEM relationships"

2. **Key Strengths** (from SWOT)
   - Max 5 items from SWOT Strengths
   - Full sentences, no truncation

3. **Growth Opportunities** (from SWOT)
   - Max 4 items from SWOT Opportunities
   - Market expansion, new products, etc.

4. **Recent Milestones** (timeline or bullets)
   - Top 4 recent milestones with dates
   - Source: Key Milestones table

5. **Future Plans** (if available)
   - Max 3 growth initiatives

6. **Strategic Partners** (if available)
   - Key partnerships mentioned

### Data Required from One-Pager:
- SWOT Analysis: Strengths ✓
- SWOT Analysis: Opportunities ✓
- Key Milestones ✓
- Future Plans ✓
- Partners ✓

### Data from Web Scraping:
- Recent news/press releases
- Industry outlook
- Competitive positioning

---

## Citation Requirements

Every claim in PPT must have:
1. **Source Type**: 
   - `onepager` - Direct from MD file
   - `calculated` - Derived from one-pager data
   - `web` - From verified web source

2. **Source Reference**:
   - For onepager: Line number and text
   - For calculated: Full Python formula
   - For web: URL and date accessed

3. **Verification Status**:
   - Only verified claims appear in PPT
   - Unverified claims are logged and excluded

---

## Data Availability Matrix

| Data Point | Required | Source | Fallback |
|------------|----------|--------|----------|
| Business Description | Yes | One-pager | Error |
| Products & Services | Yes | One-pager | Generic |
| Revenue (multi-year) | Yes | One-pager | Error |
| EBITDA (multi-year) | Yes | One-pager | Skip chart |
| Shareholders | Yes | One-pager | Skip section |
| SWOT Strengths | Yes | One-pager | Skip section |
| SWOT Opportunities | Yes | One-pager | Skip section |
| Key Milestones | Yes | One-pager | Skip section |
| Market Size | No | Web | Skip section |
| Industry News | No | Web | Skip section |
| Competitor Data | No | Web | Skip section |

---

## Template Placeholder IDs

For template.pptx, use these placeholder names:

### Slide 1:
- `[TITLE_1]` - Slide title
- `[OVERVIEW]` - Company overview paragraph
- `[PRODUCTS_LIST]` - Products bullet list
- `[INDUSTRIES_LIST]` - Industries bullet list
- `[HIGHLIGHTS_LIST]` - Key highlights
- `[CERTS_LIST]` - Certifications
- `[METRICS_BAR]` - Bottom metrics

### Slide 2:
- `[TITLE_2]` - Slide title
- `[REVENUE_CHART]` - Revenue chart area
- `[EBITDA_CHART]` - EBITDA chart area
- `[KPIS_TABLE]` - Financial KPIs
- `[SHAREHOLDERS_TABLE]` - Shareholder table

### Slide 3:
- `[TITLE_3]` - Slide title
- `[HOOKS_BOX_1]` to `[HOOKS_BOX_4]` - Investment hooks
- `[STRENGTHS_LIST]` - Key strengths
- `[OPPORTUNITIES_LIST]` - Growth opportunities
- `[MILESTONES_LIST]` - Recent milestones
- `[PLANS_LIST]` - Future plans
