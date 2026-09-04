import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { clearCart, getCart, removeCartItem } from "../api/cartApi";
import { createOrderFromCart } from "../api/ordersApi";

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

export default function CartPage() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(null);
  const [operation, setOperation] = useState("");

  const loadCart = useCallback(async () => {
    try {
      const data = await getCart();
      setCart(data);
      setError("");
    } catch {
      setError("Не удалось загрузить корзину.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCart();
  }, [loadCart]);

  const items = useMemo(() => cart?.items || cart?.cart_items || [], [cart]);

  const total = useMemo(() => {
    if (cart?.total_amount !== undefined) return Number(cart.total_amount);

    return items.reduce((sum, item) => {
      const price = Number(item.product?.price ?? item.price ?? 0);
      const quantity = item.quantity ?? 1;
      return sum + price * quantity;
    }, 0);
  }, [cart?.total_amount, items]);

  const itemCount = items.reduce((sum, item) => sum + (item.quantity ?? 1), 0);

  const handleCreateOrder = async () => {
    setOperation("order");
    setNotice(null);

    try {
      await createOrderFromCart();
      setNotice({ type: "success", text: "Заказ успешно оформлен." });
      await loadCart();
    } catch {
      setNotice({ type: "error", text: "Не удалось оформить заказ." });
    } finally {
      setOperation("");
    }
  };

  const handleClearCart = async () => {
    setOperation("clear");
    setNotice(null);

    try {
      await clearCart();
      setNotice({ type: "success", text: "Корзина очищена." });
      await loadCart();
    } catch {
      setNotice({ type: "error", text: "Не удалось очистить корзину." });
    } finally {
      setOperation("");
    }
  };

  const handleRemoveItem = async (itemId) => {
    setOperation(`remove-${itemId}`);
    setNotice(null);

    try {
      await removeCartItem(itemId);
      await loadCart();
    } catch {
      setNotice({ type: "error", text: "Не удалось удалить позицию." });
    } finally {
      setOperation("");
    }
  };

  return (
    <main className="workspace-page cart-page">
      <div className="container workspace-layout">
        <header className="workspace-heading">
          <p className="workspace-heading__eyebrow">Личный кабинет / покупки</p>
          <h1>Корзина</h1>
          <p>Проверьте выбранные позиции перед оформлением заказа.</p>
        </header>

        {notice && (
          <div className={`workspace-notice workspace-notice--${notice.type}`} role="status">
            {notice.text}
          </div>
        )}

        {loading && <div className="workspace-status">Загружаем корзину…</div>}
        {!loading && error && (
          <div className="workspace-status workspace-status--error">{error}</div>
        )}

        {!loading && !error && items.length === 0 && (
          <section className="glass-panel empty-state">
            <span className="empty-state__mark" aria-hidden="true">0</span>
            <p className="workspace-heading__eyebrow">Пока ничего нет</p>
            <h2>Корзина пуста</h2>
            <p>Перейдите в каталог и добавьте подходящие позиции.</p>
            <Link to="/catalog" className="workspace-primary-button">
              Открыть каталог <span aria-hidden="true">↗</span>
            </Link>
          </section>
        )}

        {!loading && !error && items.length > 0 && (
          <div className="cart-layout">
            <section className="cart-items" aria-label="Товары в корзине">
              {items.map((item, index) => {
                const product = item.product || {};
                const name =
                  item.product_name || product.name || item.name || `Товар #${index + 1}`;
                const price = Number(product.price ?? item.price ?? 0);
                const quantity = item.quantity ?? 1;
                const itemTotal = Number(item.total_price ?? price * quantity);
                const isRemoving = operation === `remove-${item.id}`;

                return (
                  <article
                    className="glass-panel cart-item"
                    key={item.id ?? index}
                    style={{ "--card-delay": `${120 + index * 80}ms` }}
                  >
                    <div className="cart-item__index" aria-hidden="true">
                      {String(index + 1).padStart(2, "0")}
                    </div>

                    <div className="cart-item__content">
                      <p className="cart-item__label">Выбранная позиция</p>
                      <h2>{name}</h2>
                      <div className="cart-item__meta">
                        <span>{currencyFormatter.format(price)}</span>
                        <span aria-hidden="true">×</span>
                        <span>{quantity} шт.</span>
                      </div>
                    </div>

                    <div className="cart-item__actions">
                      <strong>{currencyFormatter.format(itemTotal)}</strong>
                      {item.id && (
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(item.id)}
                          disabled={Boolean(operation)}
                        >
                          {isRemoving ? "Удаляем…" : "Удалить"}
                        </button>
                      )}
                    </div>
                  </article>
                );
              })}
            </section>

            <aside className="glass-panel cart-summary">
              <p className="cart-summary__eyebrow">Ваш заказ</p>
              <h2>Итого</h2>

              <dl>
                <div>
                  <dt>Количество</dt>
                  <dd>{itemCount} шт.</dd>
                </div>
                <div>
                  <dt>Стоимость</dt>
                  <dd>{currencyFormatter.format(total)}</dd>
                </div>
              </dl>

              <div className="cart-summary__total">
                <span>К оплате</span>
                <strong>{currencyFormatter.format(total)}</strong>
              </div>

              <p className="cart-summary__note">
                Оформление регулируемых товаров производится с соблюдением установленных
                требований.
              </p>

              <button
                type="button"
                className="workspace-primary-button"
                onClick={handleCreateOrder}
                disabled={Boolean(operation)}
              >
                {operation === "order" ? "Оформляем…" : "Оформить заказ"}
              </button>
              <button
                type="button"
                className="workspace-text-button"
                onClick={handleClearCart}
                disabled={Boolean(operation)}
              >
                {operation === "clear" ? "Очищаем…" : "Очистить корзину"}
              </button>
            </aside>
          </div>
        )}
      </div>
    </main>
  );
}
