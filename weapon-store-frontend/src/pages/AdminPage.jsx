import { useCallback, useEffect, useMemo, useState } from "react";
import {
  deleteAdminOrder,
  getAdminOrders,
  getAdminUsers,
  updateAdminOrderStatus,
} from "../api/adminApi";
import { getApiErrorMessage } from "../utils/apiErrors";

const ORDER_STATUSES = [
  ["created", "Создан"],
  ["confirmed", "Подтверждён"],
  ["processing", "В обработке"],
  ["shipped", "Передан в доставку"],
  ["completed", "Завершён"],
  ["cancelled", "Отменён"],
];

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const formatDate = (date) => {
  if (!date) return "Дата не указана";
  const parsedDate = new Date(date);
  return Number.isNaN(parsedDate.getTime()) ? "Дата не указана" : dateFormatter.format(parsedDate);
};

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [activeSection, setActiveSection] = useState("orders");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [updatingOrderId, setUpdatingOrderId] = useState(null);
  const [orderToDelete, setOrderToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadAdminData = useCallback(async () => {
    setLoading(true);
    setLoadError("");
    setActionError("");
    setNotice("");

    try {
      const [usersData, ordersData] = await Promise.all([
        getAdminUsers(),
        getAdminOrders(),
      ]);
      setUsers(Array.isArray(usersData) ? usersData : []);
      setOrders(Array.isArray(ordersData) ? ordersData : []);
    } catch (requestError) {
      setLoadError(
        getApiErrorMessage(
          requestError,
          "Не удалось загрузить данные административной панели.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAdminData();
  }, [loadAdminData]);

  const usersById = useMemo(
    () => new Map(users.map((user) => [user.id, user])),
    [users],
  );

  const activeOrdersCount = orders.filter(
    (order) => !["completed", "cancelled"].includes(order.status),
  ).length;

  const handleStatusChange = async (orderId, status) => {
    setUpdatingOrderId(orderId);
    setNotice("");
    setActionError("");

    try {
      const updatedOrder = await updateAdminOrderStatus(orderId, status);
      setOrders((currentOrders) =>
        currentOrders.map((order) => (order.id === orderId ? updatedOrder : order)),
      );
      setNotice(`Статус заказа № ${updatedOrder.order_number} обновлён.`);
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(requestError, "Не удалось изменить статус заказа."),
      );
    } finally {
      setUpdatingOrderId(null);
    }
  };

  const handleDeleteOrder = async () => {
    if (!orderToDelete) return;

    setDeleting(true);
    setNotice("");
    setActionError("");

    try {
      await deleteAdminOrder(orderToDelete.id);
      setOrders((currentOrders) =>
        currentOrders.filter((order) => order.id !== orderToDelete.id),
      );
      setNotice(`Заказ № ${orderToDelete.order_number} удалён.`);
      setOrderToDelete(null);
    } catch (requestError) {
      setActionError(getApiErrorMessage(requestError, "Не удалось удалить заказ."));
      setOrderToDelete(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <main className="workspace-page admin-page">
      <div className="container workspace-layout workspace-layout--admin">
        <header className="workspace-heading admin-heading">
          <p className="workspace-heading__eyebrow">Системное управление</p>
          <h1>Админ-панель</h1>
          <p>Пользователи, заказы и управление этапами обработки в одном интерфейсе.</p>
        </header>

        {loading && <div className="workspace-status">Загружаем данные…</div>}

        {!loading && loadError && (
          <div className="workspace-status workspace-status--error admin-error">
            <span>{loadError}</span>
            <button type="button" onClick={loadAdminData}>Повторить</button>
          </div>
        )}

        {!loading && !loadError && (
          <>
            <section className="glass-panel admin-overview" aria-label="Сводка">
              <div>
                <span>Пользователи</span>
                <strong>{users.length}</strong>
              </div>
              <div>
                <span>Все заказы</span>
                <strong>{orders.length}</strong>
              </div>
              <div>
                <span>Требуют внимания</span>
                <strong>{activeOrdersCount}</strong>
              </div>
            </section>

            <div className="admin-toolbar">
              <div className="admin-tabs" role="tablist" aria-label="Разделы панели">
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeSection === "orders"}
                  className={activeSection === "orders" ? "is-active" : ""}
                  onClick={() => setActiveSection("orders")}
                >
                  Заказы <span>{orders.length}</span>
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeSection === "users"}
                  className={activeSection === "users" ? "is-active" : ""}
                  onClick={() => setActiveSection("users")}
                >
                  Пользователи <span>{users.length}</span>
                </button>
              </div>
              <button className="admin-refresh" type="button" onClick={loadAdminData}>
                Обновить данные
              </button>
            </div>

            {notice && (
              <div className="workspace-notice workspace-notice--success" role="status">
                {notice}
              </div>
            )}

            {actionError && (
              <div className="workspace-notice workspace-notice--error" role="alert">
                {actionError}
              </div>
            )}

            {activeSection === "orders" && (
              <section className="admin-section" role="tabpanel">
                <div className="admin-section__heading">
                  <div>
                    <p>Управление заказами</p>
                    <h2>Текущие заказы</h2>
                  </div>
                  <span>{orders.length} записей</span>
                </div>

                {orders.length === 0 ? (
                  <div className="glass-panel admin-empty">Заказов пока нет.</div>
                ) : (
                  <div className="admin-orders">
                    {orders.map((order, index) => {
                      const customer = usersById.get(order.user_id);
                      const productNames = (order.items || [])
                        .map((item) => item.product_name)
                        .filter(Boolean)
                        .join(", ");

                      return (
                        <article
                          className="glass-panel admin-order-card"
                          key={order.id}
                          style={{ "--card-delay": `${100 + index * 55}ms` }}
                        >
                          <div className="admin-order-card__identity">
                            <span className="admin-order-card__index">
                              {String(index + 1).padStart(2, "0")}
                            </span>
                            <div>
                              <p>{customer?.email || `Пользователь #${order.user_id}`}</p>
                              <h3>№ {order.order_number}</h3>
                              <time dateTime={order.created_at}>{formatDate(order.created_at)}</time>
                            </div>
                            <strong>{currencyFormatter.format(Number(order.total_amount || 0))}</strong>
                          </div>

                          <div className="admin-order-card__contents">
                            <span>{order.items?.length || 0} позиций</span>
                            <p>{productNames || "Состав заказа не указан"}</p>
                          </div>

                          <footer className="admin-order-card__actions">
                            <label>
                              <span>Статус заказа</span>
                              <select
                                value={order.status}
                                disabled={updatingOrderId === order.id}
                                onChange={(event) =>
                                  handleStatusChange(order.id, event.target.value)
                                }
                              >
                                {ORDER_STATUSES.map(([value, label]) => (
                                  <option value={value} key={value}>{label}</option>
                                ))}
                              </select>
                            </label>
                            <button
                              type="button"
                              className="admin-delete-button"
                              onClick={() => setOrderToDelete(order)}
                            >
                              Удалить заказ
                            </button>
                          </footer>
                        </article>
                      );
                    })}
                  </div>
                )}
              </section>
            )}

            {activeSection === "users" && (
              <section className="admin-section" role="tabpanel">
                <div className="admin-section__heading">
                  <div>
                    <p>Учётные записи</p>
                    <h2>Зарегистрированные пользователи</h2>
                  </div>
                  <span>{users.length} записей</span>
                </div>

                <div className="glass-panel admin-users-table-wrap">
                  <table className="admin-users-table">
                    <thead>
                      <tr>
                        <th>Пользователь</th>
                        <th>Телефон</th>
                        <th>Роль</th>
                        <th>Статус</th>
                        <th>Регистрация</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td>
                            <strong>{user.full_name || "Имя не указано"}</strong>
                            <span>{user.email}</span>
                          </td>
                          <td>{user.phone || "Не указан"}</td>
                          <td>
                            <span className={`admin-role${user.is_admin ? " is-admin" : ""}`}>
                              {user.is_admin ? "Администратор" : "Клиент"}
                            </span>
                          </td>
                          <td>
                            <span className={`admin-user-status${user.is_active ? " is-active" : ""}`}>
                              <span aria-hidden="true" />
                              {user.is_active ? "Активен" : "Отключён"}
                            </span>
                          </td>
                          <td>{formatDate(user.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
        )}
      </div>

      {orderToDelete && (
        <div className="admin-modal-backdrop">
          <section
            className="glass-panel admin-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-order-title"
          >
            <span className="admin-modal__mark" aria-hidden="true">!</span>
            <p className="workspace-heading__eyebrow">Необратимое действие</p>
            <h2 id="delete-order-title">Удалить заказ?</h2>
            <p>
              Заказ № {orderToDelete.order_number} и все его позиции будут удалены из истории.
            </p>
            <div>
              <button
                type="button"
                className="admin-modal__cancel"
                disabled={deleting}
                onClick={() => setOrderToDelete(null)}
              >
                Отмена
              </button>
              <button
                type="button"
                className="admin-modal__confirm"
                disabled={deleting}
                onClick={handleDeleteOrder}
              >
                {deleting ? "Удаляем…" : "Удалить"}
              </button>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
