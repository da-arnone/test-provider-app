async function request(path, options = {}) {
  const { token, ...fetchOptions } = options;
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(fetchOptions.headers || {}),
    },
    ...fetchOptions,
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`${response.status} ${response.statusText}${detail ? ` - ${detail}` : ""}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  login: (username, password) =>
    request("/api/provider/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  session: (token) => request("/api/provider/auth/session/", { token }),
  forms: (token) => request("/api/provider/forms/", { token }),
  incomingSubmissions: (token) => request("/api/provider/subscriptions/incoming/", { token }),
  decideIncomingSubmission: (id, body, token) =>
    request(`/api/provider/subscriptions/incoming/${id}/decision/`, {
      method: "POST",
      token,
      body: JSON.stringify(body),
    }),
  updateQuestionAnswer: (id, answer, token) =>
    request(`/api/provider/questions/${id}/answer/`, {
      method: "PATCH",
      token,
      body: JSON.stringify({ answer }),
    }),
  adminProviders: (token) => request("/admin/provider/providers/", { token }),
  createProvider: (body, token) =>
    request("/admin/provider/providers/", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    }),
  updateProvider: (id, body, token) =>
    request(`/admin/provider/providers/${id}/`, {
      method: "PATCH",
      token,
      body: JSON.stringify(body),
    }),
  deleteProvider: (id, token) =>
    request(`/admin/provider/providers/${id}/`, {
      method: "DELETE",
      token,
    }),
  createForm: (body, token) =>
    request("/admin/provider/forms/", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    }),
  updateForm: (id, body, token) =>
    request(`/admin/provider/forms/${id}/`, {
      method: "PATCH",
      token,
      body: JSON.stringify(body),
    }),
  deleteForm: (id, token) =>
    request(`/admin/provider/forms/${id}/`, {
      method: "DELETE",
      token,
    }),
  createQuestion: (body, token) =>
    request("/admin/provider/questions/", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    }),
  updateQuestion: (id, body, token) =>
    request(`/admin/provider/questions/${id}/`, {
      method: "PATCH",
      token,
      body: JSON.stringify(body),
    }),
  deleteQuestion: (id, token) =>
    request(`/admin/provider/questions/${id}/`, {
      method: "DELETE",
      token,
    }),
  publicFormsByProvider: (providerId, token) =>
    request(`/api/provider/consultation/providers/${providerId}/forms/`, { token }),
};
