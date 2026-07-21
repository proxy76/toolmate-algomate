import { Calculator, CircleUser, LogOut, Menu, ShieldCheck, X } from "lucide-react";
import { ReactNode, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";

const navItems = [
  { to: "/", label: "Acasă" },
  { to: "/practice", label: "Antrenament" },
  { to: "/simulate", label: "Simulare BAC" },
  { to: "/arhiva", label: "Arhivă" },
  { to: "/blog", label: "Blog" },
  { to: "/contact", label: "Contact" },
];

const navLinkClass = (isActive: boolean) =>
  `px-3 py-2 rounded-lg text-sm transition-colors ${
    isActive
      ? "text-oxblood font-semibold bg-oxblood/10"
      : "text-ink-muted font-medium hover:text-ink hover:bg-sunken"
  }`;

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);

  // The practice workspace is a full-height, two-pane app view — the marketing
  // footer would only fight the split for the viewport, so it sits this one out.
  const fullBleed = pathname === "/practice";

  return (
    <div className="min-h-full flex flex-col">
      <header className="sticky top-0 z-30 bg-paper/90 backdrop-blur supports-[backdrop-filter]:bg-paper/75 border-b border-edge">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3 group">
            <span className="grid place-items-center w-10 h-10 rounded-xl bg-oxblood/10 text-oxblood transition-colors group-hover:bg-oxblood/15">
              <Calculator size={22} strokeWidth={2.25} />
            </span>
            <span className="leading-tight">
              <span className="block text-lg font-extrabold tracking-tight text-ink-strong">
                Algomate
              </span>
              <span className="block text-xs text-ink-muted">
                Antrenament BAC Matematică
              </span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) => navLinkClass(isActive)}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-2">
            {user ? (
              <>
                {user.is_staff && (
                  <NavLink
                    to="/admin"
                    title="Panou de administrare"
                    aria-label="Panou de administrare"
                    className={({ isActive }) =>
                      `inline-flex items-center justify-center w-10 h-10 rounded-lg transition-colors ${
                        isActive ? "text-oxblood bg-oxblood/10" : "text-ink-muted hover:text-ink hover:bg-sunken"
                      }`
                    }
                  >
                    <ShieldCheck size={22} strokeWidth={2} />
                  </NavLink>
                )}
                <NavLink
                  to="/dashboard"
                  title={`Seturile mele · ${user.email}`}
                  aria-label="Seturile mele"
                  className={({ isActive }) =>
                    `inline-flex items-center justify-center w-10 h-10 rounded-lg transition-colors ${
                      isActive
                        ? "text-oxblood bg-oxblood/10"
                        : "text-ink-muted hover:text-ink hover:bg-sunken"
                    }`
                  }
                >
                  <CircleUser size={22} strokeWidth={2} />
                </NavLink>
                <button
                  onClick={() => {
                    logout();
                    navigate("/");
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-edge text-sm font-medium text-ink hover:bg-sunken transition-colors"
                >
                  <LogOut size={16} /> Ieșire
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-3 py-2 rounded-lg text-sm font-medium text-ink hover:bg-sunken transition-colors"
                >
                  Autentificare
                </Link>
                <Link
                  to="/register"
                  className="px-3 py-2 rounded-lg bg-oxblood text-paper text-sm font-semibold hover:bg-oxblood-deep transition-colors"
                >
                  Înregistrare
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center gap-2">
            {user && (
              <NavLink
                to="/dashboard"
                onClick={() => setOpen(false)}
                aria-label="Seturile mele"
                className={({ isActive }) =>
                  `inline-flex items-center justify-center w-10 h-10 rounded-lg transition-colors ${
                    isActive ? "text-oxblood bg-oxblood/10" : "text-ink-muted hover:text-ink hover:bg-sunken"
                  }`
                }
              >
                <CircleUser size={22} strokeWidth={2} />
              </NavLink>
            )}
            <button
              onClick={() => setOpen((v) => !v)}
              className="inline-flex p-2 rounded-lg border border-edge text-ink hover:bg-sunken transition-colors"
              aria-label="Meniu"
              aria-expanded={open}
            >
              {open ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {open && (
          <div className="md:hidden border-t border-edge bg-paper px-6 py-3 flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                onClick={() => setOpen(false)}
                className={({ isActive }) => navLinkClass(isActive)}
              >
                {item.label}
              </NavLink>
            ))}
            <div className="my-1 h-px bg-edge" />
            {user ? (
              <>
                {user.is_staff && (
                  <NavLink
                    to="/admin"
                    onClick={() => setOpen(false)}
                    className={({ isActive }) => navLinkClass(isActive)}
                  >
                    Administrare
                  </NavLink>
                )}
                <button
                  onClick={() => {
                    logout();
                    setOpen(false);
                    navigate("/");
                  }}
                  className="text-left px-3 py-2 rounded-lg text-sm font-medium text-ink hover:bg-sunken transition-colors"
                >
                  Ieșire
                </button>
              </>
            ) : (
              <>
                <NavLink
                  to="/login"
                  onClick={() => setOpen(false)}
                  className="px-3 py-2 rounded-lg text-sm font-medium text-ink hover:bg-sunken transition-colors"
                >
                  Autentificare
                </NavLink>
                <NavLink
                  to="/register"
                  onClick={() => setOpen(false)}
                  className="px-3 py-2 rounded-lg bg-oxblood text-paper text-sm font-semibold hover:bg-oxblood-deep transition-colors"
                >
                  Înregistrare
                </NavLink>
              </>
            )}
          </div>
        )}
      </header>

      <main className="flex-grow">{children}</main>

      {!fullBleed && (
      <footer className="mt-auto border-t border-edge bg-paper">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col items-center gap-2 text-center">
          <div className="flex items-center gap-2 text-oxblood">
            <Calculator size={18} strokeWidth={2.25} />
            <span className="font-bold text-ink-strong">Algomate</span>
          </div>
          <p className="text-sm text-ink-muted">
            © {new Date().getFullYear()} Algomate. Platformă educațională de matematică pentru BAC.
          </p>
          <nav className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-sm text-ink-muted">
            <Link to="/termeni" className="hover:text-oxblood transition-colors">
              Termeni și Condiții
            </Link>
            <span className="text-edge" aria-hidden>·</span>
            <Link to="/confidentialitate" className="hover:text-oxblood transition-colors">
              Confidențialitate
            </Link>
            <span className="text-edge" aria-hidden>·</span>
            <Link to="/cookies" className="hover:text-oxblood transition-colors">
              Cookies
            </Link>
          </nav>
        </div>
      </footer>
      )}
    </div>
  );
}
