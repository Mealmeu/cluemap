import { NavLink, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { RoleGuard } from "../components/RoleGuard";
import { useAuth } from "../hooks/useAuth";
import { useAuthStore } from "../store/auth-store";
import { LoginPage } from "../pages/LoginPage";
import { ProblemDetailPage } from "../pages/ProblemDetailPage";
import { ProblemsPage } from "../pages/ProblemsPage";
import { RegisterPage } from "../pages/RegisterPage";
import { SubmissionResultPage } from "../pages/SubmissionResultPage";
import { TeacherDashboardPage } from "../pages/TeacherDashboardPage";
import { TeacherProblemManagementPage } from "../pages/TeacherProblemManagementPage";

const AppShell = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const { logoutMutation } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-slate-50 to-white">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <div>
            <p className="text-sm font-semibold text-blue-700">ClueMap</p>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>

          <nav className="flex flex-wrap items-center gap-3">
            <NavLink className="text-sm font-medium text-slate-600 hover:text-blue-700" to="/problems">
              문제 목록
            </NavLink>
            {user?.role === "teacher" ? (
              <>
                <NavLink className="text-sm font-medium text-slate-600 hover:text-blue-700" to="/teacher/dashboard">
                  대시보드
                </NavLink>
                <NavLink className="text-sm font-medium text-slate-600 hover:text-blue-700" to="/teacher/problems">
                  문제 관리
                </NavLink>
              </>
            ) : null}
            <button
              className="button-secondary"
              onClick={() =>
                logoutMutation.mutate(undefined, {
                  onSettled: () => navigate("/login")
                })
              }
              type="button"
            >
              로그아웃
            </button>
          </nav>
        </div>
      </header>
      <Outlet />
    </div>
  );
};

const HomeRedirect = () => {
  const user = useAuthStore((state) => state.user);
  return <Navigate replace to={user?.role === "teacher" ? "/teacher/dashboard" : "/problems"} />;
};

export const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<LoginPage />} path="/login" />
      <Route element={<RegisterPage />} path="/register" />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route element={<HomeRedirect />} path="/" />
          <Route element={<ProblemsPage />} path="/problems" />
          <Route element={<ProblemDetailPage />} path="/problems/:problemId" />
          <Route element={<SubmissionResultPage />} path="/submissions/:submissionId" />

          <Route element={<RoleGuard roles={["teacher"]} />}>
            <Route element={<TeacherDashboardPage />} path="/teacher/dashboard" />
            <Route element={<TeacherProblemManagementPage />} path="/teacher/problems" />
          </Route>
        </Route>
      </Route>

      <Route element={<Navigate replace to="/" />} path="*" />
    </Routes>
  );
};
