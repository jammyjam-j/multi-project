import {
  createCategory,
  createProduct,
  deleteCategory,
  deleteProduct,
  fetchAllProducts,
  fetchAllOrders,
  fetchCategories,
} from "../api.js";
import { escapeHtml, formatDate } from "../utils.js";

export async function renderAdmin(root, options) {
  const { auth } = options;

  if (auth.role !== "admin") {
    root.innerHTML = `
      <section class="section-card">
        <p class="message error">Admin access is required for this dashboard.</p>
      </section>
    `;
    return;
  }

  root.innerHTML = '<div class="loading">Loading admin page...</div>';

  let productMessage = "";
  let categoryMessage = "";
  let messageType = "success";

  async function loadAndPaint() {
    const [ordersData, products, categories] = await Promise.all([
      fetchAllOrders(),
      fetchAllProducts(),
      fetchCategories(),
    ]);

    const orders = ordersData.orders || [];

    root.innerHTML = `
      <section class="view-grid">
        <div class="section-card">
          <div class="section-header">
            <div>
              <p class="eyebrow">Admin</p>
              <h2>Dashboard</h2>
              <p>Manage products, categories, and orders here.</p>
            </div>
            <div class="toolbar">
              <button class="button button-secondary" id="refresh-admin">Refresh data</button>
            </div>
          </div>
          <div class="stats-grid">
            <article class="stat-card">
              <span>Total products</span>
              <strong>${products.length}</strong>
            </article>
            <article class="stat-card">
              <span>Total categories</span>
              <strong>${categories.length}</strong>
            </article>
            <article class="stat-card">
              <span>Total orders</span>
              <strong>${orders.length}</strong>
            </article>
          </div>
        </div>

        <div class="admin-layout">
          <div class="stack">
            <section class="panel">
              <p class="eyebrow">Create product</p>
              ${productMessage ? `<p class="message ${messageType}">${escapeHtml(productMessage)}</p>` : ""}
              <form id="product-form" class="form-grid">
                <div class="field">
                  <label for="product-name">Name</label>
                  <input id="product-name" name="name" required>
                </div>
                <div class="field">
                  <label for="product-price">Price</label>
                  <input id="product-price" name="price" type="number" min="0" step="0.01" required>
                </div>
                <div class="field">
                  <label for="product-stock">Stock</label>
                  <input id="product-stock" name="stock" type="number" min="0" step="1" value="0">
                </div>
                <div class="field">
                  <label for="product-category">Category</label>
                  <select id="product-category" name="category_id">
                    <option value="">No category</option>
                    ${categories
                      .map(
                        (category) => `
                          <option value="${category.id}">${escapeHtml(category.name)}</option>
                        `,
                      )
                      .join("")}
                  </select>
                </div>
                <div class="field" style="grid-column: 1 / -1;">
                  <label for="product-description">Description</label>
                  <textarea id="product-description" name="description"></textarea>
                </div>
                <div class="form-actions" style="grid-column: 1 / -1;">
                  <button class="button button-primary" type="submit">Create product</button>
                </div>
              </form>
            </section>

            <section class="panel">
              <p class="eyebrow">Create category</p>
              ${categoryMessage ? `<p class="message ${messageType}">${escapeHtml(categoryMessage)}</p>` : ""}
              <form id="category-form" class="form-grid single">
                <div class="field">
                  <label for="category-name">Name</label>
                  <input id="category-name" name="name" required>
                </div>
                <div class="field">
                  <label for="category-description">Description</label>
                  <textarea id="category-description" name="description"></textarea>
                </div>
                <div class="form-actions">
                  <button class="button button-primary" type="submit">Create category</button>
                </div>
              </form>
            </section>
          </div>

          <div class="stack">
            <section class="panel">
              <p class="eyebrow">Products</p>
              <div class="admin-list">
                ${
                  products.length
                    ? products
                        .map(
                          (product) => `
                            <div class="table-row">
                              <div>
                                <strong>${escapeHtml(product.name)}</strong>
                                <div class="muted">$${Number(product.price).toFixed(2)} | stock ${product.stock}</div>
                              </div>
                              <div>${escapeHtml(categories.find((category) => category.id === product.category_id)?.name || "Unsorted")}</div>
                              <div><button class="button button-danger delete-product" data-product-id="${product.id}">Delete</button></div>
                            </div>
                          `,
                        )
                        .join("")
                    : '<div class="empty-state">No products yet.</div>'
                }
              </div>
            </section>

            <section class="panel">
              <p class="eyebrow">Categories</p>
              <div class="admin-list">
                ${
                  categories.length
                    ? categories
                        .map(
                          (category) => `
                            <div class="table-row">
                              <div>
                                <strong>${escapeHtml(category.name)}</strong>
                                <div class="muted">${escapeHtml(category.description || "No description")}</div>
                              </div>
                              <div>${escapeHtml(formatDate(category.created_at))}</div>
                              <div><button class="button button-danger delete-category" data-category-id="${category.id}">Delete</button></div>
                            </div>
                          `,
                        )
                        .join("")
                    : '<div class="empty-state">No categories yet.</div>'
                }
              </div>
            </section>
          </div>
        </div>

        <section class="section-card">
          <p class="eyebrow">Orders</p>
          <h2>All orders</h2>
          <div class="stack">
            ${
              orders.length
                ? orders
                    .map(
                      (order) => `
                        <article class="order-card">
                          <div class="section-header">
                            <div>
                              <h3>Order #${order.id}</h3>
                              <div class="line-meta">
                                <span>User ${order.user_id}</span>
                                <span>Status ${escapeHtml(order.status)}</span>
                                <span>Total $${Number(order.total_amount).toFixed(2)}</span>
                                <span>${escapeHtml(formatDate(order.created_at))}</span>
                              </div>
                            </div>
                          </div>
                          <div class="order-items">
                            ${order.items
                              .map(
                                (item) => `
                                  <div class="table-row">
                                    <div><strong>${escapeHtml(item.product_name)}</strong></div>
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
                    .join("")
                : '<div class="empty-state">No orders recorded yet.</div>'
            }
          </div>
        </section>
      </section>
    `;

    root.querySelector("#refresh-admin").addEventListener("click", async () => {
      await paintWithErrorHandling();
    });

    root.querySelector("#product-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const payload = {
        name: String(form.get("name") || "").trim(),
        price: Number(form.get("price") || 0),
        stock: Number(form.get("stock") || 0),
        description: String(form.get("description") || "").trim(),
      };
      const categoryId = String(form.get("category_id") || "").trim();
      if (categoryId) {
        payload.category_id = Number(categoryId);
      }

      try {
        await createProduct(payload);
        productMessage = "Product created.";
        messageType = "success";
        await paintWithErrorHandling();
      } catch (error) {
        productMessage = error.message || "Could not create product.";
        messageType = "error";
        await paintWithErrorHandling();
      }
    });

    root.querySelector("#category-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const payload = {
        name: String(form.get("name") || "").trim(),
        description: String(form.get("description") || "").trim(),
      };

      try {
        await createCategory(payload);
        categoryMessage = "Category created.";
        messageType = "success";
        await paintWithErrorHandling();
      } catch (error) {
        categoryMessage = error.message || "Could not create category.";
        messageType = "error";
        await paintWithErrorHandling();
      }
    });

    root.querySelectorAll(".delete-product").forEach((button) => {
      button.addEventListener("click", async () => {
        try {
          await deleteProduct(button.dataset.productId);
          productMessage = "Product deleted.";
          messageType = "success";
          await paintWithErrorHandling();
        } catch (error) {
          productMessage = error.message || "Could not delete product.";
          messageType = "error";
          await paintWithErrorHandling();
        }
      });
    });

    root.querySelectorAll(".delete-category").forEach((button) => {
      button.addEventListener("click", async () => {
        try {
          await deleteCategory(button.dataset.categoryId);
          categoryMessage = "Category deleted.";
          messageType = "success";
          await paintWithErrorHandling();
        } catch (error) {
          categoryMessage = error.message || "Could not delete category.";
          messageType = "error";
          await paintWithErrorHandling();
        }
      });
    });
  }

  async function paintWithErrorHandling() {
    try {
      await loadAndPaint();
    } catch (error) {
      root.innerHTML = `
        <section class="section-card">
          <p class="message error">${escapeHtml(error.message || "Could not load admin page.")}</p>
        </section>
      `;
    }
  }

  await paintWithErrorHandling();
}
