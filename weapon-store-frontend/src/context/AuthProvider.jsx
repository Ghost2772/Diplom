import { useEffect, useState } from "react";
import { getCurrentUser, getDemoConfig } from "../api/authApi";
import { AuthContext } from "./authContext";

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(null);
  const [userLoading, setUserLoading] = useState(Boolean(token));
  const [demoConfig, setDemoConfig] = useState(null);
  const [sessionNotice, setSessionNotice] = useState("");

  useEffect(() => {
    let isMounted = true;
    getDemoConfig()
      .then((config) => {
        if (isMounted) setDemoConfig(config);
      })
      .catch(() => {
        // Normal sign-in remains available if demo mode cannot be loaded.
      });
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    if (!user?.is_demo || !user.demo_expires_at) return undefined;

    const expiresAt = new Date(user.demo_expires_at).getTime();
    const expireSession = () => {
      if (Date.now() < expiresAt) return;
      localStorage.removeItem("access_token");
      setToken(null);
      setUser(null);
      setUserLoading(false);
      setSessionNotice("Демо-сессия завершилась. Вы можете открыть новую одним нажатием");
    };
    const timer = window.setTimeout(expireSession, Math.max(0, expiresAt - Date.now()));
    document.addEventListener("visibilitychange", expireSession);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("visibilitychange", expireSession);
    };
  }, [user]);

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
    setSessionNotice("");
    setUserLoading(true);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setSessionNotice("");
    setUserLoading(false);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        userLoading,
        demoConfig,
        sessionNotice,
        login,
        logout,
        isAuthenticated: Boolean(token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
