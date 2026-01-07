import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.postgres import get_db
from app.middleware.auth_middleware import require_permission
from app.models.postgres_models import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.user import TokenData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    is_service: bool = Query(None),
    is_active: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("products:read")),
) -> List[ProductResponse]:
    logger.info(f"Fetching products (skip={skip}, limit={limit})")

    query = db.query(Product)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) |
            (Product.description.ilike(search_filter)) |
            (Product.sku.ilike(search_filter))
        )

    if is_service is not None:
        query = query.filter(Product.is_service == is_service)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("products:read")),
) -> ProductResponse:
    logger.info(f"Fetching product: {product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("products:write")),
) -> ProductResponse:
    logger.info(f"Creating product: {product_data.name}")

    if product_data.sku:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists",
            )

    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    logger.info(f"Product created: {product.id}")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("products:write")),
) -> ProductResponse:
    logger.info(f"Updating product: {product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_update.model_dump(exclude_unset=True)

    if "sku" in update_data and update_data["sku"] and update_data["sku"] != product.sku:
        existing = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    logger.info(f"Product updated: {product_id}")
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("products:delete")),
) -> None:
    logger.info(f"Deleting product: {product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()

    logger.info(f"Product deleted: {product_id}")
