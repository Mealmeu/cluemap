import { Navigate, Outlet } from "react-router-dom";

import { useAuthStore } from "../store/auth-store";
import type { Role } from "../types/api";

interface RoleGuardProps {
  roles: Role[];
}

export const RoleGuard = ({ roles }: RoleGuardProps) => {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate replace to="/login" />;
  }

  if (!roles.includes(user.role)) {
    return <Navigate replace to="/problems" />;
  }

  return <Outlet />;
};
