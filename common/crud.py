from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .models import Product, Review, ReviewStatus
from .schemas import ProductCreate, ProductUpdate, ReviewCreate, ReviewUpdate


# Product operations
def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session) -> List[Product]:
    stmt = select(Product).order_by(Product.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_product(db: Session, product_id: UUID) -> Optional[Product]:
    stmt = select(Product).options(joinedload(Product.reviews)).where(
        Product.id == product_id
    )
    return db.execute(stmt).unique().scalar_one_or_none()


def update_product(db: Session, product_id: UUID, payload: ProductUpdate) -> Optional[Product]:
    product = db.get(Product, product_id)
    if not product:
        return None
    product.name = payload.name
    product.description = payload.description
    product.price = payload.price
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: UUID) -> bool:
    product = db.get(Product, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


# Review operations
def create_review(db: Session, payload: ReviewCreate) -> Review:
    review = Review(
        product_id=payload.product_id,
        text=payload.text,
        author=payload.author,
        status=ReviewStatus.pending,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(db: Session, review_id: UUID, payload: ReviewUpdate) -> Optional[Review]:
    review = db.get(Review, review_id)
    if not review:
        return None
    review.text = payload.text
    review.status = ReviewStatus.pending
    db.commit()
    db.refresh(review)
    return review


def list_reviews(
    db: Session,
    product_id: Optional[UUID] = None,
    published_only: bool = False,
) -> List[Review]:
    stmt = select(Review)
    if product_id:
        stmt = stmt.where(Review.product_id == product_id)
    if published_only:
        stmt = stmt.where(Review.status == ReviewStatus.published)
    stmt = stmt.order_by(Review.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_review(db: Session, review_id: UUID) -> Optional[Review]:
    return db.get(Review, review_id)


def set_review_status(
    db: Session, review_id: UUID, status: ReviewStatus, reason: Optional[str] = None
) -> Optional[Review]:
    review = db.get(Review, review_id)
    if not review:
        return None
    review.status = status
    review.moderation_reason = reason
    db.commit()
    db.refresh(review)
    return review
