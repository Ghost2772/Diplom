import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCategories, getProduct } from "../api/productsApi";
import CartToast from "../components/CartToast";
import ProductImage from "../components/ProductImage";
import { useCartAction } from "../hooks/useCartAction";

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

export default function ProductPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const { notice, addingProductId, addProduct, dismissNotice } = useCartAction();

  useEffect(() => {
    let isMounted = true;
    const loadProduct = async () => {
      setLoading(true);
      setError("");
      setNotFound(false);
      setProduct(null);
      setCategory(null);
      window.scrollTo({ top: 0, behavior: "instant" });

      try {
        if (!/^[1-9]\d*$/.test(productId)) {
          if (isMounted) setNotFound(true);
          return;
        }
        const [item, categories] = await Promise.all([
          getProduct(productId),
          getCategories().catch(() => []),
        ]);
        if (!isMounted) return;
        setProduct(item);
        setCategory(
          Array.isArray(categories)
            ? categories.find((entry) => entry.id === item.category_id) || null
            : null,
        );
      } catch (requestError) {
        if (!isMounted) return;
        if (requestError.response?.status === 404) {
          setNotFound(true);
        } else {
          setError("Не удалось загрузить товар. Проверьте подключение и попробуйте ещё раз.");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadProduct();
    return () => { isMounted = false; };
  }, [productId, retryCount]);

  useEffect(() => {
    if (!product) return undefined;
    const previousTitle = document.title;
    document.title = `${product.name} — Muller's Firearms`;
    return () => { document.title = previousTitle; };
  }, [product]);

  const categoryUrl = category ? `/catalog/${category.slug}` : "/catalog";
  const inStock = product?.is_active && product.stock > 0;
  const attributes = Object.entries(product?.attributes || {});

  return (
    <main className="catalog-page product-page">
      <CartToast notice={notice} onClose={dismissNotice} />
      <div className="container product-layout">
        <Link to={categoryUrl} className="catalog-back-link">
          <span aria-hidden="true">←</span> {category ? "Назад в категорию" : "В каталог"}
        </Link>

        {loading && <div className="catalog-status" role="status">Загружаем товар…</div>}
        {!loading && notFound && (
          <section className="glass-panel product-empty" aria-labelledby="product-not-found">
            <p className="catalog-heading__eyebrow">Каталог</p>
            <h1 id="product-not-found">Товар не найден</h1>
            <p>Возможно, ссылка устарела или товар больше не доступен</p>
            <Link className="product-secondary-action" to="/catalog">Перейти в каталог ↗</Link>
          </section>
        )}
        {!loading && error && (
          <div className="catalog-status catalog-status--error product-load-error" role="alert">
            <p>{error}</p>
            <button className="product-secondary-action" onClick={() => setRetryCount((value) => value + 1)}>
              Повторить
            </button>
          </div>
        )}

        {!loading && !error && !notFound && product && (
          <>
            <nav className="product-breadcrumbs" aria-label="Хлебные крошки">
              <Link to="/catalog">Каталог</Link>
              {category && <><span aria-hidden="true">/</span><Link to={categoryUrl}>{category.name}</Link></>}
              <span aria-hidden="true">/</span>
              <span aria-current="page">{product.name}</span>
            </nav>

            <section className="product-hero" aria-labelledby="product-title">
              <div className="glass-panel product-gallery">
                <div className="product-gallery__caption" aria-hidden="true">
                  <span>{product.brand || "Muller's Firearms"}</span>
                  <span>01 / 01</span>
                </div>
                <ProductImage src={product.image_url} name={product.name} priority />
                <span className="product-gallery__sku">{product.sku}</span>
              </div>

              <div className="product-summary">
                <p className="catalog-heading__eyebrow">{product.brand || "Коллекция Muller's Firearms"}</p>
                <h1 id="product-title">{product.name}</h1>
                {product.short_description && <p className="product-summary__intro">{product.short_description}</p>}
                <span className={`product-stock${inStock ? " is-available" : ""}`}>
                  <span aria-hidden="true" />
                  {inStock ? `В наличии · ${product.stock} шт` : "Нет в наличии"}
                </span>

                <div className="product-purchase">
                  <span className="product-purchase__label">Стоимость</span>
                  <div className="product-price">
                    <strong>{currencyFormatter.format(Number(product.price))}</strong>
                    {Number(product.old_price) > Number(product.price) && (
                      <del>{currencyFormatter.format(Number(product.old_price))}</del>
                    )}
                  </div>
                  <button
                    className="product-add-button"
                    type="button"
                    disabled={!inStock || addingProductId !== null}
                    onClick={() => addProduct(product)}
                  >
                    <span>{addingProductId === product.id ? "Добавляем…" : "Добавить в корзину"}</span>
                    <span aria-hidden="true">↗</span>
                  </button>
                  <a className="product-specs-link" href="#product-specifications">Смотреть характеристики ↓</a>
                </div>
              </div>
            </section>

            <div className="product-information">
              <section className="glass-panel product-description" aria-labelledby="product-description-title">
                <p className="catalog-heading__eyebrow">Подробнее</p>
                <h2 id="product-description-title">О модели</h2>
                <p className="product-description__text">
                  {product.description || product.short_description || "Описание пока не добавлено"}
                </p>
              </section>

              <section className="glass-panel product-specifications" id="product-specifications" aria-labelledby="product-specifications-title">
                <p className="catalog-heading__eyebrow">Детали</p>
                <h2 id="product-specifications-title">Характеристики</h2>
                {attributes.length > 0 ? (
                  <dl>
                    {attributes.map(([name, value]) => (
                      <div key={name}><dt>{name}</dt><dd>{value}</dd></div>
                    ))}
                  </dl>
                ) : <p className="product-description__text">Характеристики пока не добавлены</p>}
              </section>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
