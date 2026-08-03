from pydantic import BaseModel


class ResearchContext(BaseModel):
    intent: str = ""
    business_category: str = ""
    product: str = ""
    product_variants: list[str] = []
    location_city: str = ""
    location_district: str = ""
    location_province: str = ""
    location_country: str = "Indonesia"
    location_raw: str = ""
    target_market: str = ""
    customer_segment: str = ""
    budget: str = ""
    business_goal: str = ""
    explicit_keywords: list[str] = []
    implicit_keywords: list[str] = []
    research_type: str = "comprehensive"
    ai_explanation: str = ""


class ResearchQueries(BaseModel):
    maps_queries: list[str] = []
    search_queries: list[str] = []
    shopping_queries: list[str] = []
    trends_queries: list[str] = []
    tavily_queries: list[str] = []
