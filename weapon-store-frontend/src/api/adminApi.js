import api from "./axios";

export const getAdminUsers = async () => {
  const response = await api.get("/users");
  return response.data;
};

export const getAdminOrders = async () => {
  const response = await api.get("/orders");
  return response.data;
};

export const updateAdminOrderStatus = async (orderId, status) => {
  const response = await api.patch(`/orders/${orderId}/status`, { status });
  return response.data;
};

export const deleteAdminOrder = async (orderId) => {
  await api.delete(`/orders/${orderId}`);
};
