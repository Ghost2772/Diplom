import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.text import slugify
from app.dependencies.auth import get_current_admin_user
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(tags=["Catalog"])


async def get_unique_slug(
    db: AsyncSession, model, value: str, exclude_id: int | None = None
) -> str:
    max_length = model.__table__.c.slug.type.length
    base_slug = (slugify(value) or uuid.uuid4().hex[:8])[:max_length].rstrip("-")
    slug = base_slug
    suffix = 2

    query = select(model.id)
    if exclude_id is not None:
        query = query.where(model.id != exclude_id)
    while await db.scalar(query.where(model.slug == slug)):
        ending = f"-{suffix}"
        slug = f"{base_slug[: max_length - len(ending)]}{ending}"
        suffix += 1

    return slug


async def commit_product(db: AsyncSession, product: Product) -> Product:
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="Артикул или адрес товара уже занят. Проверьте данные"
        ) from exc
    await db.refresh(product)
    return product


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

    category_slug = await get_unique_slug(
        db,
        Category,
        category_data.slug or category_data.name,
    )

    category = Category(
        name=category_data.name,
        slug=category_slug,
        description=category_data.description,
        image_url=category_data.image_url,
        display_order=category_data.display_order,
        is_active=category_data.is_active,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.display_order, Category.name))
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

    existing_sku = await db.scalar(select(Product.id).where(Product.sku == product_data.sku))
    if existing_sku:
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")

    product_slug = await get_unique_slug(
        db,
        Product,
        product_data.slug or product_data.name,
    )

    product = Product(
        name=product_data.name,
        slug=product_slug,
        sku=product_data.sku,
        brand=product_data.brand,
        short_description=product_data.short_description,
        description=product_data.description,
        image_url=product_data.image_url,
        price=product_data.price,
        old_price=product_data.old_price,
        stock=product_data.stock,
        attributes=product_data.attributes,
        category_id=product_data.category_id,
        is_active=product_data.is_active,
        is_featured=product_data.is_featured,
        is_regulated=product_data.is_regulated,
    )

    db.add(product)
    return await commit_product(db, product)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    product = await db.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if await db.get(Category, product_data.category_id) is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    duplicate = await db.scalar(
        select(Product.id).where(Product.sku == product_data.sku, Product.id != product_id)
    )
    if duplicate is not None:
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")

    fields = product_data.model_dump(exclude={"slug"})
    fields["slug"] = await get_unique_slug(
        db, Product, product_data.slug or product.slug, exclude_id=product_id
    )
    for field, value in fields.items():
        setattr(product, field, value)
    return await commit_product(db, product)


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
