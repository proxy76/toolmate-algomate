import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { api, apiErrorMessage } from "../api";

type State = { status: "loading" } | { status: "ok" | "error"; message: string };

export function Verify() {
  const [params] = useSearchParams();
  const token = params.get("token");
  const [state, setState] = useState<State>({ status: "loading" });
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return; // guard React 18 StrictMode double-invoke
    ran.current = true;
    if (!token) {
      setState({ status: "error", message: "Link invalid: lipsește tokenul." });
      return;
    }
    api
      .verifyEmail(token)
      .then((res) => setState({ status: "ok", message: res.detail }))
      .catch((err) => setState({ status: "error", message: apiErrorMessage(err) }));
  }, [token]);

  return (
    <div className="max-w-md mx-auto px-6 py-16 md:py-24 text-center">
      {state.status === "loading" && (
        <>
          <Loader2 size={36} className="mx-auto animate-spin text-ink-muted" />
          <p className="mt-4 text-ink-muted">Se confirmă adresa…</p>
        </>
      )}

      {state.status === "ok" && (
        <>
          <CheckCircle2 size={44} className="mx-auto text-oxblood" strokeWidth={1.75} />
          <h1 className="mt-5 text-2xl font-extrabold tracking-tight text-ink-strong">
            Adresă confirmată
          </h1>
          <p className="mt-3 text-ink-muted">{state.message}</p>
          <Link
            to="/login"
            className="mt-6 inline-flex items-center justify-center py-3 px-6 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition"
          >
            Conectează-te
          </Link>
        </>
      )}

      {state.status === "error" && (
        <>
          <XCircle size={44} className="mx-auto text-danger-ink" strokeWidth={1.75} />
          <h1 className="mt-5 text-2xl font-extrabold tracking-tight text-ink-strong">
            Confirmarea a eșuat
          </h1>
          <p className="mt-3 text-ink-muted">{state.message}</p>
          <Link to="/login" className="mt-6 inline-block text-oxblood font-semibold hover:underline">
            Înapoi la autentificare
          </Link>
        </>
      )}
    </div>
  );
}
