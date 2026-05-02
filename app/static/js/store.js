const CART_KEY = "ecommerce-lite-cart";
const AUTH_KEY = "ecommerce-lite-auth";

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (error) {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function getCartKey() {
  const auth = readJson(AUTH_KEY, null);
  const owner = auth && auth.username ? `user:${auth.username}` : "guest";
  return `${CART_KEY}:${owner}`;
}

function sanitizeCart(items) {
  if (!Array.isArray(items)) {
    return [];
  }

  return items
    .filter((item) => item && Number.isInteger(item.productId) && item.quantity > 0)
    .map((item) => ({
      productId: item.productId,
      name: String(item.name || "Unnamed product"),
      price: Number(item.price || 0),
      quantity: Number(item.quantity || 1),
    }));
}

export function getCart() {
  return sanitizeCart(readJson(getCartKey(), []));
}

export function saveCart(items) {
  writeJson(getCartKey(), sanitizeCart(items));
}

export function addToCart(product, quantity = 1) {
  const cart = getCart();
  const existing = cart.find((item) => item.productId === product.id);

  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.push({
      productId: product.id,
      name: product.name,
      price: Number(product.price || 0),
      quantity,
    });
  }

  saveCart(cart);
  return getCart();
}

export function updateCartItem(productId, quantity) {
  const nextQuantity = Number(quantity);
  const cart = getCart();
  const item = cart.find((entry) => entry.productId === Number(productId));

  if (!item) {
    return cart;
  }

  if (nextQuantity <= 0) {
    return removeFromCart(productId);
  }

  item.quantity = nextQuantity;
  saveCart(cart);
  return getCart();
}

export function removeFromCart(productId) {
  const cart = getCart().filter((item) => item.productId !== Number(productId));
  saveCart(cart);
  return cart;
}

export function clearCart() {
  localStorage.removeItem(getCartKey());
}

export function getCartCount() {
  return getCart().reduce((sum, item) => sum + item.quantity, 0);
}

export function getCartTotal() {
  return getCart().reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function getAuth() {
  const auth = readJson(AUTH_KEY, null);
  if (!auth || !auth.token) {
    return { token: "", role: "", username: "" };
  }
  return {
    token: auth.token,
    role: auth.role || "",
    username: auth.username || "",
  };
}

export function saveAuth(auth) {
  const currentAuth = getAuth();
  const nextUsername = auth.username || "";
  const currentUsername = currentAuth.username || "";

  if (currentUsername && currentUsername !== nextUsername) {
    clearCart();
  }

  writeJson(AUTH_KEY, {
    token: auth.token,
    role: auth.role,
    username: auth.username,
  });
}

export function clearAuth() {
  clearCart();
  localStorage.removeItem(AUTH_KEY);
}

export function isLoggedIn() {
  return Boolean(getAuth().token);
}
