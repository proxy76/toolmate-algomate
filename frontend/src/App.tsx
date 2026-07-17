import { Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider, useAuth } from "./auth";
import { Layout } from "./components/Layout";
import { AdminDashboard } from "./pages/AdminDashboard";
import { Arhiva } from "./pages/Arhiva";
import { BlogIndex } from "./pages/Blog";
import { BlogPostPage } from "./pages/BlogPost";
import { Contact } from "./pages/Contact";
import { Dashboard } from "./pages/Dashboard";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { Practice } from "./pages/Practice";
import { Register } from "./pages/Register";
import { Simulate } from "./pages/Simulate";
import { Verify } from "./pages/Verify";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-10 text-center text-ink-muted">Se încarcă…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AdminRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-10 text-center text-ink-muted">Se încarcă…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_staff) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/simulate" element={<Simulate />} />
          <Route path="/arhiva" element={<Arhiva />} />
          <Route path="/blog" element={<BlogIndex />} />
          <Route path="/blog/:slug" element={<BlogPostPage />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify" element={<Verify />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  );
}
