import React, { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import "./styles.css";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("provider_app_token") || "");
  const [sessionUser, setSessionUser] = useState(null);
  const [forms, setForms] = useState([]);
  const [providers, setProviders] = useState([]);
  const [newProviderName, setNewProviderName] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("app");
  const [consultProviderId, setConsultProviderId] = useState("");
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const groupedByProvider = useMemo(() => {
    const grouped = new Map();
    forms.forEach((form) => {
      const key = String(form.provider);
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(form);
    });
    return grouped;
  }, [forms]);
  const isProviderAdmin = (sessionUser?.profiles || []).some(
    (profile) =>
      profile.appScope === "provider-app" &&
      profile.role === "provider-admin"
  );

  const loadAppData = async (authToken) => {
    const tokenToUse = authToken || token;
    const formsData = await api.forms(tokenToUse);
    setForms(formsData);
    if (isProviderAdmin) {
      const providersData = await api.adminProviders(tokenToUse);
      setProviders(providersData);
    } else {
      const ids = Array.from(new Set(formsData.map((item) => item.provider)));
      setProviders(ids.map((id) => ({ id, name: `Provider #${id}` })));
    }
  };

  useEffect(() => {
    if (!token || mode !== "app") return;
    setLoading(true);
    api
      .session(token)
      .then((user) => {
        setSessionUser(user);
        setError(null);
      })
      .catch((e) => {
        localStorage.removeItem("provider_app_token");
        setToken("");
        setSessionUser(null);
        setError(`Session error: ${e.message}`);
      })
      .finally(() => setLoading(false));
  }, [token, mode]);

  useEffect(() => {
    if (mode !== "app" || !token) return;
    setLoading(true);
    loadAppData(token)
      .then(() => setError(null))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [mode, token, isProviderAdmin]);

  const doLogin = async () => {
    setLoading(true);
    try {
      const payload = await api.login(loginUsername, loginPassword);
      localStorage.setItem("provider_app_token", payload.accessToken);
      setToken(payload.accessToken);
      setSessionUser(payload.user);
      setError(null);
      setLoginPassword("");
      await loadAppData(payload.accessToken);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadConsultation = async () => {
    if (!consultProviderId) return;
    setLoading(true);
    try {
      const data = await api.publicFormsByProvider(consultProviderId);
      setForms(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("provider_app_token");
    setToken("");
    setSessionUser(null);
    setForms([]);
    setProviders([]);
    setError(null);
  };

  const createProvider = async () => {
    const name = newProviderName.trim();
    if (!name) return;
    setLoading(true);
    try {
      await api.createProvider({ name }, token);
      setNewProviderName("");
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const updateProvider = async (provider) => {
    const nextName = window.prompt("Provider name", provider.name || "");
    if (!nextName || nextName === provider.name) return;
    setLoading(true);
    try {
      await api.updateProvider(provider.id, { name: nextName }, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteProvider = async (provider) => {
    if (!window.confirm(`Delete provider "${provider.name}" and all forms/questions?`)) return;
    setLoading(true);
    try {
      await api.deleteProvider(provider.id, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const createForm = async (providerId) => {
    const name = window.prompt("Form name");
    if (!name) return;
    const description = window.prompt("Form description (optional)", "") || "";
    setLoading(true);
    try {
      await api.createForm({ provider: providerId, name, description }, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const updateForm = async (form) => {
    const name = window.prompt("Form name", form.name || "");
    if (!name) return;
    const description = window.prompt("Form description", form.description || "") || "";
    setLoading(true);
    try {
      await api.updateForm(form.id, { name, description }, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteForm = async (form) => {
    if (!window.confirm(`Delete form "${form.name}"?`)) return;
    setLoading(true);
    try {
      await api.deleteForm(form.id, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const createQuestion = async (formId) => {
    const label = window.prompt("Question label");
    if (!label) return;
    const answer = window.prompt("Answer (optional)", "") || "";
    const isPublic = window.confirm("Should this question be public?");
    const orderRaw = window.prompt("Order", "0") || "0";
    const order = Number(orderRaw) || 0;
    setLoading(true);
    try {
      await api.createQuestion(
        { form: formId, label, answer, is_public: isPublic, order },
        token
      );
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const updateQuestion = async (question) => {
    const label = window.prompt("Question label", question.label || "");
    if (!label) return;
    const answer = window.prompt("Answer", question.answer || "") || "";
    const isPublic = window.confirm("Mark as public?");
    const orderRaw = window.prompt("Order", String(question.order ?? 0)) || "0";
    const order = Number(orderRaw) || 0;
    setLoading(true);
    try {
      await api.updateQuestion(
        question.id,
        { label, answer, is_public: isPublic, order },
        token
      );
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const updateQuestionAnswer = async (question) => {
    const nextAnswer = window.prompt("Answer", question.answer || "");
    if (nextAnswer === null) return;
    setLoading(true);
    try {
      await api.updateQuestionAnswer(question.id, nextAnswer, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteQuestion = async (question) => {
    if (!window.confirm(`Delete question "${question.label}"?`)) return;
    setLoading(true);
    try {
      await api.deleteQuestion(question.id, token);
      await loadAppData();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="provider-app">
      <header>
        <h1>provider-app</h1>
        <div className="row">
          <label htmlFor="mode">Mode</label>
          <select
            id="mode"
            value={mode}
            onChange={(e) => {
              setMode(e.target.value);
              setForms([]);
              setError(null);
            }}
          >
            <option value="app">App mode (provider users/admin)</option>
            <option value="consultation">Consultation mode (third-party, view-only)</option>
          </select>
        </div>
      </header>

      <main>
        {error ? <p className="error">Error: {error}</p> : null}

        {mode === "app" ? (
          <>
            {!token || !sessionUser ? (
              <section>
                <h2>Sign in</h2>
                <p>
                  <label htmlFor="username">Username</label>
                  <input id="username" value={loginUsername} onChange={(e) => setLoginUsername(e.target.value)} />
                </p>
                <p>
                  <label htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                  />
                </p>
                <button onClick={doLogin} disabled={loading}>
                  {loading ? "Signing in..." : "Sign in"}
                </button>
              </section>
            ) : (
              <section>
                <div className="row">
                  <strong>Signed in as {sessionUser.username}</strong>
                  <button onClick={logout}>Logout</button>
                </div>
                <p className="hint">App mode shows all questions (public and private).</p>
                {isProviderAdmin ? (
                  <section className="card">
                    <h2>Provider administration</h2>
                    <p className="hint">
                      Create and manage providers, forms, and questions.
                    </p>
                    <div className="row">
                      <input
                        placeholder="New provider name"
                        value={newProviderName}
                        onChange={(e) => setNewProviderName(e.target.value)}
                      />
                      <button onClick={createProvider} disabled={loading || !newProviderName.trim()}>
                        Create provider
                      </button>
                    </div>
                  </section>
                ) : null}
                {loading ? (
                  <p>Loading forms...</p>
                ) : (
                  <FormsList
                    formsByProvider={groupedByProvider}
                    providers={providers}
                    isProviderAdmin={isProviderAdmin}
                    onUpdateProvider={updateProvider}
                    onDeleteProvider={deleteProvider}
                    onCreateForm={createForm}
                    onUpdateForm={updateForm}
                    onDeleteForm={deleteForm}
                    onCreateQuestion={createQuestion}
                    onUpdateQuestion={updateQuestion}
                    onDeleteQuestion={deleteQuestion}
                    onUpdateQuestionAnswer={updateQuestionAnswer}
                  />
                )}
              </section>
            )}
          </>
        ) : (
          <section>
            <h2>Consultation (view-only)</h2>
            <p className="hint">
              This mode calls the third surface and only displays public questions.
            </p>
            <div className="row">
              <input
                placeholder="Provider ID"
                value={consultProviderId}
                onChange={(e) => setConsultProviderId(e.target.value)}
              />
              <button onClick={loadConsultation} disabled={loading || !consultProviderId}>
                {loading ? "Loading..." : "Load public data"}
              </button>
            </div>
            <FormsList formsByProvider={groupedByProvider} />
          </section>
        )}
      </main>
    </div>
  );
}

function FormsList({
  formsByProvider,
  providers,
  isProviderAdmin,
  onUpdateProvider,
  onDeleteProvider,
  onCreateForm,
  onUpdateForm,
  onDeleteForm,
  onCreateQuestion,
  onUpdateQuestion,
  onDeleteQuestion,
  onUpdateQuestionAnswer,
}) {
  if (!formsByProvider.size) {
    return <p className="hint">No forms loaded.</p>;
  }

  const providerList = providers.length
    ? providers
    : Array.from(formsByProvider.keys()).map((id) => ({ id, name: `Provider #${id}` }));

  return (
    <>
      {providerList.map((provider) => {
        const providerId = String(provider.id);
        const providerForms = formsByProvider.get(providerId) || [];
        return (
        <section key={providerId} className="card">
          <div className="row">
            <h3>
              {provider.name || `Provider #${providerId}`} (#{providerId})
            </h3>
            {isProviderAdmin ? (
              <>
                <button onClick={() => onUpdateProvider(provider)}>Rename provider</button>
                <button className="danger" onClick={() => onDeleteProvider(provider)}>
                  Delete provider
                </button>
                <button onClick={() => onCreateForm(Number(providerId))}>Add form</button>
              </>
            ) : null}
          </div>
          {providerForms.length === 0 ? <p className="hint">No forms for this provider.</p> : null}
          {providerForms.map((form) => (
            <article key={form.id} className="form-card">
              <div className="row">
                <h4>{form.name}</h4>
                {isProviderAdmin ? (
                  <>
                    <button onClick={() => onUpdateForm(form)}>Edit form</button>
                    <button className="danger" onClick={() => onDeleteForm(form)}>
                      Delete form
                    </button>
                    <button onClick={() => onCreateQuestion(form.id)}>Add question</button>
                  </>
                ) : null}
              </div>
              <p>{form.description || "(no description)"}</p>
              {form.questions.length === 0 ? (
                <p className="hint">No questions.</p>
              ) : (
                <ul>
                  {form.questions.map((q) => (
                    <li key={q.id}>
                      <strong>{q.label}</strong>: {q.answer || "(empty)"}{" "}
                      {"is_public" in q ? (
                        <span className={q.is_public ? "public" : "private"}>
                          [{q.is_public ? "public" : "private"}]
                        </span>
                      ) : null}
                      {isProviderAdmin ? (
                        <>
                          {" "}
                          <button onClick={() => onUpdateQuestion(q)}>Edit</button>
                          <button className="danger" onClick={() => onDeleteQuestion(q)}>
                            Delete
                          </button>
                        </>
                      ) : (
                        <button onClick={() => onUpdateQuestionAnswer(q)}>Update answer</button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </section>
      )})}
    </>
  );
}
