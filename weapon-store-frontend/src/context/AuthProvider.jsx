import { useEffect, useState } from "react";
import { getCurrentUser } from "../api/authApi";
import { AuthContext } from "./authContext";

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(null);
  const [userLoading, setUserLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) {
      return undefined;
    }

    let isMounted = true;
    getCurrentUser()
      .then((profile) => {
        if (isMounted) setUser(profile);
      })
      .catch((error) => {
        if (!isMounted) return;

        setUser(null);
        if ([401, 403].includes(error?.response?.status)) {
          localStorage.removeItem("access_token");
          setToken(null);
        }
      })
      .finally(() => {
        if (isMounted) setUserLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const login = (newToken) => {
    localStorage.setItem("access_token", newToken);
    setUser(null);
    setUserLoading(true);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setUserLoading(false);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        userLoading,
        login,
        logout,
        isAuthenticated: Boolean(token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
