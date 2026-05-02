function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function renderRegister(root, options) {
  const { auth, onRegisterSuccess } = options;

  if (auth.token) {
    root.innerHTML = `
      <section class="section-card">
        <p class="eyebrow">Session</p>
        <h2>You are already signed in</h2>
        <p class="muted">Sign out before creating another account.</p>
        <div class="inline-actions">
          <a class="button button-primary" href="#/catalog">Go to catalog</a>
          <a class="button button-secondary" href="#/login">Open login</a>
        </div>
      </section>
    `;
    return;
  }

  root.innerHTML = `
    <section class="hero-slab">
      <div class="section-card">
        <p class="eyebrow">New shopper</p>
        <h2>Create an account</h2>
        <p class="muted">Registers a <strong>customer</strong> account so you can check out and view order history.</p>
        <form id="register-form" class="stack">
          <div id="register-message"></div>
          <div class="form-grid single">
            <div class="field">
              <label for="register-username">Username</label>
              <input id="register-username" name="username" autocomplete="username" placeholder="my_username" maxlength="80">
            </div>
            <div class="field">
              <label for="register-password">Password</label>
              <input id="register-password" name="password" type="password" autocomplete="new-password" placeholder="At least 6 characters">
            </div>
            <div class="field">
              <label for="register-password2">Confirm password</label>
              <input id="register-password2" name="password2" type="password" autocomplete="new-password">
            </div>
          </div>
          <div class="form-actions">
            <button class="button button-primary" type="submit">Register</button>
            <a class="button button-secondary" href="#/login">Back to login</a>
          </div>
        </form>
      </div>
      <aside class="hero-note">
        <p><strong>Username rules</strong></p>
        <p>Use 3–80 characters: letters, numbers, and underscores only.</p>
        <p>To manage the catalog or all orders you need an <code>admin</code> account (seeded separately).</p>
      </aside>
    </section>
  `;

  const form = root.querySelector("#register-form");
  const message = root.querySelector("#register-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const username = String(formData.get("username") || "").trim();
    const password = String(formData.get("password") || "");
    const password2 = String(formData.get("password2") || "");

    message.innerHTML = "";

    if (!username || !password) {
      message.innerHTML = '<p class="message error">Username and password are required.</p>';
      return;
    }

    if (password !== password2) {
      message.innerHTML = '<p class="message error">Passwords do not match.</p>';
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "Creating account…";

    try {
      await onRegisterSuccess({ username, password });
    } catch (error) {
      message.innerHTML = `<p class="message error">${escapeHtml(error.message)}</p>`;
      submitButton.disabled = false;
      submitButton.textContent = "Register";
    }
  });
}
