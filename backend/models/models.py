from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
import enum


class PlanType(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"


class OpportunityType(str, enum.Enum):
    grant = "grant"
    rfp = "rfp"
    rfq = "rfq"
    rfi = "rfi"
    contract = "contract"


class AlertSeverity(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    organization_name = Column(String)
    organization_type = Column(String)  # nonprofit, contractor, consultant
    focus_areas = Column(Text)  # JSON list of keywords they care about
    states = Column(Text)  # JSON list of states to monitor
    plan = Column(Enum(PlanType), default=PlanType.starter)
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    is_active = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    alerts = relationship("Alert", back_populates="user")
    saved_opportunities = relationship("SavedOpportunity", back_populates="user")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    opportunity_type = Column(Enum(OpportunityType))
    source = Column(String)  # grants.gov, sam.gov, state portal, etc.
    source_url = Column(String)
    agency = Column(String)
    funding_amount = Column(Float)
    funding_amount_max = Column(Float)
    posted_date = Column(DateTime)
    close_date = Column(DateTime)
    eligibility = Column(Text)
    category = Column(String)
    cfda_number = Column(String)
    naics_code = Column(String)
    state = Column(String)
    keywords = Column(Text)  # JSON extracted keywords
    ai_summary = Column(Text)
    ai_relevance_score = Column(Float)
    ai_action_items = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    alerts = relationship("Alert", back_populates="opportunity")
    saved_by = relationship("SavedOpportunity", back_populates="opportunity")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    severity = Column(Enum(AlertSeverity))
    match_reason = Column(Text)
    is_read = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="alerts")
    opportunity = relationship("Opportunity", back_populates="alerts")


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    notes = Column(Text)
    status = Column(String, default="tracking")  # tracking, applying, submitted, won, lost
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # user or assistant
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
