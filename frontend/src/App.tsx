import { AppRoutes } from "./routes";
import { useBootstrapAuth } from "./hooks/useAuth";

export default function App() {
  useBootstrapAuth();

  return <AppRoutes />;
}
