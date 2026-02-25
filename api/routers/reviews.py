from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from common import crud
from api.queue import publish_review_task
from common.schemas import ReviewCreate, ReviewOut, ReviewUpdate
from api.deps import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/publish", response_model=ReviewOut, status_code=201)
def publish_review(payload: ReviewCreate, db=Depends(get_db)):
    product = crud.get_product(db, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    review = crud.create_review(db, payload)
    publish_review_task(str(review.id))
    return review


@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: UUID, payload: ReviewUpdate, db=Depends(get_db)):
    review = crud.update_review(db, review_id, payload)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    publish_review_task(str(review.id))
    return review


@router.get("", response_model=List[ReviewOut])
def list_reviews(
    product_id: Optional[UUID] = None,
    published_only: bool = True,
    db=Depends(get_db),
):
    return crud.list_reviews(db, product_id, published_only=published_only)


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: UUID, db=Depends(get_db)):
    review = crud.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: UUID, db=Depends(get_db)):
    review = crud.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return None


@router.get("/{review_id}/status")
def review_status(review_id: UUID, db=Depends(get_db)):
    review = crud.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": review.status}
