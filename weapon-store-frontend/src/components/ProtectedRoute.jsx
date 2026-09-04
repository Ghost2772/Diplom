import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/authContext";

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { isAuthenticated, user, userLoading } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (userLoading) {
    return (
      <main className="workspace-page">
        <div className="container workspace-layout">
          <div className="workspace-status">Проверяем права доступа…</div>
        </div>
      </main>
    );
  }

  if (adminOnly && !user?.is_admin) {
    return <Navigate to="/profile" replace />;
  }

  return children;
}
