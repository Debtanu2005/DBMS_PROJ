/* ================================================================
   orders.js — Order History page logic
   Depends on: api.js (loaded first via <script> tag)
================================================================ */

'use strict';

/* ── STATE ──────────────────────────────────────────────────── */
let allOrders  = [];
let activeFilter = 'all';   // 'all' | 'processing' | 'shipped' | 'delivered'

/* ── MOCK DATA (offline fallback) ───────────────────────────── */
function getMockOrders() {
  return [
    {
      order_id: 1001, status: 'delivered', total: 748,
      date: '2026-03-15T10:30:00',
      address: '42 MG Road, Bhubaneswar, Odisha 751001',
      items: [
        { title: 'The Midnight Library', author: 'Matt Haig',    quantity: 1, price: 349 },
        { title: 'Atomic Habits',         author: 'James Clear',  quantity: 1, price: 399 },
      ],
    },
    {
      order_id: 1002, status: 'shipped', total: 499,
      date: '2026-04-01T14:00:00',
      address: '42 MG Road, Bhubaneswar, Odisha 751001',
      items: [
        { title: 'Sapiens', author: 'Yuval Noah Harari', quantity: 1, price: 499 },
      ],
    },
    {
      order_id: 1003, status: 'processing', total: 249,
      date: '2026-04-07T09:00:00',
      address: '42 MG Road, Bhubaneswar, Odisha 751001',
      items: [
        { title: '1984', author: 'George Orwell', quantity: 1, price: 249 },
      ],
    },
  ];
}

/* ── LOAD ORDERS FROM BACKEND ───────────────────────────────── */
async function loadOrders() {
  const content = document.getElementById('orders-content');
  if (!content) return;

  // Auth guard
  if (!Auth.isLoggedIn()) {
    content.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔒</div>
        <div class="empty-title">Sign in to view your orders</div>
        <div class="empty-sub">Your order history is saved to your account</div>
        <a href="login.html" class="empty-cta">Sign In</a>
      </div>`;
    return;
  }

  // Show loading skeletons
  content.innerHTML = Array.from({ length: 3 }, (_, i) => `
    <div class="sk-card" style="animation-delay:${i * 0.08}s">
      <div style="flex:1">
        <div class="sk-line" style="width:20%;margin-bottom:10px"></div>
        <div class="sk-line" style="width:50%"></div>
      </div>
      <div class="sk-line" style="width:80px;height:24px;align-self:center"></div>
    </div>`).join('');

  try {
    allOrders = await apiGetOrders();
  } catch (err) {
    console.warn('Orders fetch failed — using mock data:', err.message);
    allOrders = getMockOrders();
  }

  renderOrders();
}

/* ── FILTER TABS ────────────────────────────────────────────── */
function setFilter(f) {
  activeFilter = f;
  renderOrders();
}

/* ── RENDER ORDERS ──────────────────────────────────────────── */
function renderOrders() {
  const content = document.getElementById('orders-content');
  if (!content) return;

  if (!allOrders.length) {
    content.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📦</div>
        <div class="empty-title">No orders yet</div>
        <div class="empty-sub">Start browsing to place your first order</div>
        <a href="search.html" class="empty-cta">Browse Books</a>
      </div>`;
    return;
  }

  // Stats
  const totalSpent = allOrders.reduce((s, o) => s + (o.total || o.amount || 0), 0);
  const delivered  = allOrders.filter(
    o => (o.status || '').toLowerCase() === 'delivered'
  ).length;

  // Filter
  const filtered = activeFilter === 'all'
    ? allOrders
    : allOrders.filter(o => (o.status || '').toLowerCase() === activeFilter);

  content.innerHTML = `
    <!-- Stats row -->
    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-box-num">${allOrders.length}</div>
        <div class="stat-box-label">Total Orders</div>
      </div>
      <div class="stat-box">
        <div class="stat-box-num">${delivered}</div>
        <div class="stat-box-label">Delivered</div>
      </div>
      <div class="stat-box">
        <div class="stat-box-num">₹${totalSpent}</div>
        <div class="stat-box-label">Total Spent</div>
      </div>
      <div class="stat-box">
        <div class="stat-box-num">${allOrders.length - delivered}</div>
        <div class="stat-box-label">In Progress</div>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="filter-tabs">
      ${['all', 'processing', 'shipped', 'delivered'].map(f => `
        <button
          class="tab-btn ${activeFilter === f ? 'active' : ''}"
          onclick="setFilter('${f}')"
        >${f === 'all' ? `All (${allOrders.length})` : capitalize(f)}</button>
      `).join('')}
    </div>

    <!-- Order cards -->
    ${filtered.length === 0
      ? `<div class="empty-state">
           <div class="empty-icon">📭</div>
           <div class="empty-title">No ${activeFilter} orders</div>
         </div>`
      : filtered.map((order, i) => orderCardHTML(order, i)).join('')
    }`;
}

/* ── ORDER CARD HTML ────────────────────────────────────────── */
function orderCardHTML(order, idx) {
  const id     = order.order_id || order.id || (idx + 1001);
  const status = (order.status || 'processing').toLowerCase();
  const amount = order.total || order.amount || 0;
  const date   = order.created_at || order.date || new Date().toISOString();
  const items  = order.items  || order.books  || [];
  const addr   = escHtml(order.address || order.delivery_address || 'Address on file');
  const delay  = `${idx * 0.06}s`;

  const formattedDate = new Date(date).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });

  // First item title for the card summary line
  const firstTitle = items[0]
    ? escHtml(items[0].title || items[0].book_title || 'Order')
    : 'Order';
  const moreLabel = items.length > 1 ? ` +${items.length - 1} more` : '';

  return `
    <div class="order-card" id="order-${id}" style="animation-delay:${delay}">

      <!-- Header (click to expand) -->
      <div class="order-header" onclick="toggleOrder('${id}')">
        <div class="order-id">#${String(id).padStart(5, '0')}</div>

        <div class="order-meta">
          <div class="order-title">${firstTitle}${moreLabel}</div>
          <div class="order-date">${formattedDate}</div>
        </div>

        <div>
          <div class="order-amount">₹${amount}</div>
          <div class="order-amount-label">Total</div>
        </div>

        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:.6rem">
          <span class="status-badge status-${status}">${capitalize(status)}</span>
          <span class="chevron">▼</span>
        </div>
      </div>

      <!-- Detail drawer -->
      <div class="order-details" id="details-${id}">
        <div class="details-title">Order Items</div>

        ${items.length
          ? items.map((item, i) => `
              <div class="order-book-row">
                <div class="order-book-spine"
                     style="background:${SPINE_COLORS[i % SPINE_COLORS.length]}"></div>
                <div class="order-book-info">
                  <div class="order-book-title">
                    ${escHtml(item.title || item.book_title || 'Book')}
                  </div>
                  <div class="order-book-author">
                    ${escHtml(item.author || item.book_author || '')}
                  </div>
                </div>
                <div class="order-book-qty">×${item.quantity || 1}</div>
                <div class="order-book-price">
                  ${item.price ? '₹' + item.price : ''}
                </div>
              </div>`).join('')
          : `<p style="font-size:.95rem;color:var(--muted);font-weight:300">
               No item details available
             </p>`
        }

        <div class="order-address">
          <strong>Delivery Address</strong>
          ${addr}
        </div>
      </div>
    </div>`;
}

/* ── TOGGLE ORDER DETAIL DRAWER ─────────────────────────────── */
function toggleOrder(id) {
  const card    = document.getElementById(`order-${id}`);
  const details = document.getElementById(`details-${id}`);
  card?.classList.toggle('expanded');
  details?.classList.toggle('open');
}

/* ── UTILS ──────────────────────────────────────────────────── */
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/* ── INIT ───────────────────────────────────────────────────── */
initNav();
window.addEventListener('DOMContentLoaded', () => loadOrders());