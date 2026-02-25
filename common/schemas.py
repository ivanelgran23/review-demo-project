from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models import ReviewStatus


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ReviewBase(BaseModel):
    product_id: UUID
    text: str = Field(..., min_length=1)
    author: Optional[str] = Field(default=None, max_length=255)


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    text: str


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    text: str
    author: Optional[str]
    status: ReviewStatus
    moderation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    created_at: datetime
    reviews: List[ReviewOut] = []
