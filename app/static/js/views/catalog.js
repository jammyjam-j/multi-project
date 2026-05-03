import { fetchAllProducts, fetchCategories } from "../api.js";
import { addToCart } from "../store.js";
import { escapeHtml } from "../utils.js";

function renderProducts(products, categories, activeCategoryId) {
  const categoryMap = new Map(categories.map((category) => [category.id, category.name]));
  const filtered = activeCategoryId
    ? products.filter((product) => product.category_id === Number(activeCategoryId))
    : products;

  if (!filtered.length) {
    return '<div class="empty-state">No products match this category yet.</div>';
  }

  return `
    <div class="products-grid">
      ${filtered
        .map(
          (product) => `
            <article class="product-card">
              <a class="product-card-hit" href="#/product/${product.id}">
                <h3>${escapeHtml(product.name)}</h3>
                <div class="product-meta">
                  <span class="price-tag">$${Number(product.price).toFixed(2)}</span>
                  <span class="badge">Stock ${product.stock}</span>
                  <span class="badge">${escapeHtml(categoryMap.get(product.category_id) || "Unsorted")}</span>
                </div>
                <p class="muted">${escapeHtml(product.description || "No description added.")}</p>
                <span class="product-card-open muted">View details -></span>
              </a>
              <div class="inline-actions">
                <button type="button" class="button button-primary add-to-cart" data-product-id="${product.id}">Add to cart</button>
              </div>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

export async function renderCatalog(root, options) {
  const { onCartChange } = options;
  root.innerHTML = '<div class="loading">Loading catalog...</div>';

  try {
    const [products, categories] = await Promise.all([fetchAllProducts(), fetchCategories()]);
    let activeCategoryId = "";
    let flashMessage = "";

    function paint() {
      root.innerHTML = `
        <section class="view-grid">
          <div class="section-card">
            <div class="section-header">
              <div>
                <p class="eyebrow">Storefront</p>
                <h2>Catalog</h2>
                <p>Browse products here and place orders from the cart.</p>
              </div>
              <div class="hero-note">
                <p>Showing ${products.length} product${products.length === 1 ? "" : "s"}.</p>
              </div>
            </div>
            ${flashMessage ? `<p class="message success">${escapeHtml(flashMessage)}</p>` : ""}
            <div class="catalog-layout">
              <aside class="panel">
                <p class="eyebrow">Categories</p>
                <div class="filter-list">
                  <button class="button ${activeCategoryId ? "button-secondary" : "button-primary"} category-filter" data-category-id="">All items</button>
                  ${categories
                    .map(
                      (category) => `
                        <button class="button ${String(category.id) === String(activeCategoryId) ? "button-primary" : "button-secondary"} category-filter" data-category-id="${category.id}">
                          ${escapeHtml(category.name)}
                        </button>
                      `,
                    )
                    .join("")}
                </div>
              </aside>
              <div>
                ${renderProducts(products, categories, activeCategoryId)}
              </div>
            </div>
          </div>
        </section>
      `;

      root.querySelectorAll(".category-filter").forEach((button) => {
        button.addEventListener("click", () => {
          activeCategoryId = button.dataset.categoryId || "";
          paint();
        });
      });

      root.querySelectorAll(".add-to-cart").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();
          const productId = Number(button.dataset.productId);
          const product = products.find((entry) => entry.id === productId);
          if (!product) {
            return;
          }
          addToCart(product, 1);
          flashMessage = `${product.name} added to cart.`;
          onCartChange();
          paint();
        });
      });
    }

    paint();
  } catch (error) {
    root.innerHTML = `
      <section class="section-card">
        <p class="message error">${escapeHtml(error.message || "Could not load catalog.")}</p>
      </section>
    `;
  }
}
