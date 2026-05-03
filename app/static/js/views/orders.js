import { fetchMyOrders, simulateOrderPayment } from "../api.js";
import { escapeHtml, formatDate } from "../utils.js";

export async function renderOrders(root, options) {
  const { auth } = options;

  async function attachPayHandlers(container) {
    container.querySelectorAll("[data-action='simulate-pay']").forEach((button) => {
      button.addEventListener("click", async () => {
        const orderId = button.dataset.orderId;
        button.disabled = true;
        button.textContent = "Processing...";
        try {
          await simulateOrderPayment(parseInt(orderId, 10));
          await paint();
        } catch (error) {
          button.disabled = false;
          button.textContent = "Pay (simulated)";
          alert(error.message || "Payment simulation failed.");
        }
      });
    });
  }

  async function paint() {
    root.innerHTML = '<div class="loading">Loading your orders...</div>';

    try {
      const data = await fetchMyOrders();
      const orders = data.orders || [];

      root.innerHTML = `
      <section class="view-grid">
        <div class="section-card">
          <div class="section-header">
            <div>
              <p class="eyebrow">History</p>
              <h2>My orders</h2>
              <p>New orders stay in pending payment until you confirm the simulated payment.</p>
            </div>
          </div>
          ${
            orders.length
              ? `<div class="stack">
                  ${orders
                    .map(
                      (order) => `
                        <article class="order-card">
                          <div class="section-header">
                            <div>
                              <h3>Order #${order.id}</h3>
                              <div class="line-meta">
                                <span>Status ${escapeHtml(order.status)}</span>
                                <span>Total $${Number(order.total_amount).toFixed(2)}</span>
                                <span>${escapeHtml(formatDate(order.created_at))}</span>
                              </div>
                            </div>
                            ${
                              order.status === "pending_payment"
                                ? `<button type="button" class="button button-primary" data-action="simulate-pay" data-order-id="${order.id}">Pay (simulated)</button>`
                                : ""
                            }
                          </div>
                          <div class="order-items">
                            ${order.items
                              .map(
                                (item) => `
                                  <div class="table-row">
                                    <div>
                                      <strong>${escapeHtml(item.product_name)}</strong>
                                    </div>
                                    <div>${item.quantity} x $${Number(item.unit_price).toFixed(2)}</div>
                                    <div>$${Number(item.line_total).toFixed(2)}</div>
                                  </div>
                                `,
                              )
                              .join("")}
                          </div>
                        </article>
                      `,
                    )
                    .join("")}
                </div>`
              : '<div class="empty-state">No orders yet.</div>'
          }
        </div>
      </section>
    `;

      await attachPayHandlers(root);
    } catch (error) {
      root.innerHTML = `
      <section class="section-card">
        <p class="message error">${escapeHtml(error.message || "Could not load orders.")}</p>
      </section>
    `;
    }
  }

  if (!auth.token) {
    root.innerHTML = `
      <section class="section-card">
        <p class="message info">Login before opening your order history.</p>
      </section>
    `;
    return;
  }

  if (auth.role === "admin") {
    root.innerHTML = `
      <section class="section-card">
        <p class="message info">Admin accounts should use the dashboard for order review.</p>
      </section>
    `;
    return;
  }

  if (auth.role === "viewer") {
    root.innerHTML = `
      <section class="section-card">
        <p class="message error">This account does not have permission to view personal orders.</p>
      </section>
    `;
    return;
  }

  await paint();
}
