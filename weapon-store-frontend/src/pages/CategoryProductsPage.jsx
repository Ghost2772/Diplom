import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { addToCart } from "../api/cartApi";
import { getCategories, getProducts } from "../api/productsApi";

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const CATEGORY_TITLES = {
  "smoothbore-shotguns": "Гладкоствольное оружие",
};

export default function CategoryProductsPage() {
  const { categorySlug } = useParams();
  const [category, setCategory] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadCategory = async () => {
      try {
        const categories = await getCategories();
        const currentCategory = Array.isArray(categories)
          ? categories.find((item) => item.slug === categorySlug)
          : null;

        if (!currentCategory) {
          throw new Error("CATEGORY_NOT_FOUND");
        }

        const categoryProducts = await getProducts({
          category_id: currentCategory.id,
          is_active: true,
        });

        if (!isMounted) return;
        setCategory(currentCategory);
        setProducts(Array.isArray(categoryProducts) ? categoryProducts : []);
      } catch {
        if (isMounted) {
          setError("Не удалось загрузить товары выбранной категории.");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadCategory();

    return () => {
      isMounted = false;
    };
  }, [categorySlug]);

  const handleAddToCart = async (productId) => {
    try {
      await addToCart(productId, 1);
      alert("Товар добавлен в корзину");
    } catch {
      alert("Войдите в аккаунт, чтобы добавить товар в корзину");
    }
  };

  const categoryTitle = CATEGORY_TITLES[categorySlug] || category?.name || "Категория";

  return (
    <main className="catalog-page category-products-page">
      <div className="container catalog-layout">
        <Link to="/catalog" className="catalog-back-link">
          <span aria-hidden="true">←</span> Все категории
        </Link>

        <header className="catalog-heading catalog-heading--compact">
          <p className="catalog-heading__eyebrow">Каталог / категория</p>
          <h1>{categoryTitle}</h1>
          {category?.description && <p>{category.description}</p>}
        </header>

        {loading && <div className="catalog-status">Загружаем товары…</div>}
        {!loading && error && <div className="catalog-status catalog-status--error">{error}</div>}
        {!loading && !error && products.length === 0 && (
          <div className="catalog-status">В этой категории пока нет товаров.</div>
        )}

        {!loading && !error && products.length > 0 && (
          <section className="product-grid" aria-label={`Товары: ${categoryTitle}`}>
            {products.map((product, index) => (
              <article
                className="product-card"
                key={product.id}
                style={{ "--card-delay": `${180 + index * 90}ms` }}
              >
                <div className="product-card__topline">
                  <span>{product.brand || "Muller's Firearms"}</span>
                  <span>{product.stock > 0 ? "В наличии" : "Нет в наличии"}</span>
                </div>

                <div className="product-card__body">
                  <p className="product-card__sku">{product.sku}</p>
                  <h2>{product.name}</h2>
                  <p className="product-card__description">
                    {product.short_description || product.description}
                  </p>

                  {product.attributes && Object.keys(product.attributes).length > 0 && (
                    <ul className="product-card__attributes">
                      {Object.entries(product.attributes).map(([name, value]) => (
                        <li key={name}>
                          <span>{name}</span>
                          <strong>{value}</strong>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="product-card__footer">
                  <strong>{currencyFormatter.format(Number(product.price))}</strong>
                  <button
                    type="button"
                    disabled={product.stock <= 0}
                    onClick={() => handleAddToCart(product.id)}
                  >
                    В корзину
                  </button>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
