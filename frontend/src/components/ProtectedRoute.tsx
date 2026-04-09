import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthStore } from "../store/auth-store";

export const ProtectedRoute = () => {
  const status = useAuthStore((state) => state.status);
  const location = useLocation();

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="card px-6 py-5 text-sm text-slate-600">인증 상태를 확인하고 있습니다...</div>
      </div>
    );
  }

  if (status !== "authenticated") {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return <Outlet />;
};
