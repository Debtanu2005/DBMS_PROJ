/* ================================================================
   auth.js — Login & Register page logic
   Depends on: api.js (loaded first via <script> tag)
================================================================ */

'use strict';

/* ── GUARD: already logged in ───────────────────────────────── */
// If the user is already authenticated, skip the auth pages entirely.
if (Auth.isLoggedIn()) {
  window.location.replace('search.html');
}

/* ── HELPERS ────────────────────────────────────────────────── */
function showFormError(msg) {
  const el = document.getElementById('error-msg');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  document.getElementById('success-msg')?.classList.remove('show');
}

function showFormSuccess(msg) {
  const el = document.getElementById('success-msg');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  document.getElementById('error-msg')?.classList.remove('show');
}

function clearMessages() {
  document.getElementById('error-msg')?.classList.remove('show');
  document.getElementById('success-msg')?.classList.remove('show');
}

function setButtonLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.classList.toggle('loading', loading);
  btn.disabled = loading;
}

/* ================================================================
   LOGIN PAGE
================================================================ */

/**
 * Called by the Sign In button (onclick="handleLogin()")
 * and also on Enter keydown.
 */
async function handleLogin() {
  const email    = document.getElementById('email')?.value.trim()    || '';
  const password = document.getElementById('password')?.value         || '';

  clearMessages();

  // Client-side validation
  if (!email || !password) {
    showFormError('Please fill in both fields.');
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showFormError('Please enter a valid email address.');
    return;
  }

  setButtonLoading('login-btn', true);

  try {
    await apiLogin(email, password);
    showFormSuccess('Signed in! Redirecting…');
    
    setTimeout(() => window.location.href = 'search.html', 900);
  } catch (err) {
    showFormError(err.message || 'Login failed. Please try again.');
  } finally {
    setButtonLoading('login-btn', false);
  }
}

/* ================================================================
   REGISTER PAGE
================================================================ */

/**
 * Password strength indicator.
 * Called oninput on the password field.
 */
function checkStrength(val) {
  const bar = document.getElementById('strength-bar');
  if (!bar) return;

  let score = 0;
  if (val.length >= 6)              score++;
  if (val.length >= 10)             score++;
  if (/[A-Z]/.test(val))           score++;
  if (/[0-9]/.test(val))           score++;
  if (/[^A-Za-z0-9]/.test(val))    score++;

  const pct    = score * 20;
  const colors = ['#c0392b', '#e67e22', '#c9a84c', '#2d4a3e', '#27ae60'];
  bar.style.width      = `${pct}%`;
  bar.style.background = colors[score - 1] || 'transparent';
}

/**
 * Called by the Create Account button (onclick="handleRegister()")
 * and also on Enter keydown.
 */
async function handleRegister() {
  const email     = document.getElementById('email')?.value.trim()      || '';
  const password  = document.getElementById('password')?.value           || '';
  const confirm   = document.getElementById('confirm')?.value            || '';
  const firstName = document.getElementById('first-name')?.value.trim() || '';
  const lastName  = document.getElementById('last-name')?.value.trim()  || '';
  const studentId = document.getElementById('student-id')?.value.trim() || '';

  clearMessages();

  // Validation
  if (!email || !password) {
    showFormError('Email and password are required.');
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showFormError('Please enter a valid email address.');
    return;
  }
  if (password.length < 6) {
    showFormError('Password must be at least 6 characters.');
    return;
  }
  if (password !== confirm) {
    showFormError('Passwords do not match.');
    return;
  }

  setButtonLoading('register-btn', true);

  // Build optional student_info only if fields were filled
  const studentInfo = {};
  if (firstName) studentInfo.first_name = firstName;
  if (lastName)  studentInfo.last_name  = lastName;
  if (studentId) studentInfo.student_id = studentId;

  try {
    await apiRegister(email, password, studentInfo);
    showFormSuccess('Account created! Redirecting…');
    setTimeout(() => window.location.href = 'search.html', 1000);
  } catch (err) {
    showFormError(err.message || 'Registration failed. Please try again.');
  } finally {
    setButtonLoading('register-btn', false);
  }
}

/* ── KEYBOARD SUPPORT ───────────────────────────────────────── */
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  // Detect which page we're on by which button exists
  if (document.getElementById('login-btn'))    handleLogin();
  if (document.getElementById('register-btn')) handleRegister();
});
