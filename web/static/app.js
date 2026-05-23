const tg = window.Telegram?.WebApp;
if (tg) { tg.ready(); tg.expand(); }

const userId = tg?.initDataUnsafe?.user?.id || new URLSearchParams(location.search).get("user_id") || 0;

const COUNTRIES = [
  ["Afghanistan","AF","93"],["Albania","AL","355"],["Algeria","DZ","213"],["Andorra","AD","376"],
  ["Angola","AO","244"],["Argentina","AR","54"],["Armenia","AM","374"],["Australia","AU","61"],
  ["Austria","AT","43"],["Azerbaijan","AZ","994"],["Bahrain","BH","973"],["Bangladesh","BD","880"],
  ["Belarus","BY","375"],["Belgium","BE","32"],["Bolivia","BO","591"],["Bosnia","BA","387"],
  ["Brazil","BR","55"],["Bulgaria","BG","359"],["Cambodia","KH","855"],["Cameroon","CM","237"],
  ["Canada","CA","1"],["Chile","CL","56"],["China","CN","86"],["Colombia","CO","57"],
  ["Croatia","HR","385"],["Cuba","CU","53"],["Cyprus","CY","357"],["Czech Republic","CZ","420"],
  ["Denmark","DK","45"],["Ecuador","EC","593"],["Egypt","EG","20"],["Estonia","EE","372"],
  ["Ethiopia","ET","251"],["Finland","FI","358"],["France","FR","33"],["Georgia","GE","995"],
  ["Germany","DE","49"],["Ghana","GH","233"],["Greece","GR","30"],["Guatemala","GT","502"],
  ["Hungary","HU","36"],["India","IN","91"],["Indonesia","ID","62"],["Iran","IR","98"],
  ["Iraq","IQ","964"],["Ireland","IE","353"],["Israel","IL","972"],["Italy","IT","39"],
  ["Jamaica","JM","1876"],["Japan","JP","81"],["Jordan","JO","962"],["Kazakhstan","KZ","7"],
  ["Kenya","KE","254"],["Kuwait","KW","965"],["Kyrgyzstan","KG","996"],["Latvia","LV","371"],
  ["Lebanon","LB","961"],["Libya","LY","218"],["Lithuania","LT","370"],["Luxembourg","LU","352"],
  ["Malaysia","MY","60"],["Maldives","MV","960"],["Malta","MT","356"],["Mexico","MX","52"],
  ["Moldova","MD","373"],["Mongolia","MN","976"],["Morocco","MA","212"],["Myanmar","MM","95"],
  ["Nepal","NP","977"],["Netherlands","NL","31"],["New Zealand","NZ","64"],["Nigeria","NG","234"],
  ["North Korea","KP","850"],["Norway","NO","47"],["Oman","OM","968"],["Pakistan","PK","92"],
  ["Palestine","PS","970"],["Panama","PA","507"],["Paraguay","PY","595"],["Peru","PE","51"],
  ["Philippines","PH","63"],["Poland","PL","48"],["Portugal","PT","351"],["Qatar","QA","974"],
  ["Romania","RO","40"],["Russia","RU","7"],["Saudi Arabia","SA","966"],["Senegal","SN","221"],
  ["Serbia","RS","381"],["Singapore","SG","65"],["Slovakia","SK","421"],["Slovenia","SI","386"],
  ["Somalia","SO","252"],["South Africa","ZA","27"],["South Korea","KR","82"],["Spain","ES","34"],
  ["Sri Lanka","LK","94"],["Sudan","SD","249"],["Sweden","SE","46"],["Switzerland","CH","41"],
  ["Syria","SY","963"],["Taiwan","TW","886"],["Tajikistan","TJ","992"],["Tanzania","TZ","255"],
  ["Thailand","TH","66"],["Tunisia","TN","216"],["Turkey","TR","90"],["Turkmenistan","TM","993"],
  ["UAE","AE","971"],["Uganda","UG","256"],["Ukraine","UA","380"],["United Kingdom","GB","44"],
  ["United States","US","1"],["Uruguay","UY","598"],["Uzbekistan","UZ","998"],["Venezuela","VE","58"],
  ["Vietnam","VN","84"],["Yemen","YE","967"],["Zambia","ZM","260"],["Zimbabwe","ZW","263"],
];

let currentPhone = "";
let currentPrefix = "91";

function populateCountries() {
  const sel = document.getElementById("country-select");
  COUNTRIES.forEach(([name, code, dial]) => {
    const opt = document.createElement("option");
    opt.value = dial;
    opt.textContent = `${name} (+${dial})`;
    if (code === "IN") opt.selected = true;
    sel.appendChild(opt);
  });
  updatePrefix();
}

function updatePrefix() {
  const sel = document.getElementById("country-select");
  currentPrefix = sel.value;
  document.getElementById("prefix-display").textContent = "+" + currentPrefix;
}

function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function showMainScreen() { showScreen("main-screen"); loadAccounts(); }

function showAddScreen() {
  showScreen("add-screen");
  showStep("step-phone");
  document.getElementById("phone-input").value = "";
  document.getElementById("otp-input").value = "";
  document.getElementById("password-input").value = "";
  document.getElementById("step-2fa").style.display = "none";
}

function goBackToPhone() { showStep("step-phone"); }

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
  toastTimer = setTimeout(() => el.classList.remove("show"), 3000);
}

function escHtml(str) {
  return String(str || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function avatarHtml(a) {
  return `<div class="account-avatar">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
    </svg>
  </div>`;
}

async function loadAccounts() {
  const list = document.getElementById("accounts-list");
  list.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div>';
  try {
    const res = await fetch(`/api/accounts?user_id=${userId}`);
    const data = await res.json();
    if (!data.ok || !data.accounts.length) {
      list.innerHTML = `<div class="empty-state">
        <div class="empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
        </svg></div>
        <div class="empty-title">No accounts connected</div>
        <div class="empty-sub">Add your first Telegram account below</div>
      </div>`;
      return;
    }
    list.innerHTML = data.accounts.map(a => `
      <div class="account-card">
        ${avatarHtml(a)}
        <div class="account-body">
          <div class="account-name">${escHtml(a.name)}</div>
          ${a.username ? `<div class="account-username">@${escHtml(a.username)}</div>` : ""}
          <div class="account-phone">${escHtml(a.phone)}</div>
          ${a.tg_user_id ? `<div class="account-id">ID: ${escHtml(String(a.tg_user_id))}</div>` : ""}
        </div>
        <button class="remove-btn" onclick="removeAccount('${escHtml(a.phone)}')">Remove</button>
      </div>
    `).join("");
  } catch {
    list.innerHTML = '<div class="empty-state"><div class="empty-title">Failed to load</div><div class="empty-sub">Check your connection and try again</div></div>';
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
    if (data.ok) { showToast("Account removed", "success"); loadAccounts(); }
    else showToast(data.error || "Failed to remove", "error");
  } catch { showToast("Network error", "error"); }
  finally { showLoader(false); }
}

async function sendOtp() {
  const rawPhone = document.getElementById("phone-input").value.trim().replace(/\D/g, "");
  if (!rawPhone || rawPhone.length < 5) { showToast("Enter a valid phone number", "error"); return; }
  if (!userId) { showToast("Open this panel from the bot", "error"); return; }
  currentPhone = currentPrefix + rawPhone;
  showLoader(true);
  try {
    const res = await fetch("/api/send-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentPhone, user_id: userId }),
    });
    const data = await res.json();
    if (data.ok) { showToast("OTP sent", "success"); showStep("step-otp"); }
    else showToast(data.error || "Failed to send OTP", "error");
  } catch { showToast("Network error", "error"); }
  finally { showLoader(false); }
}

async function verifyOtp() {
  const code = document.getElementById("otp-input").value.trim();
  const password = document.getElementById("password-input").value.trim();
  if (!code) { showToast("Enter the verification code", "error"); return; }
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
      const meta = [];
      if (data.username) meta.push("@" + data.username);
      if (data.tg_user_id) meta.push("ID: " + data.tg_user_id);
      meta.push(data.phone);
      document.getElementById("success-meta").textContent = meta.join("  ·  ");
      showScreen("success-screen");
    } else if (data.error === "2FA_REQUIRED") {
      document.getElementById("step-2fa").style.display = "flex";
      document.getElementById("step-2fa").style.flexDirection = "column";
      showToast("Enter your 2FA password", "");
    } else {
      showToast(data.error || "Verification failed", "error");
    }
  } catch { showToast("Network error", "error"); }
  finally { showLoader(false); }
}

populateCountries();
loadAccounts();
