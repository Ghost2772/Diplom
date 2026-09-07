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

export const createAdminProduct = async (product) => {
  const response = await api.post("/products", product);
  return response.data;
};

export const updateAdminProduct = async (productId, product) => {
  const response = await api.put(`/products/${productId}`, product);
  return response.data;
};

export const uploadProductImage = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const response = await api.post("/products/images", form, { timeout: 60000 });
  return response.data.image_url;
};
