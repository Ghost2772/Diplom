import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getMyOrders } from "../api/ordersApi";

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const orderDateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const STATUS_LABELS = {
  created: "Создан",
  confirmed: "Подтверждён",
  processing: "В обработке",
  shipped: "Передан в доставку",
  completed: "Завершён",
  cancelled: "Отменён",
};

const getPositionLabel = (count) => {
  const lastTwoDigits = count % 100;
  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) return "позиций";

  const lastDigit = count % 10;
  if (lastDigit === 1) return "позиция";
  if (lastDigit >= 2 && lastDigit <= 4) return "позиции";
  return "позиций";
};

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadOrders = useCallback(async () => {
    setLoading(true);

    try {
      const data = await getMyOrders();
      setOrders(Array.isArray(data) ? data : []);
      setError("");
    } catch {
      setError("Не удалось загрузить историю заказов.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  const sortedOrders = useMemo(
    () =>
      [...orders].sort(
        (first, second) => new Date(second.created_at) - new Date(first.created_at),
      ),
    [orders],
  );

  const totalSpent = orders.reduce(
    (sum, order) => sum + Number(order.total_amount ?? order.total_price ?? 0),
    0,
  );

  return (
    <main className="workspace-page orders-page">
      <div className="container workspace-layout">
        <header className="workspace-heading">
          <p className="workspace-heading__eyebrow">Личный кабинет / покупки</p>
          <h1>Мои заказы</h1>
          <p>История оформленных заказов, их состав и текущие статусы.</p>
        </header>

        {loading && <div className="workspace-status">Загружаем заказы…</div>}

        {!loading && error && (
          <div className="workspace-status workspace-status--error orders-error">
            <span>{error}</span>
            <button type="button" onClick={loadOrders}>Повторить</button>
          </div>
        )}

        {!loading && !error && orders.length === 0 && (
          <section className="glass-panel empty-state">
            <span className="empty-state__mark" aria-hidden="true">0</span>
            <p className="workspace-heading__eyebrow">История пуста</p>
            <h2>Заказов пока нет</h2>
            <p>Соберите первую подборку товаров в каталоге и оформите её через корзину.</p>
            <Link to="/catalog" className="workspace-primary-button">
              Перейти в каталог <span aria-hidden="true">↗</span>
            </Link>
          </section>
        )}

        {!loading && !error && orders.length > 0 && (
          <>
            <section className="glass-panel orders-overview" aria-label="Сводка заказов">
              <div>
                <span>Всего заказов</span>
                <strong>{orders.length}</strong>
              </div>
              <div>
                <span>Позиций заказано</span>
                <strong>
                  {orders.reduce(
                    (sum, order) =>
                      sum +
                      (order.items || []).reduce(
                        (itemSum, item) => itemSum + Number(item.quantity || 0),
                        0,
                      ),
                    0,
                  )}
                </strong>
              </div>
              <div>
                <span>Общая стоимость</span>
                <strong>{currencyFormatter.format(totalSpent)}</strong>
              </div>
            </section>

            <section className="orders-list" aria-label="История заказов">
              {sortedOrders.map((order, index) => {
                const items = Array.isArray(order.items) ? order.items : [];
                const total = Number(order.total_amount ?? order.total_price ?? 0);
                const orderNumber = order.order_number || `MF-${order.id}`;
                const orderDate = order.created_at ? new Date(order.created_at) : null;

                return (
                  <article
                    className="glass-panel order-card"
                    key={order.id}
                    style={{ "--card-delay": `${160 + index * 90}ms` }}
                  >
                    <header className="order-card__header">
                      <div>
                        <p>Заказ</p>
                        <h2>№ {orderNumber}</h2>
                        {orderDate && !Number.isNaN(orderDate.getTime()) && (
                          <time dateTime={order.created_at}>
                            {orderDateFormatter.format(orderDate)}
                          </time>
                        )}
                      </div>
                      <span className={`order-status order-status--${order.status || "created"}`}>
                        <span aria-hidden="true" />
                        {STATUS_LABELS[order.status] || order.status || "Создан"}
                      </span>
                    </header>

                    <div className="order-card__items">
                      {items.map((item, itemIndex) => (
                        <div className="order-line" key={item.id ?? itemIndex}>
                          <span className="order-line__index" aria-hidden="true">
                            {String(itemIndex + 1).padStart(2, "0")}
                          </span>
                          <div>
                            <strong>
                              {item.product_name || item.product?.name || `Товар #${itemIndex + 1}`}
                            </strong>
                            <span>{item.product_sku || "Артикул не указан"}</span>
                          </div>
                          <span>{item.quantity || 1} шт.</span>
                          <strong>
                            {currencyFormatter.format(
                              Number(item.total_price ?? Number(item.price || 0) * (item.quantity || 1)),
                            )}
                          </strong>
                        </div>
                      ))}
                    </div>

                    <footer className="order-card__footer">
                      <span>{items.length} {getPositionLabel(items.length)}</span>
                      <div>
                        <span>Сумма заказа</span>
                        <strong>{currencyFormatter.format(total)}</strong>
                      </div>
                    </footer>
                  </article>
                );
              })}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
