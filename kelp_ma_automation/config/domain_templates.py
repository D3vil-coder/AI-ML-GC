"""
Domain Templates - 8 Industry-Specific Slide Structures
Clean aesthetics with KPI spotlights, shareholder pie charts, and no redundancy.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class SlideSection:
    """A slide section with name and display settings."""
    name: str
    display_name: str
    max_items: int = 8
    is_kpi: bool = False  # Show as spotlight box
    is_chart: bool = False  # Show as pie/bar chart
    required: bool = True


@dataclass
class SlideTemplate:
    """Template for a single slide."""
    title: str
    sections: List[SlideSection]
    image_position: str = "none"  # "top", "left", "right", "none"
    layout: str = "columns"  # "columns", "grid", "full"


@dataclass
class DomainTemplate:
    """Complete template for a domain."""
    domain_name: str
    domain_key: str
    slides: List[SlideTemplate]
    image_folder: str
    primary_kpis: List[str]
    secondary_kpis: List[str]


# ==============================================================================
# DOMAIN TEMPLATES
# ==============================================================================

MANUFACTURING_TEMPLATE = DomainTemplate(
    domain_name="Manufacturing & Industrials",
    domain_key="manufacturing",
    slides=[
        SlideTemplate(
            title="Infrastructure & Capabilities",
            sections=[
                SlideSection("products", "Product Portfolio", max_items=8),
                SlideSection("industries", "Industries Served", max_items=6),
                SlideSection("certifications", "Certifications", max_items=5),
                SlideSection("facilities", "Manufacturing Footprint", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Financial Performance",
            sections=[
                SlideSection("revenue_chart", "Revenue & EBITDA Trend", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_roce", "ROCE", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),  # Pie chart
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Highlights",
            sections=[
                SlideSection("hooks", "Key Investment Thesis", max_items=3),
                SlideSection("strengths", "Strategic Moats", max_items=4),
                SlideSection("opportunities", "Growth Drivers", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="manufacturing",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "ROCE"],
    secondary_kpis=["Export Contribution", "Capacity Utilization", "Customer Count"]
)

TECHNOLOGY_TEMPLATE = DomainTemplate(
    domain_name="Technology & IT Services",
    domain_key="technology",
    slides=[
        SlideTemplate(
            title="Technology Stack & Market Presence",
            sections=[
                SlideSection("products", "Service Offerings", max_items=8),
                SlideSection("industries", "Industry Verticals", max_items=6),
                SlideSection("team", "Team Composition", max_items=4),
                SlideSection("partnerships", "Strategic Partnerships", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Growth & Profitability",
            sections=[
                SlideSection("revenue_chart", "Revenue Growth", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_employees", "Employee Count", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Highlights",
            sections=[
                SlideSection("hooks", "Scalability Thesis", max_items=3),
                SlideSection("strengths", "Competitive Advantages", max_items=4),
                SlideSection("opportunities", "Market Opportunity", max_items=4),
                SlideSection("milestones", "Key Achievements", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="technology",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "Employee Count"],
    secondary_kpis=["Revenue per Employee", "Client Retention", "Repeat Rate"]
)

LOGISTICS_TEMPLATE = DomainTemplate(
    domain_name="Logistics & Supply Chain",
    domain_key="logistics",
    slides=[
        SlideTemplate(
            title="Network & Infrastructure",
            sections=[
                SlideSection("products", "Service Portfolio", max_items=8),
                SlideSection("network", "Network Coverage", max_items=4),
                SlideSection("fleet", "Fleet & Assets", max_items=4),
                SlideSection("technology", "Technology Platform", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Operational & Financial Metrics",
            sections=[
                SlideSection("revenue_chart", "Revenue Trend", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_shipments", "Annual Shipments", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Case",
            sections=[
                SlideSection("hooks", "Key Investment Thesis", max_items=3),
                SlideSection("strengths", "Operational Excellence", max_items=4),
                SlideSection("opportunities", "Growth Vectors", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="logistics",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "Fleet Size"],
    secondary_kpis=["Warehouse Sq Ft", "Pin Codes Served", "On-Time Delivery"]
)

CONSUMER_TEMPLATE = DomainTemplate(
    domain_name="Consumer Brands / D2C",
    domain_key="consumer",
    slides=[
        SlideTemplate(
            title="Brand & Product Portfolio",
            sections=[
                SlideSection("products", "Product Categories", max_items=8),
                SlideSection("channels", "Channel Presence", max_items=4),
                SlideSection("certifications", "Certifications", max_items=4),
                SlideSection("demographic", "Target Demographics", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Growth & Unit Economics",
            sections=[
                SlideSection("revenue_chart", "Revenue Growth", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_gross_margin", "Gross Margin", is_kpi=True),
                SlideSection("kpi_repeat_rate", "Repeat Purchase Rate", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Brand Equity & Investment Case",
            sections=[
                SlideSection("hooks", "Market Position", max_items=3),
                SlideSection("strengths", "Brand Strengths", max_items=4),
                SlideSection("opportunities", "Growth Opportunity", max_items=4),
                SlideSection("milestones", "Key Achievements", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="consumer",
    primary_kpis=["Revenue CAGR", "Gross Margin", "Repeat Rate"],
    secondary_kpis=["CAC", "LTV", "Average Order Value"]
)

HEALTHCARE_TEMPLATE = DomainTemplate(
    domain_name="Healthcare & Pharma",
    domain_key="healthcare",
    slides=[
        SlideTemplate(
            title="Product Portfolio & Capabilities",
            sections=[
                SlideSection("products", "Therapeutic Areas", max_items=8),
                SlideSection("manufacturing", "Manufacturing Infrastructure", max_items=4),
                SlideSection("certifications", "Regulatory Approvals", max_items=6),
                SlideSection("distribution", "Distribution Network", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Financials & Market Position",
            sections=[
                SlideSection("revenue_chart", "Revenue & R&D Trend", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_rd_spend", "R&D Spend %", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Highlights",
            sections=[
                SlideSection("hooks", "Regulatory Moat", max_items=3),
                SlideSection("strengths", "Competitive Advantages", max_items=4),
                SlideSection("opportunities", "Growth Drivers", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="healthcare",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "R&D Spend %"],
    secondary_kpis=["ANDA Filings", "Export %", "Product Pipeline"]
)

INFRASTRUCTURE_TEMPLATE = DomainTemplate(
    domain_name="Infrastructure & Real Estate",
    domain_key="infrastructure",
    slides=[
        SlideTemplate(
            title="Project Portfolio & Execution",
            sections=[
                SlideSection("projects", "Project Types", max_items=8),
                SlideSection("geographies", "Geographic Presence", max_items=4),
                SlideSection("clients", "Client Segments", max_items=4),
                SlideSection("capabilities", "Execution Capabilities", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Financials & Order Book",
            sections=[
                SlideSection("revenue_chart", "Revenue & Order Book", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_order_book", "Order Book", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Case",
            sections=[
                SlideSection("hooks", "Execution Track Record", max_items=3),
                SlideSection("strengths", "Strategic Advantages", max_items=4),
                SlideSection("opportunities", "Growth Pipeline", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="infrastructure",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "Order Book"],
    secondary_kpis=["Execution Timeline", "Debt/Equity", "Project Pipeline"]
)

CHEMICALS_TEMPLATE = DomainTemplate(
    domain_name="Chemicals & Specialty Materials",
    domain_key="chemicals",
    slides=[
        SlideTemplate(
            title="Product Portfolio & Applications",
            sections=[
                SlideSection("products", "Product Segments", max_items=8),
                SlideSection("industries", "End-User Industries", max_items=6),
                SlideSection("certifications", "Quality Certifications", max_items=4),
                SlideSection("facilities", "Manufacturing Facilities", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Financial Performance",
            sections=[
                SlideSection("revenue_chart", "Revenue by Segment", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_capacity", "Capacity Utilization", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Thesis",
            sections=[
                SlideSection("hooks", "Product Differentiation", max_items=3),
                SlideSection("strengths", "Entry Barriers", max_items=4),
                SlideSection("opportunities", "Growth Catalysts", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="chemicals",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "Export Contribution"],
    secondary_kpis=["Customer Concentration", "Capacity Utilization", "R&D Investment"]
)

AUTOMOTIVE_TEMPLATE = DomainTemplate(
    domain_name="Automotive & Components",
    domain_key="automotive",
    slides=[
        SlideTemplate(
            title="Product Range & Customer Base",
            sections=[
                SlideSection("products", "Product Categories", max_items=8),
                SlideSection("oems", "OEM Relationships", max_items=6),
                SlideSection("aftermarket", "Aftermarket Presence", max_items=4),
                SlideSection("certifications", "Quality Standards", max_items=4),
            ],
            image_position="top",
            layout="columns"
        ),
        SlideTemplate(
            title="Operational & Financial Metrics",
            sections=[
                SlideSection("revenue_chart", "Revenue & Volume Growth", is_chart=True),
                SlideSection("kpi_revenue_cagr", "Revenue CAGR", is_kpi=True),
                SlideSection("kpi_ebitda_margin", "EBITDA Margin", is_kpi=True),
                SlideSection("kpi_capacity", "Capacity Utilization", is_kpi=True),
                SlideSection("shareholders", "Key Shareholders", is_chart=True),
            ],
            image_position="none",
            layout="grid"
        ),
        SlideTemplate(
            title="Investment Case",
            sections=[
                SlideSection("hooks", "OEM Relationships", max_items=3),
                SlideSection("strengths", "Technological Capabilities", max_items=4),
                SlideSection("opportunities", "EV Opportunity", max_items=4),
                SlideSection("milestones", "Key Milestones", max_items=4),
            ],
            image_position="right",
            layout="columns"
        )
    ],
    image_folder="automotive",
    primary_kpis=["Revenue CAGR", "EBITDA Margin", "EV Order Book"],
    secondary_kpis=["Customer Mix", "Export %", "Capacity Utilization"]
)


# ==============================================================================
# TEMPLATE REGISTRY
# ==============================================================================

DOMAIN_TEMPLATES = {
    "manufacturing": MANUFACTURING_TEMPLATE,
    "technology": TECHNOLOGY_TEMPLATE,
    "logistics": LOGISTICS_TEMPLATE,
    "consumer": CONSUMER_TEMPLATE,
    "healthcare": HEALTHCARE_TEMPLATE,
    "infrastructure": INFRASTRUCTURE_TEMPLATE,
    "chemicals": CHEMICALS_TEMPLATE,
    "automotive": AUTOMOTIVE_TEMPLATE,
}


def get_domain_template(domain: str) -> DomainTemplate:
    """Get template for a domain (case-insensitive, partial match)."""
    domain_lower = domain.lower()
    
    # Direct match
    if domain_lower in DOMAIN_TEMPLATES:
        return DOMAIN_TEMPLATES[domain_lower]
    
    # Partial match
    for key, template in DOMAIN_TEMPLATES.items():
        if key in domain_lower or domain_lower in key:
            return template
        if key in template.domain_name.lower():
            return template
    
    # Default to manufacturing
    return MANUFACTURING_TEMPLATE


def list_domains() -> List[str]:
    """List all available domain names."""
    return [t.domain_name for t in DOMAIN_TEMPLATES.values()]


if __name__ == "__main__":
    # Test template lookup
    print("Available domains:")
    for i, domain in enumerate(list_domains(), 1):
        print(f"  {i}. {domain}")
    
    print("\nTemplate lookup tests:")
    for test in ["technology", "IT Services", "pharma", "logistics", "d2c", "automotive"]:
        template = get_domain_template(test)
        print(f"  '{test}' -> {template.domain_name}")
