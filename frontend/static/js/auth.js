(() => {
  'use strict';

  const TOKEN_KEY = 'maweshi-auth-token';
  const USER_KEY = 'maweshi-auth-user';
  const LOGIN_URL = 'auth.html?view=login';
  const LANDING_URL = 'index.html';
  const ME_URL = 'http://127.0.0.1:5000/api/auth/me';
  let redirectingToLogin = false;
  let sessionVerified = false;
  let verificationPromise = null;

  class AuthRequestError extends Error {
    constructor(message, status, details, kind, payload = null) {
      super(message);
      this.name = 'AuthRequestError';
      this.status = status;
      this.details = details;
      this.kind = kind;
      this.payload = payload;
      this.errorItems = Array.isArray(payload?.error) ? payload.error : [];
    }
  }

  function saveSession(token, user) {
    if (typeof token !== 'string' || !token.trim()) throw new Error('A valid token is required.');
    const minimalUser = user && typeof user === 'object'
      ? { id: user.id ?? null, name: user.name ?? '', email: user.email ?? '' }
      : null;
    localStorage.setItem(TOKEN_KEY, token.trim());
    localStorage.setItem(USER_KEY, JSON.stringify(minimalUser));
  }

  function getToken() { return localStorage.getItem(TOKEN_KEY); }

  function getUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); }
    catch { return null; }
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    sessionVerified = false;
    verificationPromise = null;
  }

  function loginRedirect(reason) {
    if (redirectingToLogin) return;
    redirectingToLogin = true;
    window.location.replace(`${LOGIN_URL}&reason=${encodeURIComponent(reason)}`);
  }

  function permissionMessage() {
    return document.documentElement.lang === 'en'
      ? 'You do not have permission to access this record.'
      : 'آپ کو یہ ریکارڈ دیکھنے یا بدلنے کی اجازت نہیں ہے۔';
  }

  function showPermissionNotice() {
    let notice = document.querySelector('#auth-permission-notice');
    if (!notice) {
      notice = document.createElement('div');
      notice.id = 'auth-permission-notice';
      notice.className = 'auth-global-notice';
      notice.setAttribute('role', 'alert');
      document.body.prepend(notice);
    }
    notice.textContent = permissionMessage();
    notice.classList.add('is-visible');
    window.clearTimeout(showPermissionNotice.timer);
    showPermissionNotice.timer = window.setTimeout(() => notice.classList.remove('is-visible'), 7000);
  }

  function errorDetails(payload) {
    if (!payload || typeof payload !== 'object') return '';
    if (Array.isArray(payload.error)) return payload.error.join(' ');
    return typeof payload.error === 'string' ? payload.error : typeof payload.message === 'string' ? payload.message : '';
  }

  function requiresSessionVerification() {
    const page = window.location.pathname.split('/').pop().toLowerCase();
    return page !== 'auth.html' && page !== 'index.html';
  }

  function unauthorized(payload) {
    clearSession();
    loginRedirect('session-expired');
    return new AuthRequestError('Session expired', 401, errorDetails(payload), 'unauthorized', payload);
  }

  async function performSessionVerification(token) {
    const headers = new Headers({ Accept: 'application/json' });
    headers.set('Authorization', `Bearer ${token}`);

    let response;
    try { response = await fetch(ME_URL, { method: 'GET', headers }); }
    catch { throw new AuthRequestError('Connection unavailable', 0, '', 'connection'); }

    let payload = null;
    try { payload = await response.json(); }
    catch { payload = null; }

    if (response.status === 401) throw unauthorized(payload);
    if (response.status === 403) {
      showPermissionNotice();
      throw new AuthRequestError('Permission denied', 403, errorDetails(payload), 'forbidden', payload);
    }
    if (!response.ok || payload?.success !== true) {
      throw new AuthRequestError(payload?.message || 'Session verification failed', response.status, errorDetails(payload), 'request', payload);
    }

    const user = payload.data;
    if (!user || typeof user !== 'object' || user.id === null || user.id === undefined || typeof user.name !== 'string' || typeof user.email !== 'string') {
      throw new AuthRequestError('Unreadable response', response.status, '', 'response', payload);
    }

    saveSession(token, user);
    return getUser();
  }

  function verifySession() {
    if (!requiresSessionVerification()) return Promise.resolve(getUser());
    if (sessionVerified) return Promise.resolve(getUser());
    if (verificationPromise) return verificationPromise;

    const token = getToken();
    if (!token) {
      loginRedirect('login-required');
      return Promise.reject(new AuthRequestError('Authentication required', 401, '', 'unauthorized'));
    }

    verificationPromise = performSessionVerification(token)
      .then((user) => {
        sessionVerified = true;
        return user;
      })
      .catch((error) => {
        if (error.status !== 401) verificationPromise = null;
        throw error;
      });
    return verificationPromise;
  }

  async function authenticatedToken() {
    let token = getToken();
    if (!token) {
      loginRedirect('login-required');
      throw new AuthRequestError('Authentication required', 401, '', 'unauthorized');
    }
    if (requiresSessionVerification()) await verifySession();
    token = getToken();
    if (!token) throw new AuthRequestError('Authentication required', 401, '', 'unauthorized');
    return token;
  }

  async function request(url, options = {}) {
    const token = await authenticatedToken();

    const headers = new Headers(options.headers || {});
    headers.set('Authorization', `Bearer ${token}`);

    let response;
    try { response = await fetch(url, { ...options, headers }); }
    catch { throw new AuthRequestError('Connection unavailable', 0, '', 'connection'); }

    let payload = null;
    try { payload = await response.json(); }
    catch { throw new AuthRequestError('Unreadable response', response.status, '', 'response'); }

    if (response.status === 401) {
      throw unauthorized(payload);
    }
    if (response.status === 403) {
      showPermissionNotice();
      throw new AuthRequestError('Permission denied', 403, errorDetails(payload), 'forbidden', payload);
    }
    if (!response.ok || payload?.success !== true) {
      throw new AuthRequestError(payload?.message || 'Request failed', response.status, errorDetails(payload), 'request', payload);
    }
    return payload.data;
  }

  async function requestBlob(url, options = {}) {
    const token = await authenticatedToken();

    const headers = new Headers(options.headers || {});
    headers.set('Authorization', `Bearer ${token}`);

    let response;
    try { response = await fetch(url, { ...options, headers }); }
    catch { throw new AuthRequestError('Connection unavailable', 0, '', 'connection'); }

    if (response.ok) return response.blob();

    let payload = null;
    try { payload = await response.json(); }
    catch { payload = null; }

    if (response.status === 401) {
      throw unauthorized(payload);
    }
    if (response.status === 403) {
      showPermissionNotice();
      throw new AuthRequestError('Permission denied', 403, errorDetails(payload), 'forbidden', payload);
    }
    throw new AuthRequestError(payload?.message || 'Image unavailable', response.status, errorDetails(payload), 'request', payload);
  }

  function logout() {
    clearSession();
    window.location.assign(LANDING_URL);
  }

  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-logout]')) logout();
  });

  window.MaweshiAuth = { saveSession, getToken, getUser, clearSession, verifySession, request, requestBlob, logout, showPermissionNotice, AuthRequestError };

  if (requiresSessionVerification()) {
    verifySession().catch((error) => {
      if (error.status !== 401) console.error('Session could not be verified.', error);
    });
  }
})();
