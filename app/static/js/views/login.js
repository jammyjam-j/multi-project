function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function isCustomerLike(role) {
  return role === "customer" || role === "user";
}

export function renderLogin(root, options) {
  const { auth, onLogin } = options;

  if (auth.token) {
    root.innerHTML = `
      <section class="section-card">
        <p class="eyebrow">Session</p>
        <h2>You are already signed in</h2>
        <p class="muted">Current role: <strong>${escapeHtml(auth.role || "unknown")}</strong></p>
        <div class="inline-actions">
          <a class="button button-primary" href="#/catalog">Go to catalog</a>
          ${
            auth.role === "admin"
              ? '<a class="button button-secondary" href="#/admin">Open admin dashboard</a>'
              : isCustomerLike(auth.role)
                ? '<a class="button button-secondary" href="#/orders">View my orders</a>'
                : ""
          }
        </div>
      </section>
    `;
    return;
  }

  root.innerHTML = `
    <section class="hero-slab">
      <div class="section-card">
        <p class="eyebrow">Lab Access</p>
        <h2>Sign in for checkout and admin tools</h2>
        <p class="muted">This store runs as a small single-page frontend on top of the class API. Login is only needed for orders and management screens.</p>
        <form id="login-form" class="stack">
          <div id="login-message"></div>
          <div class="form-grid single">
            <div class="field">
              <label for="username">Username</label>
              <input id="username" name="username" autocomplete="username" placeholder="customer1">
            </div>
            <div class="field">
              <label for="password">Password</label>
              <input id="password" name="password" type="password" autocomplete="current-password" placeholder="customer123">
            </div>
          </div>
          <div class="form-actions">
            <button class="button button-primary" type="submit">Login</button>
            <a class="button button-secondary" href="#/catalog">Browse catalog first</a>
            <a class="button button-secondary" href="#/register">Create an account</a>
          </div>
        </form>
      </div>
      <aside class="hero-note">
        <p><strong>Demo accounts</strong></p>
        <p><code>customer1 / customer123</code> for shopping flow.</p>
        <p><code>editor / editor123</code> follows the backend <code>user</code> role and uses the same order flow as customer.</p>
        <p><code>admin / admin123</code> for order review and catalog management.</p>
        <p><code>viewer / viewer123</code> to confirm restricted access messaging.</p>
      </aside>
    </section>
  `;

  const form = root.querySelector("#login-form");
  const message = root.querySelector("#login-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const username = String(formData.get("username") || "").trim();
    const password = String(formData.get("password") || "").trim();

    message.innerHTML = "";

    if (!username || !password) {
      message.innerHTML = '<p class="message error">Enter both username and password.</p>';
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "Checking...";

    try {
      await onLogin({ username, password });
    } catch (error) {
      message.innerHTML = `<p class="message error">${escapeHtml(error.message)}</p>`;
      submitButton.disabled = false;
      submitButton.textContent = "Login";
    }
  });
}
