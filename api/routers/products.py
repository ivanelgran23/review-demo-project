from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from common import crud
from common.models import ReviewStatus
from common.schemas import ProductCreate, ProductOut, ProductUpdate
from api.deps import get_db

router = APIRouter(prefix="/products", tags=["products"])


def _serialize_product(product, include_unpublished: bool = False) -> ProductOut:
    reviews = product.reviews
    if not include_unpublished:
        reviews = [r for r in reviews if r.status == ReviewStatus.published]
    return ProductOut(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        created_at=product.created_at,
        reviews=reviews,
    )


@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db=Depends(get_db)):
    product = crud.create_product(db, payload)
    return _serialize_product(product)


@router.get("", response_model=List[ProductOut])
def list_products(db=Depends(get_db)):
    products = crud.list_products(db)
    return [_serialize_product(p) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: UUID, include_unpublished: bool = Query(False), db=Depends(get_db)
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize_product(product, include_unpublished=include_unpublished)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: UUID, payload: ProductUpdate, db=Depends(get_db)):
    product = crud.update_product(db, product_id, payload)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize_product(product)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID, db=Depends(get_db)):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
