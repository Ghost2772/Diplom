// import api from "./axios";

// export const getProducts = async () => {
//   const response = await api.get("/products");
//   return response.data;
// };

import api from "./axios";

export const getProducts = async () => {
  const response = await api.get("/products");
  console.log("GET /products response:", response.data);
  return response.data;
};