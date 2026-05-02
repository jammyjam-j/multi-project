import { login, readRoleFromToken, register as registerApi } from "./api.js";
import { clearAuth, getAuth, getCartCount, saveAuth } from "./store.js";
import { renderAdmin } from "./views/admin.js";
import { renderCart } from "./views/cart.js";
import { renderCatalog } from "./views/catalog.js";
import { renderLogin } from "./views/login.js";
import { renderRegister } from "./views/register.js";
import { renderOrders } from "./views/orders.js";
import { renderProductDetailPage } from "./views/product-detail.js";

const root = document.getElementById("app");
const nav = document.getElementById("topbar-actions");

const STATIC_ROUTES = new Set(["#/catalog", "#/login", "#/register", "#/cart", "#/orders", "#/admin"]);

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function showFatalError(message) {
  if (!root) {
    console.error(message);
    return;
  }
  root.innerHTML = `
    <section class="section-card">
      <p class="message error">${escapeHtml(String(message))}</p>
    </section>
  `;
}

function isCustomerLike(role) {
  return role === "customer" || role === "user";
}

function resolveRoute(hash) {
  let h = hash || "#/catalog";
  if (h === "#") h = "#/catalog";
  if (!h.startsWith("#/")) h = "#/catalog";

  const prod = /^#\/product\/(\d+)$/.exec(h);
  if (prod) {
    return { mode: "product", productId: Number.parseInt(prod[1], 10) };
  }
  return { mode: "static", route: STATIC_ROUTES.has(h) ? h : "#/catalog" };
}

function navHighlight(hash) {
  const r = resolveRoute(hash);
  return r.mode === "product" ? "#/catalog" : r.route;
}

function routeNeedsFreshAuth(route) {
  return route === "#/orders" || route === "#/admin";
}

function renderNav() {
  if (!nav || !root) {
    return;
  }
  const auth = getAuth();
  const cartCount = getCartCount();
  const active = navHighlight(window.location.hash);

  const links = [
    { href: "#/catalog", label: "Catalog", show: true },
    { href: "#/cart", label: `Cart (${cartCount})`, show: true },
    { href: "#/orders", label: "My Orders", show: isCustomerLike(auth.role) },
    { href: "#/admin", label: "Admin", show: auth.role === "admin" },
    { href: "#/register", label: "Register", show: !auth.token },
  ].filter((item) => item.show);

  nav.innerHTML = `
    ${links
      .map(
        (link) => `
          <a class="nav-link ${active === link.href ? "active" : ""}" href="${link.href}">${escapeHtml(link.label)}</a>
        `,
      )
      .join("")}
    ${
      auth.token
        ? `
          <span class="chip">Signed in as ${escapeHtml(auth.username || auth.role)}</span>
          <button class="nav-button" id="logout-button" type="button">Logout</button>
        `
        : '<a class="nav-button" href="#/login">Login</a>'
    }
  `;

  const logoutButton = nav.querySelector("#logout-button");
  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      clearAuth();
      renderNav();
      window.location.hash = "#/catalog";
    });
  }
}

async function handleLogin(credentials) {
  const result = await login(credentials.username, credentials.password);
  const role = readRoleFromToken(result.token);

  saveAuth({
    token: result.token,
    role,
    username: credentials.username,
  });

  renderNav();
  window.location.hash = role === "admin" ? "#/admin" : "#/catalog";
}

async function handleRegister(credentials) {
  const result = await registerApi(credentials.username, credentials.password);
  const role = readRoleFromToken(result.token);

  saveAuth({
    token: result.token,
    role,
    username: credentials.username,
  });

  renderNav();
  window.location.hash = "#/catalog";
}

async function renderRoute() {
  if (!nav || !root) {
    console.error("#app or #topbar-actions missing — check index.html.");
    return;
  }

  const auth = getAuth();
  let hash = window.location.hash;
  if (!hash || hash === "#") {
    history.replaceState(null, "", "#/catalog");
    hash = "#/catalog";
  }

  const resolved = resolveRoute(hash);

  try {
    renderNav();

    if (resolved.mode === "static" && resolved.route === "#/admin" && auth.role !== "admin") {
      root.innerHTML = `
      <section class="section-card">
        <p class="message error">Admin access is required for that route.</p>
      </section>
    `;
      return;
    }

    if (resolved.mode === "product") {
      await renderProductDetailPage(root, {
        productId: resolved.productId,
        onCartChange: () => {
          renderNav();
        },
      });
      return;
    }

    switch (resolved.route) {
      case "#/login":
        renderLogin(root, {
          auth,
          onLogin: handleLogin,
        });
        break;
      case "#/register":
        renderRegister(root, {
          auth,
          onRegisterSuccess: handleRegister,
        });
        break;
      case "#/cart":
        renderCart(root, {
          auth,
          navigate: (nextRoute) => {
            window.location.hash = nextRoute;
          },
          onCartChange: () => {
            renderNav();
          },
        });
        break;
      case "#/orders":
        await renderOrders(root, { auth });
        break;
      case "#/admin":
        await renderAdmin(root, { auth });
        break;
      default:
        await renderCatalog(root, {
          onCartChange: () => {
            renderNav();
          },
        });
        break;
    }
  } catch (error) {
    console.error(error);
    showFatalError(error.message || String(error));
  }
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("storage", renderRoute);
window.addEventListener("auth:invalid", () => {
  const r = resolveRoute(window.location.hash);
  const route = r.mode === "static" ? r.route : "#/catalog";

  if (routeNeedsFreshAuth(route)) {
    window.location.hash = "#/login";
    return;
  }

  renderRoute();
});

renderRoute();
