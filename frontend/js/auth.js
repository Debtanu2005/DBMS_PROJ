

'use strict';

/* ── REDIRECT IF LOGGED IN ─────────────────────────────────── */
if (Auth.isLoggedIn()) {
  window.location.replace('search.html');
}

/* ── HELPERS ───────────────────────────────────────────────── */
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

function setButtonLoading(id, state) {
  const btn = document.getElementById(id);
  if (!btn) return;

  btn.disabled = state;
  btn.classList.toggle('loading', state);
}

/* ================================================================
   LOGIN
================================================================ */

async function handleLogin() {
  const email = document.getElementById('email')?.value.trim();
  const password = document.getElementById('password')?.value;

  clearMessages();

  if (!email || !password) {
    return showFormError('Please fill all fields.');
  }

  try {
    setButtonLoading('login-btn', true);

    await apiLogin(email, password);

    showFormSuccess('Login successful!');
    setTimeout(() => {
      window.location.href = 'search.html';
    }, 800);

  } catch (err) {
    showFormError(err.message || 'Login failed');
  } finally {
    setButtonLoading('login-btn', false);
  }
}

/* ================================================================
   REGISTER
================================================================ */
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
const phone         = document.getElementById('phone')?.value.trim()  || '';
const dob           = document.getElementById('dob')?.value            || '';
const universityId  = parseInt(document.getElementById('university')?.value) || null;
const major         = document.getElementById('major')?.value.trim()   || '';
const status        = document.getElementById('status')?.value         || '';
const yearOfStudent = parseInt(document.getElementById('year')?.value) || null;

if (phone && !/^\d{7,15}$/.test(phone)) {
  showFormError('Phone number must be 7–15 digits.'); return;
}
if (status && !yearOfStudent) {
  showFormError('Please select your year of study.'); return;
}

const studentInfo = {};
if (firstName)     studentInfo.first_name      = firstName;
if (lastName)      studentInfo.last_name       = lastName;
if (phone)         studentInfo.phone           = phone;
if (dob)           studentInfo.dob             = dob;
if (universityId)  studentInfo.university_id   = universityId;
if (major)         studentInfo.major           = major;
if (status)        studentInfo.status          = status;
if (yearOfStudent) studentInfo.year_of_student = yearOfStudent;

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
/* ================================================================
   ENTER KEY SUPPORT
================================================================ */

document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;

  if (document.getElementById('login-btn')) {
    handleLogin();
  }

  if (document.getElementById('register-btn')) {
    handleRegister();
  }
});