import { fetchCategories, fetchProduct } from "../api.js";
import { addToCart } from "../store.js";

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDate(value) {
  if (!value) {
    return "—";
  }
  try {
    return new Date(value).toLocaleString();
  } catch (error) {
    return value;
  }
}

function renderSheet(root, options) {
  const { product, categories, onCartChange } = options;

  const category = categories.find((c) => c.id === product.category_id);
  const categoryLabel = category ? category.name : "Unsorted";

  function paint(message = "", messageType = "info") {
    root.innerHTML = `
      <section class="view-grid">
        <div class="section-card product-detail-sheet">
          <div class="section-header">
            <div>
              <p class="eyebrow">Product</p>
              <h2>${escapeHtml(product.name)}</h2>
              <div class="line-meta">
                <span class="price-tag">$${Number(product.price).toFixed(2)}</span>
                <span class="badge">Stock ${product.stock}</span>
                <span class="badge">${escapeHtml(categoryLabel)}</span>
              </div>
            </div>
            <div class="inline-actions product-detail-actions">
              <button type="button" class="button button-primary" id="detail-add-cart">Add to cart</button>
              <a class="button button-secondary" href="#/catalog">Back to catalog</a>
            </div>
          </div>
          ${
            message
              ? `<p class="message ${messageType}">${escapeHtml(message)}</p>`
              : ""
          }
          <p class="product-detail-description">${escapeHtml(product.description || "No description provided.")}</p>
          <dl class="product-meta-grid">
            <div><dt>Product ID</dt><dd>${product.id}</dd></div>
            <div><dt>Category ID</dt><dd>${product.category_id ?? "—"}</dd></div>
            <div><dt>Created</dt><dd>${escapeHtml(formatDate(product.created_at))}</dd></div>
            <div><dt>Updated</dt><dd>${escapeHtml(formatDate(product.updated_at))}</dd></div>
          </dl>
        </div>
      </section>
    `;

    root.querySelector("#detail-add-cart").addEventListener("click", () => {
      if (product.stock <= 0) {
        paint("This item is out of stock.", "error");
        return;
      }
      addToCart(product, 1);
      if (typeof onCartChange === "function") {
        onCartChange();
      }
      paint(`${product.name} added to cart.`, "success");
    });
  }

  paint();
}

export async function renderProductDetailPage(root, options) {
  const { productId, onCartChange } = options;
  root.innerHTML = '<div class="loading">Loading product...</div>';

  try {
    const [product, categories] = await Promise.all([
      fetchProduct(productId),
      fetchCategories(),
    ]);
    renderSheet(root, { product, categories, onCartChange });
  } catch (error) {
    root.innerHTML = `
      <section class="section-card">
        <p class="message error">${escapeHtml(error.message || "Could not load this product.")}</p>
        <div class="inline-actions">
          <a class="button button-primary" href="#/catalog">Back to catalog</a>
        </div>
      </section>
    `;
  }
}
