import { useState } from "react";
import { AuthContext } from "./authContext";

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  const login = (newToken) => {
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        login,
        logout,
        isAuthenticated: Boolean(token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

