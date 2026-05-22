const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const userId = tg?.initDataUnsafe?.user?.id || new URLSearchParams(location.search).get("user_id") || 0;

let currentPhone = "";

function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function showMainScreen() {
  showScreen("main-screen");
  loadAccounts();
}

function showAddScreen() {
  showScreen("add-screen");
  showStep("step-phone");
  document.getElementById("phone-input").value = "";
  document.getElementById("otp-input").value = "";
  document.getElementById("password-input").value = "";
  document.getElementById("step-2fa").style.display = "none";
}

function goBackToPhone() {
  showStep("step-phone");
}

function showStep(id) {
  document.querySelectorAll(".step").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function showLoader(show) {
  document.getElementById("loader").style.display = show ? "flex" : "none";
}

let toastTimer;
function showToast(msg, type = "") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast show" + (type ? " " + type : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.remove("show");
  }, 3000);
}

async function loadAccounts() {
  const list = document.getElementById("accounts-list");
  list.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const res = await fetch(`/api/accounts?user_id=${userId}`);
    const data = await res.json();
    if (!data.ok || !data.accounts.length) {
      list.innerHTML = '<div class="empty">No accounts yet. Add one below.</div>';
      return;
    }
    list.innerHTML = data.accounts.map(a => `
      <div class="account-card">
        <div class="account-info">
          <div class="account-name">${escHtml(a.name)}</div>
          <div class="account-phone">${escHtml(a.phone)}</div>
        </div>
        <button class="remove-btn" onclick="removeAccount('${escHtml(a.phone)}')">Remove</button>
      </div>
    `).join("");
  } catch {
    list.innerHTML = '<div class="empty">Failed to load. Try again.</div>';
  }
}

async function removeAccount(phone) {
  if (!confirm(`Remove account ${phone}?`)) return;
  showLoader(true);
  try {
    const res = await fetch("/api/remove-account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, phone }),
    });
    const data = await res.json();
    if (data.ok) {
      showToast("Account removed", "success");
      loadAccounts();
    } else {
      showToast(data.error || "Failed to remove", "error");
    }
  } catch {
    showToast("Network error", "error");
  } finally {
    showLoader(false);
  }
}

async function sendOtp() {
  const phone = document.getElementById("phone-input").value.trim().replace(/\D/g, "");
  if (!phone || phone.length < 8) {
    showToast("Enter a valid phone number", "error");
    return;
  }
  if (!userId) {
    showToast("Open this panel from the bot", "error");
    return;
  }
  currentPhone = phone;
  showLoader(true);
  try {
    const res = await fetch("/api/send-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, user_id: userId }),
    });
    const data = await res.json();
    if (data.ok) {
      showToast("OTP sent!", "success");
      showStep("step-otp");
    } else {
      showToast(data.error || "Failed to send OTP", "error");
    }
  } catch {
    showToast("Network error", "error");
  } finally {
    showLoader(false);
  }
}

async function verifyOtp() {
  const code = document.getElementById("otp-input").value.trim();
  const password = document.getElementById("password-input").value.trim();
  if (!code) {
    showToast("Enter the OTP code", "error");
    return;
  }
  showLoader(true);
  try {
    const res = await fetch("/api/verify-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentPhone, user_id: userId, code, password }),
    });
    const data = await res.json();
    if (data.ok) {
      document.getElementById("success-name").textContent = data.name;
      showScreen("success-screen");
    } else if (data.error === "2FA_REQUIRED") {
      document.getElementById("step-2fa").style.display = "flex";
      document.getElementById("step-2fa").style.flexDirection = "column";
      showToast("Enter your 2FA password", "");
    } else {
      showToast(data.error || "Verification failed", "error");
    }
  } catch {
    showToast("Network error", "error");
  } finally {
    showLoader(false);
  }
}

function escHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

loadAccounts();
