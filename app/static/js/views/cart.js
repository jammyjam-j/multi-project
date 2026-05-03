import { createOrder } from "../api.js";
import { clearCart, getCart, getCartTotal, removeFromCart, updateCartItem } from "../store.js";
import { escapeHtml } from "../utils.js";

// Note: cart lives in localStorage so it survives page refreshes.
// If the user clears browser data, orders are lost — not ideal but fine for demo.
export function renderCart(root, options) {
  const { auth, onCartChange, navigate } = options;
  let cart = getCart();
  let message = "";
  let messageType = "info";

  function paint() {
    cart = getCart();
    const total = getCartTotal();

    if (!cart.length) {
      root.innerHTML = `
        <section class="section-card">
          <p class="eyebrow">Cart</p>
          <h2>Your cart is empty</h2>
          <p class="muted">Add something from the catalog before checking out.</p>
          <div class="inline-actions">
            <a class="button button-primary" href="#/catalog">Go to catalog</a>
          </div>
        </section>
      `;
      return;
    }

    root.innerHTML = `
      <section class="split">
        <div class="section-card">
          <div class="section-header">
            <div>
              <p class="eyebrow">Checkout Prep</p>
              <h2>Cart</h2>
              <p>Quantities stay in localStorage until you clear them or place an order.</p>
            </div>
          </div>
          ${message ? `<p class="message ${messageType}">${escapeHtml(message)}</p>` : ""}
          <div class="cart-list">
            ${cart
              .map(
                (item) => `
                  <article class="order-card">
                    <div class="section-header">
                      <div>
                        <h3>${escapeHtml(item.name)}</h3>
                        <div class="line-meta">
                          <span>$${Number(item.price).toFixed(2)} each</span>
                          <span>Line total $${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                      </div>
                      <button class="button button-danger remove-item" data-product-id="${item.productId}">Remove</button>
                    </div>
                    <div class="qty-row">
                      <label for="qty-${item.productId}">Quantity</label>
                      <input id="qty-${item.productId}" class="quantity-input" type="number" min="1" step="1" value="${item.quantity}" data-product-id="${item.productId}">
                    </div>
                  </article>
                `,
              )
              .join("")}
          </div>
        </div>
        <aside class="summary-card">
          <p class="eyebrow">Summary</p>
          <h2>Ready to submit</h2>
          <dl>
            <dt>Items</dt>
            <dd>${cart.reduce((sum, item) => sum + item.quantity, 0)}</dd>
            <dt>Estimated total</dt>
            <dd>$${total.toFixed(2)}</dd>
            <dt>Signed in role</dt>
            <dd>${escapeHtml(auth.role || "guest")}</dd>
          </dl>
          <div class="stack">
            <button class="button button-primary" id="checkout-button">Place order</button>
            <button class="button button-secondary" id="clear-cart-button">Clear cart</button>
          </div>
        </aside>
      </section>
    `;

    root.querySelectorAll(".quantity-input").forEach((input) => {
      input.addEventListener("change", () => {
        updateCartItem(input.dataset.productId, Number(input.value));
        onCartChange();
        paint();
      });
    });

    root.querySelectorAll(".remove-item").forEach((button) => {
      button.addEventListener("click", () => {
        removeFromCart(button.dataset.productId);
        onCartChange();
        paint();
      });
    });

    root.querySelector("#clear-cart-button").addEventListener("click", () => {
      clearCart();
      onCartChange();
      paint();
    });

    root.querySelector("#checkout-button").addEventListener("click", async () => {
      if (!auth.token) {
        message = "Login first so the API can attach the order to your account.";
        messageType = "error";
        paint();
        return;
      }

      if (auth.role === "viewer") {
        message = "This account can browse only. Use a customer or admin login to place orders.";
        messageType = "error";
        paint();
        return;
      }

      const payload = cart.map((item) => ({
        product_id: item.productId,
        quantity: item.quantity,
      }));

      const button = root.querySelector("#checkout-button");
      button.disabled = true;
      button.textContent = "Submitting...";

      try {
        await createOrder(payload);
        clearCart();
        onCartChange();
        navigate(auth.role === "admin" ? "#/admin" : "#/orders");
      } catch (error) {
        message = error.message || "Checkout failed.";
        messageType = "error";
        paint();
      }
    });
  }

  paint();
}
