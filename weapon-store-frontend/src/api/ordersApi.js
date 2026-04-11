import api from "./axios";

export const createOrderFromCart = async () => {
  const response = await api.post("/orders/create-from-cart");
  return response.data;
};

export const getMyOrders = async () => {
  const response = await api.get("/orders/my");
  return response.data;
};