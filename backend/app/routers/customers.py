import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.postgres import get_db
from app.middleware.auth_middleware import require_permission
from app.models.postgres_models import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.schemas.user import TokenData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("customers:read")),
) -> List[CustomerResponse]:
    logger.info(f"Fetching customers (skip={skip}, limit={limit}, search={search})")

    query = db.query(Customer)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_filter)) |
            (Customer.email.ilike(search_filter)) |
            (Customer.company.ilike(search_filter))
        )

    customers = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("customers:read")),
) -> CustomerResponse:
    logger.info(f"Fetching customer: {customer_id}")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return CustomerResponse.model_validate(customer)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("customers:write")),
) -> CustomerResponse:
    logger.info(f"Creating customer: {customer_data.email}")

    existing = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists",
        )

    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)

    logger.info(f"Customer created: {customer.id}")
    return CustomerResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("customers:write")),
) -> CustomerResponse:
    logger.info(f"Updating customer: {customer_id}")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    update_data = customer_update.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != customer.email:
        existing = db.query(Customer).filter(
            Customer.email == update_data["email"],
            Customer.id != customer_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists",
            )

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    logger.info(f"Customer updated: {customer_id}")
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("customers:delete")),
) -> None:
    logger.info(f"Deleting customer: {customer_id}")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    db.delete(customer)
    db.commit()

    logger.info(f"Customer deleted: {customer_id}")
