import { Navigate, Outlet, useLocation } from "react-router-dom";
import { isAuthenticated } from "@/lib/auth";

export default function ProtectedRoute() {
  const location = useLocation();
  const authed = isAuthenticated();

  if (!authed) {
    const redirect = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?redirect=${redirect}`} replace />;
  }

  return <Outlet />;
}
