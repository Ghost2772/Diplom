from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(tags=["Catalog"])


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    result = await db.execute(select(Category).where(Category.name == category_data.name))
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(status_code=400, detail="Категория уже существует")

    category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return categories


@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    result = await db.execute(select(Category).where(Category.id == product_data.category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category_id=product_data.category_id,
        is_active=product_data.is_active
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product


@router.get("/products", response_model=list[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(default=None, description="Поиск по названию товара"),
    category_id: int | None = Query(default=None, description="Фильтр по категории"),
    min_price: float | None = Query(default=None, ge=0, description="Минимальная цена"),
    max_price: float | None = Query(default=None, ge=0, description="Максимальная цена"),
    is_active: bool | None = Query(default=None, description="Фильтр по активности товара"),
):
    query = select(Product)

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    result = await db.execute(query)
    products = result.scalars().all()
    return products


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return product