"use strict";

const API_BASE = "/api/v1";
const TOKEN_KEY = "cms_token";

const sections = {
  login: document.getElementById("login-section"),
  projects: document.getElementById("projects-section"),
  detail: document.getElementById("project-detail-section"),
};
const alertArea = document.getElementById("alert-area");

function show(sectionName) {
  Object.values(sections).forEach((s) => s.classList.add("d-none"));
  sections[sectionName].classList.remove("d-none");
}

function setNavAuthenticated(auth) {
  document.getElementById("nav-login").classList.toggle("d-none", auth);
  document.getElementById("nav-projects").classList.toggle("d-none", !auth);
  document.getElementById("nav-logout").classList.toggle("d-none", !auth);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Token ${token}`;
  return headers;
}

function showAlert(message, type = "danger") {
  alertArea.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${escapeHtml(String(message))}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
}

function clearAlert() {
  alertArea.innerHTML = "";
}

function formatError(data, status) {
  if (!data) return `Request failed (${status}).`;
  if (typeof data === "string") return data;
  if (data.detail) return String(data.detail);

  const parts = [];
  Object.entries(data).forEach(([field, value]) => {
    const text = Array.isArray(value) ? value.join(" ") : value;
    parts.push(`${field}: ${text}`);
  });
  return parts.length ? parts.join("\n") : `Request failed (${status}).`;
}

async function request(path, options = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: { ...authHeaders(), ...options.headers },
  });

  if (res.status === 401) {
    clearToken();
    setNavAuthenticated(false);
    show("login");
    showAlert("Session expired or invalid token. Please sign in again.", "warning");
    return null;
  }

  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) data = await res.json();

  if (!res.ok) {
    throw formatError(data, res.status);
  }

  return data;
}

async function login(username, password) {
  const data = await request("/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (data && data.token) {
    setToken(data.token);
    setNavAuthenticated(true);
    show("projects");
    showAlert("Signed in successfully.", "success");
    await loadProjects();
  }
  return data;
}

async function loadProjects() {
  clearAlert();
  const projects = await request("/projects/");
  if (!projects) return;

  renderProjects(projects);
}

async function loadPage(url) {
  clearAlert();
  const data = await request(url);
  if (!data) return;

  renderProjects(data);
}

function renderProjects(data) {
  const list = document.getElementById("projects-list");
  const pagination = document.getElementById("projects-pagination");
  const results = data.results || [];

  if (results.length === 0) {
    list.innerHTML = `<p class="text-center p-3 text-muted">No projects found.</p>`;
    pagination.innerHTML = "";
    pagination.classList.add("d-none");
    return;
  }

  list.innerHTML = `
    <table class="table table-hover mb-0">
      <thead>
        <tr>
          <th>Name</th>
          <th>Owner</th>
          <th>Created at</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        ${results
          .map(
            (p) => `
            <tr>
              <td>${escapeHtml(p.name)}</td>
              <td>${escapeHtml(p.owner_username || p.owner)}</td>
              <td>${escapeHtml(p.created_at)}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary" data-project-id="${p.id}">Open</button>
                <button class="btn btn-sm btn-outline-danger" data-delete-project-id="${p.id}">Delete</button>
              </td>
            </tr>
          `
          )
          .join("")}
      </tbody>
    </table>
  `;

  const hasPages = Boolean(data.next || data.previous);
  pagination.classList.toggle("d-none", !hasPages);
  pagination.innerHTML = hasPages
    ? `<div class="d-flex justify-content-between">
        ${data.previous ? `<button class="btn btn-sm btn-outline-secondary" data-url="${data.previous}">Previous</button>` : "<span></span>"}
        ${data.next ? `<button class="btn btn-sm btn-outline-secondary" data-url="${data.next}">Next</button>` : "<span></span>"}
      </div>`
    : "";
}

async function createProject(name) {
  clearAlert();
  await request("/projects/", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  document.getElementById("create-project-form").reset();
  document.getElementById("create-project-section").classList.add("d-none");
  await loadProjects();
}

async function deleteProject(id) {
  if (!confirm("Delete this project and all its assets?")) return;
  clearAlert();
  await request(`/projects/${id}/`, { method: "DELETE" });
  show("projects");
  await loadProjects();
  showAlert("Project deleted.", "success");
}

async function openProject(id) {
  clearAlert();
  const project = await request(`/projects/${id}/`);
  if (!project) return;

  document.getElementById("detail-project-name").textContent = project.name;
  document.getElementById("detail-name").value = project.name;
  document.getElementById("detail-owner").value =
    project.owner_username || project.owner;
  document.getElementById("detail-created").value = project.created_at;
  document.getElementById("create-asset-form").dataset.projectId = id;
  document.getElementById("btn-delete-project").dataset.projectId = id;
  document.getElementById("assets-list").innerHTML = `<p class="text-center p-3">Loading assets...</p>`;

  show("detail");
  await loadAssets(id);
}

async function loadAssets(projectId, url = null) {
  const assets = await request(url || `/projects/${projectId}/assets/`);
  if (!assets) return;

  const list = document.getElementById("assets-list");
  const pagination = document.getElementById("assets-pagination");
  const results = assets.results || [];

  if (results.length === 0) {
    list.innerHTML = `<p class="text-muted text-center p-3">No assets yet.</p>`;
    pagination.innerHTML = "";
    return;
  }

  const rows = results
    .map(
      (a) => `
      <tr>
        <td>${escapeHtml(a.name)}</td>
        <td>${escapeHtml(a.asset_type)}</td>
        <td>${a.is_public ? '<span class="badge bg-success">Public</span>' : '<span class="badge bg-secondary">Private</span>'}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-danger" data-delete-asset-id="${a.id}">Delete</button>
        </td>
      </tr>
    `
    )
    .join("");

  list.innerHTML = `
    <table class="table table-sm table-hover mb-0">
      <thead><tr><th>Name</th><th>Type</th><th>Visibility</th><th></th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;

  const hasPages = Boolean(assets.next || assets.previous);
  pagination.innerHTML = hasPages
    ? `<div class="d-flex justify-content-between">
        ${assets.previous ? `<button class="btn btn-sm btn-outline-secondary" data-asset-url="${assets.previous}">Previous</button>` : "<span></span>"}
        ${assets.next ? `<button class="btn btn-sm btn-outline-secondary" data-asset-url="${assets.next}">Next</button>` : "<span></span>"}
      </div>`
    : "";
}

async function createAsset(formData) {
  const projectId = document.getElementById("create-asset-form").dataset.projectId;
  clearAlert();
  const body = {
    name: formData.get("name"),
    asset_type: formData.get("asset_type"),
    is_public: formData.get("is_public") === "on",
  };
  await request(`/projects/${projectId}/assets/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  document.getElementById("create-asset-form").reset();
  await loadAssets(projectId);
}

async function deleteAsset(projectId, assetId) {
  if (!confirm("Delete this asset?")) return;
  clearAlert();
  await request(`/projects/${projectId}/assets/${assetId}/`, {
    method: "DELETE",
  });
  await loadAssets(projectId);
  showAlert("Asset deleted.", "success");
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

const app = {
  openProject,
  loadPage,
};

// ---------------- Event listeners ----------------
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await login(fd.get("username"), fd.get("password"));
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("projects-list").addEventListener("click", async (e) => {
  const deleteButton = e.target.closest("button[data-delete-project-id]");
  if (deleteButton) {
    try {
      await deleteProject(Number(deleteButton.dataset.deleteProjectId));
    } catch (err) {
      showAlert(String(err));
    }
    return;
  }

  const button = e.target.closest("button[data-project-id]");
  if (!button) return;
  try {
    await openProject(Number(button.dataset.projectId));
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("assets-list").addEventListener("click", async (e) => {
  const button = e.target.closest("button[data-delete-asset-id]");
  if (!button) return;
  const projectId = Number(
    document.getElementById("create-asset-form").dataset.projectId
  );
  try {
    await deleteAsset(projectId, Number(button.dataset.deleteAssetId));
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("projects-pagination").addEventListener("click", async (e) => {
  const button = e.target.closest("button[data-url]");
  if (!button) return;
  try {
    await loadPage(button.dataset.url);
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("assets-pagination").addEventListener("click", async (e) => {
  const button = e.target.closest("button[data-asset-url]");
  if (!button) return;
  const projectId = Number(
    document.getElementById("create-asset-form").dataset.projectId
  );
  try {
    await loadAssets(projectId, button.dataset.assetUrl);
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("nav-logout").addEventListener("click", (e) => {
  e.preventDefault();
  clearToken();
  setNavAuthenticated(false);
  show("login");
  showAlert("Signed out.", "info");
});

document.getElementById("nav-projects").addEventListener("click", async (e) => {
  e.preventDefault();
  show("projects");
  try {
    await loadProjects();
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("btn-new-project").addEventListener("click", () => {
  document.getElementById("create-project-section").classList.toggle("d-none");
});

document.getElementById("btn-cancel-project").addEventListener("click", () => {
  document.getElementById("create-project-section").classList.add("d-none");
});

document.getElementById("create-project-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await createProject(fd.get("name"));
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("btn-delete-project").addEventListener("click", async (e) => {
  const projectId = Number(e.currentTarget.dataset.projectId);
  try {
    await deleteProject(projectId);
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("btn-back-to-list").addEventListener("click", async (e) => {
  e.preventDefault();
  show("projects");
  try {
    await loadProjects();
  } catch (err) {
    showAlert(String(err));
  }
});

document.getElementById("create-asset-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await createAsset(fd);
  } catch (err) {
    showAlert(String(err));
  }
});

// ---------------- Boot ----------------
(function init() {
  setNavAuthenticated(Boolean(getToken()));
  if (getToken()) {
    show("projects");
    loadProjects().catch((err) => showAlert(String(err)));
  } else {
    show("login");
  }
})();
