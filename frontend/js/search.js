/* ================================================================
   search.js — Browse / Search page logic
   Depends on: api.js (loaded first via <script> tag)
================================================================ */

'use strict';

/* ── PAGE STATE ─────────────────────────────────────────────── */
const state = {
  query   : '',
  type    : 'all',   // 'all' | 'author' | 'title'
  sort    : '',
  view    : 'grid',
  books   : [],      // raw results from last API call
  filtered: [],      // after client-side sort is applied
};

/* ── MOCK DATA (offline fallback) ───────────────────────────── */
const MOCK_BOOKS = [
  { id:1,  title:'The Midnight Library',     author:'Matt Haig',          price:349 },
  { id:2,  title:'Sapiens',                   author:'Yuval Noah Harari',  price:499 },
  { id:3,  title:'Atomic Habits',             author:'James Clear',        price:399 },
  { id:4,  title:'The Alchemist',             author:'Paulo Coelho',       price:299 },
  { id:5,  title:'1984',                       author:'George Orwell',      price:249 },
  { id:6,  title:'Dune',                       author:'Frank Herbert',      price:449 },
  { id:7,  title:'Thinking, Fast and Slow',   author:'Daniel Kahneman',    price:549 },
  { id:8,  title:'The Name of the Wind',      author:'Patrick Rothfuss',   price:399 },
  { id:9,  title:'A Brief History of Time',   author:'Stephen Hawking',    price:329 },
  { id:10, title:'The Psychology of Money',   author:'Morgan Housel',      price:379 },
  { id:11, title:'Crime and Punishment',      author:'Fyodor Dostoevsky',  price:279 },
  { id:12, title:'The Brothers Karamazov',    author:'Fyodor Dostoevsky',  price:319 },
];

function getMockBooks(query, type) {
  if (!query) return MOCK_BOOKS;
  const q = query.toLowerCase();
  return MOCK_BOOKS.filter(b => {
    if (type === 'author') return b.author.toLowerCase().includes(q);
    if (type === 'title')  return b.title.toLowerCase().includes(q);
    return b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q);
  });
}

/* ── SEARCH TYPE TOGGLE ─────────────────────────────────────── */
function setType(type) {
  state.type = type;
  ['all', 'author', 'title'].forEach(id => {
    document.getElementById(`type-${id}`)
      ?.classList.toggle('active', id === type);
  });
  // Update placeholder to hint the user
  const hints = {
    all   : 'Type a title, author name, or keyword…',
    author: 'Enter an author name…',
    title : 'Enter a book title…',
  };
  const input = document.getElementById('search-input');
  if (input) input.placeholder = hints[type];
}

/* ── VIEW TOGGLE (grid / list) — no re-fetch ────────────────── */
function setView(view) {
  state.view = view;
  document.getElementById('btn-grid')?.classList.toggle('active', view === 'grid');
  document.getElementById('btn-list')?.classList.toggle('active', view === 'list');
  // Update grid class then re-render cards with correct layout
  renderBooks(state.filtered);
}

/* ── CLIENT-SIDE SORT — no re-fetch ────────────────────────── */
function sortBooks() {
  const val   = document.getElementById('sort-select')?.value || '';
  state.sort  = val;
  const books = [...state.books];

  if (val === 'title_asc')  books.sort((a, b) => (a.title  || '').localeCompare(b.title  || ''));
  if (val === 'title_desc') books.sort((a, b) => (b.title  || '').localeCompare(a.title  || ''));
  if (val === 'author_asc') books.sort((a, b) => (a.author || '').localeCompare(b.author || ''));
  if (val === 'price_asc')  books.sort((a, b) => (a.price  || 0) - (b.price  || 0));
  if (val === 'price_desc') books.sort((a, b) => (b.price  || 0) - (a.price  || 0));

  state.filtered = books;
  renderBooks(state.filtered);
}

/* ── CLEAR FILTERS ──────────────────────────────────────────── */
function clearFilters() {
  document.querySelectorAll('.check-item input').forEach(c => c.checked = false);
  const sel = document.getElementById('sort-select');
  if (sel) sel.value = '';
  state.sort     = '';
  state.filtered = [...state.books];
  renderBooks(state.filtered);
}

/* ── MAIN SEARCH — calls backend ────────────────────────────── */
async function doSearch() {
  const query   = document.getElementById('search-input')?.value.trim() || '';
  state.query   = query;

  showSkeletons();
  setResultsInfo('Searching…');

  try {
    const books    = await apiSearchBooks(query, state.type);
    state.books    = books;
    state.filtered = books;
    sortBooks();   // apply current sort if one is selected
  } catch (err) {
    // Only fall back to mock data when the backend is truly unreachable (network error).
    // Do NOT mask real HTTP errors like 401/422 — show them instead.
    const isNetworkError = err.message.includes('Failed to fetch') ||
                           err.message.includes('NetworkError') ||
                           err.message.includes('502');
    if (isNetworkError) {
      console.warn('Backend unreachable — showing mock data:', err.message);
      const books    = getMockBooks(query, state.type);
      state.books    = books;
      state.filtered = books;
      renderBooks(state.filtered);
    } else {
      // Real backend error — show it so we can debug
      state.books    = [];
      state.filtered = [];
      setResultsInfo(`Error: ${escHtml(err.message)}`);
      renderBooks([]);
    }
  }
}

/* ── RENDER BOOKS ───────────────────────────────────────────── */
function renderBooks(books) {
  const grid = document.getElementById('books-grid');
  if (!grid) return;

  // Sync grid CSS class with current view
  grid.className = state.view === 'list' ? 'is-list' : '';

  // Results info bar
  const count = books.length;
  setResultsInfo(
    count === 0
      ? 'No results'
      : `<strong>${count}</strong> result${count !== 1 ? 's' : ''}` +
        (state.query ? ` for "<em>${escHtml(state.query)}</em>"` : '')
  );

  if (!count) {
    grid.innerHTML = `
      <div class="state-box">
        <div class="state-icon">📚</div>
        <div class="state-title">
          ${state.query ? `Nothing found for "${escHtml(state.query)}"` : 'No books to show'}
        </div>
        <div class="state-sub">Try a different search term or clear the filters</div>
      </div>`;
    return;
  }

  grid.innerHTML = books.map((book, i) => bookCardHTML(book, i)).join('');
}

/* ── BOOK CARD HTML ─────────────────────────────────────────── */
function bookCardHTML(book, idx) {
  const color  = SPINE_COLORS[idx % SPINE_COLORS.length];

  const title  = escHtml(book.title || 'Untitled');
  const author = escHtml(book.author || '');

  const stock  = book.stock != null
    ? `<div class="book-stock">
        ${book.stock > 0 ? `${book.stock} in stock` : '<span style="color:red">Out of stock</span>'}
       </div>`
    : '';

  const id     = book.id ?? idx;
  const delay  = `${idx * 0.035}s`;

  return `
    <div class="book-card" style="animation-delay:${delay}">
      <div class="book-spine" style="background:${color}">
        <span class="book-spine-text">${title}</span>
      </div>
      <div class="book-body">
        <div class="book-title">${title}</div>
        ${author ? `<div class="book-author">${author}</div>` : ''}
        ${stock}
      </div>
      <div class="book-footer">
        <button
          class="add-cart-btn"
          data-id="${id}"
          data-title="${title}"
          onclick="handleAddToCart(this)"
        >Add to Cart</button>
      </div>
    </div>`;
}

/* ── ADD TO CART ────────────────────────────────────────────── */
async function handleAddToCart(btn) {
  if (!Auth.isLoggedIn()) {
    showToast('Sign in to add books to your cart', 'err');
    setTimeout(() => window.location.href = 'login.html', 1100);
    return;
  }

  const bookId = btn.dataset.id;
  const title  = btn.dataset.title;

  btn.disabled    = true;
  btn.textContent = '…';

  try {
    await apiAddToCart(bookId, 1);
    btn.textContent = '✓ Added';
    btn.classList.add('is-added');
    showToast(`"${title}" added to cart`, 'ok');
    setTimeout(() => {
      btn.textContent = 'Add to Cart';
      btn.classList.remove('is-added');
      btn.disabled = false;
    }, 2000);
  } catch (err) {
    btn.textContent = 'Add to Cart';
    btn.disabled    = false;
    showToast(err.message, 'err');
  }
}

/* ── UI HELPERS ─────────────────────────────────────────────── */
function showSkeletons() {
  const grid = document.getElementById('books-grid');
  if (!grid) return;
  grid.className = '';
  grid.innerHTML = Array.from({ length: 8 }, (_, i) => `
    <div class="skel" style="animation-delay:${i * 0.04}s">
      <div class="skel-cover"></div>
      <div class="skel-line"></div>
      <div class="skel-line half"></div>
    </div>`).join('');
}

function setResultsInfo(html) {
  const el = document.getElementById('results-info');
  if (el) el.innerHTML = html;
}

/* ── INIT ───────────────────────────────────────────────────── */
initNav();

// Pre-fill query from URL ?q= param (from landing page hero search)
const _urlQ = new URLSearchParams(window.location.search).get('q') || '';
if (_urlQ) {
  const input = document.getElementById('search-input');
  if (input) input.value = _urlQ;
  state.query = _urlQ;
}


// Enter key triggers search
document.getElementById('search-input')
  ?.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

/* ================================================================*/
document.addEventListener("DOMContentLoaded", () => {

  // 🔍 Run search on page load
  doSearch();

  // ⌨️ Enter key triggers search
  const input = document.getElementById('search-input');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        doSearch();
      }
    });
  }

  // 🔑 Show admin link
  const token = localStorage.getItem("folio_token");
  const role = localStorage.getItem("role");
  const link = document.getElementById("addBookLink");

  console.log("ROLE:", role);
  console.log("LINK:", link);

  if (role === "admin" && link) {
    link.style.display = "inline"; // better than block for navbar
  }

});