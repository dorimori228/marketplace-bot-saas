/**
 * Chrome Extension Popup - Main Logic
 * Handles authentication, listings, and UI state management
 */

// API Configuration
const API_URL = 'https://web-production-cc17c.up.railway.app/api';

// State
let currentUser = null;
let accounts = [];
let authToken = null;

// DOM Elements
const loadingScreen = document.getElementById('loading-screen');
const authScreen = document.getElementById('auth-screen');
const dashboardScreen = document.getElementById('dashboard-screen');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log('🚀 Extension initialized');

    // Check if user is already logged in
    const token = await getStoredToken();

    if (token) {
        authToken = token;
        await loadUser();
    } else {
        showScreen('auth');
    }

    setupEventListeners();
}

// ==================== STORAGE ====================

async function getStoredToken() {
    return new Promise((resolve) => {
        chrome.storage.sync.get(['authToken'], (result) => {
            resolve(result.authToken || null);
        });
    });
}

async function setStoredToken(token) {
    return new Promise((resolve) => {
        chrome.storage.sync.set({ authToken: token }, resolve);
    });
}

async function clearStorage() {
    return new Promise((resolve) => {
        chrome.storage.sync.clear(resolve);
    });
}

// ==================== API CALLS ====================

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const contentType = response.headers.get('content-type') || '';

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`API returned non-JSON (${response.status}): ${text.slice(0, 120)}`);
        }

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ==================== AUTH ====================

async function login(email, password) {
    try {
        const result = await apiCall('/auth/login', 'POST', { email, password });
        authToken = result.access_token;
        await setStoredToken(authToken);
        currentUser = result.user;

        showNotification('Login successful!', 'success');
        await loadUser();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function register(email, password) {
    try {
        const result = await apiCall('/auth/register', 'POST', { email, password });
        authToken = result.access_token;
        await setStoredToken(authToken);
        currentUser = result.user;

        showNotification('Account created successfully!', 'success');
        await loadUser();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function logout() {
    authToken = null;
    currentUser = null;
    await clearStorage();
    showScreen('auth');
    showNotification('Logged out successfully', 'success');
}

async function loadUser() {
    try {
        const result = await apiCall('/auth/me');
        currentUser = result.user;

        // Update UI
        updateDashboard(result.user, result.usage);

        // Load accounts
        await loadAccounts();

        showScreen('dashboard');
    } catch (error) {
        console.error('Failed to load user:', error);
        showNotification(error.message || 'Failed to load user profile', 'error');
        showScreen('auth');
    }
}

// ==================== ACCOUNTS ====================

async function loadAccounts() {
    try {
        const result = await apiCall('/accounts');
        accounts = result.accounts;

        updateAccountSelector();
    } catch (error) {
        console.error('Failed to load accounts:', error);
        showNotification('Failed to load accounts', 'error');
    }
}

function updateAccountSelector() {
    const selector = document.getElementById('account-selector');
    selector.innerHTML = '<option value="">Select account...</option>';

    accounts.forEach(account => {
        const option = document.createElement('option');
        option.value = account.id;
        option.textContent = account.account_name;
        selector.appendChild(option);
    });
}

async function addAccount(accountName, cookies) {
    try {
        await apiCall('/accounts/add', 'POST', {
            account_name: accountName,
            cookies: cookies
        });

        showNotification('Account added successfully!', 'success');
        await loadAccounts();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// ==================== LISTINGS ====================

async function createListing(formData) {
    try {
        const accountId = parseInt(document.getElementById('account-selector').value);

        if (!accountId) {
            showNotification('Please select an account first', 'warning');
            return;
        }

        const listingData = {
            fb_account_id: accountId,
            title: formData.title,
            price: formData.price,
            description: formData.description,
            category: formData.category,
            location: formData.location,
            images: []  // TODO: Add image upload
        };

        const result = await apiCall('/listings/create', 'POST', listingData);

        showNotification('Listing created and queued!', 'success');

        // Clear form
        document.getElementById('listing-form').reset();

        // Reload usage
        await loadUser();
    } catch (error) {
        if (error.message.includes('limit reached')) {
            showNotification('Monthly limit reached! Please upgrade your plan.', 'error');
            showUpgradePrompt();
        } else {
            showNotification(error.message, 'error');
        }
    }
}

// ==================== COOKIE EXTRACTION ====================

async function extractFacebookCookies() {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
            { action: 'extractCookies' },
            (response) => {
                if (response.success) {
                    resolve(response.cookies);
                } else {
                    reject(new Error(response.error || 'Failed to extract cookies'));
                }
            }
        );
    });
}

// ==================== UI UPDATES ====================

function showScreen(screenName) {
    loadingScreen.style.display = 'none';
    authScreen.style.display = 'none';
    dashboardScreen.style.display = 'none';

    switch (screenName) {
        case 'loading':
            loadingScreen.style.display = 'flex';
            break;
        case 'auth':
            authScreen.style.display = 'block';
            break;
        case 'dashboard':
            dashboardScreen.style.display = 'block';
            break;
    }
}

function updateDashboard(user, usage) {
    // Update user email
    document.getElementById('user-email').textContent = user.email;

    // Update tier badge
    const tierBadge = document.getElementById('tier-badge');
    const tierName = tierBadge.querySelector('.tier-name');

    tierName.textContent = user.subscription_tier.charAt(0).toUpperCase() +
                           user.subscription_tier.slice(1);

    tierBadge.className = `tier-badge ${user.subscription_tier}`;

    // Update usage
    if (usage && usage.monthly_listings) {
        const current = usage.monthly_listings.current;
        const limit = usage.monthly_listings.limit;
        const unlimited = usage.monthly_listings.unlimited;

        const usageBar = document.getElementById('usage-bar');
        const usageText = document.getElementById('usage-text');
        const upgradeBtn = document.getElementById('upgrade-btn');

        if (unlimited) {
            usageBar.style.width = '0%';
            usageText.textContent = `${current} listings this month (Unlimited)`;
            upgradeBtn.style.display = 'none';
        } else {
            const percentage = (current / limit) * 100;
            usageBar.style.width = `${percentage}%`;
            usageText.textContent = `${current} / ${limit} listings this month`;

            // Color coding
            if (percentage >= 90) {
                usageBar.classList.add('danger');
            } else if (percentage >= 70) {
                usageBar.classList.add('warning');
            }

            // Show upgrade button if near limit
            if (percentage >= 80 && user.subscription_tier !== 'premium') {
                upgradeBtn.style.display = 'block';
            }
        }
    }

    // Enable/disable feature buttons based on tier
    const batchRelistBtn = document.getElementById('batch-relist-btn');
    const templatesBtn = document.getElementById('templates-btn');

    if (usage && usage.features) {
        if (usage.features.batch_operations) {
            batchRelistBtn.disabled = false;
            batchRelistBtn.querySelector('.lock-icon').style.display = 'none';
        }

        if (usage.features.templates) {
            templatesBtn.disabled = false;
            templatesBtn.querySelector('.lock-icon').style.display = 'none';
        }
    }
}

function showNotification(message, type = 'info') {
    const toast = document.getElementById('notification-toast');
    const messageEl = document.getElementById('notification-message');

    messageEl.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function showUpgradePrompt() {
    const upgradeBtn = document.getElementById('upgrade-btn');
    upgradeBtn.style.display = 'block';
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Auth tabs
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const tab = btn.dataset.tab;
            document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
            document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';
        });
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        await login(email, password);
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        await register(email, password);
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Add account
    document.getElementById('add-account-btn').addEventListener('click', () => {
        document.getElementById('add-account-modal').style.display = 'flex';
    });

    document.getElementById('cancel-add-account-btn').addEventListener('click', () => {
        document.getElementById('add-account-modal').style.display = 'none';
    });

    document.getElementById('auto-detect-cookies-btn').addEventListener('click', async () => {
        try {
            showNotification('Extracting cookies...', 'info');
            const cookies = await extractFacebookCookies();
            const accountName = document.getElementById('new-account-name').value || 'My Account';

            await addAccount(accountName, cookies);

            document.getElementById('add-account-modal').style.display = 'none';
            document.getElementById('new-account-name').value = '';
        } catch (error) {
            showNotification(error.message, 'error');
        }
    });

    // Create listing
    document.getElementById('listing-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            title: document.getElementById('listing-title').value,
            price: document.getElementById('listing-price').value,
            description: document.getElementById('listing-description').value,
            category: document.getElementById('listing-category').value,
            location: document.getElementById('listing-location').value
        };

        await createListing(formData);
    });

    // Upgrade button
    document.getElementById('upgrade-btn').addEventListener('click', () => {
        chrome.tabs.create({ url: 'https://your-website.com/pricing' });
    });

    // Visit website
    document.getElementById('visit-website').addEventListener('click', (e) => {
        e.preventDefault();
        chrome.tabs.create({ url: 'https://your-website.com' });
    });

    // Support link
    document.getElementById('support-link').addEventListener('click', (e) => {
        e.preventDefault();
        chrome.tabs.create({ url: 'https://your-website.com/support' });
    });

    // Batch relist (Pro+ feature)
    document.getElementById('batch-relist-btn').addEventListener('click', () => {
        showNotification('Batch relist feature coming soon!', 'info');
    });

    // Templates (Pro+ feature)
    document.getElementById('templates-btn').addEventListener('click', () => {
        showNotification('Templates feature coming soon!', 'info');
    });

    // Analytics
    document.getElementById('analytics-btn').addEventListener('click', () => {
        showNotification('Analytics feature coming soon!', 'info');
    });
}
