

'use strict';

/* ── CONFIG ─────────────────────────────────────────────────── */
const BASE_URL = '/api';

/* ── TOKEN MANAGEMENT ───────────────────────────────────────── */
const Auth = {
  getToken: () => localStorage.getItem('folio_token'),
  setToken: (t) => localStorage.setItem('folio_token', t),
  clearToken: () => localStorage.removeItem('folio_token'),
  isLoggedIn: () => !!localStorage.getItem('folio_token'),
};

/* ── HEADERS ────────────────────────────────────────────────── */
function jsonHeaders(requireAuth = false) {
  const headers = { 'Content-Type': 'application/json' };
  const token = Auth.getToken();

  if (token) headers['Authorization'] = `Bearer ${token}`;
  else if (requireAuth) throw new Error('Not authenticated');

  return headers;
}

/* ── RESPONSE HANDLER ───────────────────────────────────────── */
async function handleResponse(res) {
  let data;
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`);
  }

  return data;
}

/* ================================================================
   AUTH APIs
================================================================ */

async function apiLogin(email, password) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ email, password }),
  });
  const data = await handleResponse(res);

  const token =
    data.access_token ||
    data.token ||
    data.data?.access_token;

  if (token) {
    Auth.setToken(token);
  } else {
    throw new Error("No token received from server");
  }

  // ✅ FIX ROLE ALSO
  const role = data.role || data.data?.role;
  if (role) {
    localStorage.setItem('role', role);
  }

  return data;
}


async function apiRegister(email, password, studentInfo = {}) {
  const res = await fetch(`${BASE_URL}/register`, {
    method : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify({ email, password, student_info: studentInfo }),
  });
  const data = await handleResponse(res);
  console.log('LOGIN RESPONSE:', data);
  const token = typeof data.access_token === 'object' 
  ? JSON.stringify(data.access_token) 
  : data.access_token;
if (token) Auth.setToken(token);  // ← correct
  return data;
}
/* ================================================================
   BOOK SEARCH
================================================================ */
async function apiSearchBooks(query, type = 'all') {
  let url = `${BASE_URL}/search_books?q=${encodeURIComponent(query)}`;

  if (type === 'author') {
    url = `${BASE_URL}/search_books?author=${encodeURIComponent(query)}`;
  } else if (type === 'title') {
    url = `${BASE_URL}/search_books?name=${encodeURIComponent(query)}`;
  }

  const res = await fetch(url);
  const data = await res.json();

  console.log("API DATA:", data);

  return data.results || [];
}

/* ================================================================
   CART
================================================================ */

async function apiGetCart() {
  const res = await fetch(`${BASE_URL}/view_cart`, {
    headers: jsonHeaders(true),
  });

  const data = await handleResponse(res);
  return data.cart_items || [];
}

async function apiAddToCart(bookId, quantity = 1) {
  const res = await fetch(
    `${BASE_URL}/add_to_cart?book_id=${bookId}&quantity=${quantity}`,
    {
      method: 'POST',
      headers: jsonHeaders(true),
    }
  );

  return handleResponse(res);
}

/* ================================================================
   ORDERS
================================================================ */

async function apiPlaceOrder(cartId, orderInfo) {
  const res = await fetch(
    `${BASE_URL}/execute_order?cart_id=${cartId}`,
    {
      method: 'POST',
      headers: jsonHeaders(true),
      body: JSON.stringify(orderInfo),
    }
  );

  return handleResponse(res);
}

async function apiGetOrders() {
  const res = await fetch(`${BASE_URL}/view_orders`, {
    headers: jsonHeaders(true),
  });

  const data = await handleResponse(res);
  console.log("Orders API data:", data);
  return data.orders || data.results || [];
}

/* ================================================================
   UI HELPERS
================================================================ */

function showToast(msg, type = 'ok') {
  const el = document.getElementById('toast');
  if (!el) return;

  el.textContent = msg;
  el.className = `toast show ${type}`;

  setTimeout(() => el.classList.remove('show'), 3000);
}

/* ================================================================
   NAVBAR
================================================================ */

function initNav() {
  const btn = document.getElementById('nav-auth-btn');
  if (!btn) return;

  if (Auth.isLoggedIn()) {
    btn.textContent = 'Sign Out';
    btn.removeAttribute('href');        // ← remove the login.html href
    btn.onclick = (e) => {
      e.preventDefault();
      Auth.clearToken();
      localStorage.removeItem('role');  // ← also clear role
      window.location.href = 'index.html';
    };
  } else {
    btn.textContent = 'Sign In';
    btn.onclick = null;                 // ← clear any previous onclick
    btn.href = 'login.html';
  }
}

/* ================================================================
  error handling
================================================================ */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}


const SPINE_COLORS = [
  '#b85c38', '#4a6fa5', '#2d4a3e', '#7a4f7d',
  '#5c4a3a', '#3d6b5e', '#8c3b2a', '#4a7c8e',
  '#6b5a4e', '#c47b3a', '#3a5c7a', '#856a44',
];