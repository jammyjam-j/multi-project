import { clearAuth, getAuth } from "./store.js";

const API_BASE = "/api/v1";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return text ? { message: text } : {};
}

async function request(path, options = {}, tokenOverride = "") {
  const auth = getAuth();
  const token = tokenOverride || auth.token;
  const headers = { ...(options.headers || {}) };
  const isJsonBody = options.body && !(options.body instanceof FormData);

  if (isJsonBody && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: isJsonBody ? JSON.stringify(options.body) : options.body,
  });

  const data = await parseResponse(response);
  return { ok: response.ok, status: response.status, data };
}

export async function apiRequest(path, options = {}) {
  const result = await request(path, options);
  if (!result.ok) {
    if (result.status === 401) {
      clearAuth();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("auth:invalid", {
          detail: { message: result.data.error || "Your session expired. Please log in again." },
        }));
      }
    }
    throw new Error(result.data.error || result.data.message || "Request failed");
  }
  return result.data;
}

export async function login(username, password) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: { username, password },
  });
}

export async function register(username, password) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: { username, password },
  });
}

function decodeBase64Url(value) {
  const base64 = value.replaceAll("-", "+").replaceAll("_", "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  return atob(padded);
}

export function readRoleFromToken(token) {
  if (!token) {
    throw new Error("Missing login token");
  }

  try {
    const [, payload] = token.split(".");
    const decoded = JSON.parse(decodeBase64Url(payload));
    if (!decoded.role) {
      throw new Error("Login token is missing role information");
    }
    return decoded.role;
  } catch (error) {
    throw new Error("Could not read role from login token");
  }
}

export function fetchProducts() {
  return apiRequest("/products");
}

export async function fetchAllProducts() {
  const firstPage = await fetchProducts();
  const pages = Number(firstPage.pages || 1);
  const products = [...(firstPage.products || [])];

  if (pages <= 1) {
    return products;
  }

  for (let page = 2; page <= pages; page += 1) {
    const nextPage = await apiRequest(`/products?page=${page}`);
    products.push(...(nextPage.products || []));
  }

  return products;
}

export function fetchCategories() {
  return apiRequest("/categories");
}

export async function fetchProduct(productId) {
  const result = await request(`/products/${Number(productId)}`, { method: "GET" });
  if (result.ok) {
    return result.data;
  }
  if (result.status === 404) {
    throw new Error("Product not found.");
  }
  throw new Error(result.data?.error || result.data?.message || "Could not load product.");
}

export function createOrder(items) {
  return apiRequest("/orders", {
    method: "POST",
    body: { items },
  });
}

export function simulateOrderPayment(orderId) {
  return apiRequest(`/orders/${orderId}/simulate-payment`, {
    method: "POST",
  });
}

export function fetchMyOrders() {
  return apiRequest("/orders/mine");
}

export function fetchAllOrders() {
  return apiRequest("/orders");
}

export function createProduct(payload) {
  return apiRequest("/products", {
    method: "POST",
    body: payload,
  });
}

export function deleteProduct(productId) {
  return apiRequest(`/products/${productId}`, {
    method: "DELETE",
  });
}

export function createCategory(payload) {
  return apiRequest("/categories", {
    method: "POST",
    body: payload,
  });
}

export function deleteCategory(categoryId) {
  return apiRequest(`/categories/${categoryId}`, {
    method: "DELETE",
  });
}
