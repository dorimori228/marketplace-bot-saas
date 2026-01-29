/**
 * Background Service Worker
 * Handles background tasks, cookie extraction, and communication between components
 */

console.log('🔧 Service Worker initialized');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Message received:', request.action);

    if (request.action === 'extractCookies') {
        extractFacebookCookies()
            .then(cookies => {
                sendResponse({ success: true, cookies });
            })
            .catch(error => {
                sendResponse({ success: false, error: error.message });
            });

        return true; // Keep channel open for async response
    }

    if (request.action === 'syncCookies') {
        // Auto-sync cookies in background
        syncCookiesWithBackend(request.accountId)
            .then(() => {
                sendResponse({ success: true });
            })
            .catch(error => {
                sendResponse({ success: false, error: error.message });
            });

        return true;
    }
});

/**
 * Extract Facebook cookies from browser
 */
async function extractFacebookCookies() {
    const domain = '.facebook.com';

    // Essential cookie names for Facebook authentication
    const essentialCookies = [
        'c_user',      // User ID
        'xs',          // Session token
        'datr',        // Browser identifier
        'sb',          // Secure browsing token
        'fr',          // Facebook tracking
        'presence'     // Online status
    ];

    try {
        // Get all cookies from facebook.com domain
        const allCookies = await chrome.cookies.getAll({ domain });

        if (!allCookies || allCookies.length === 0) {
            throw new Error('No Facebook cookies found. Please login to Facebook first.');
        }

        // Filter and format cookies
        const cookies = allCookies
            .filter(cookie => {
                // Include essential cookies and any fbm_* or fbsr_* cookies
                return essentialCookies.includes(cookie.name) ||
                       cookie.name.startsWith('fbm_') ||
                       cookie.name.startsWith('fbsr_');
            })
            .map(cookie => ({
                name: cookie.name,
                value: cookie.value,
                domain: cookie.domain,
                path: cookie.path,
                expires: cookie.expirationDate,
                httpOnly: cookie.httpOnly,
                secure: cookie.secure,
                sameSite: cookie.sameSite || 'no_restriction'
            }));

        if (cookies.length === 0) {
            throw new Error('No valid Facebook session cookies found');
        }

        // Verify we have the minimum required cookies
        const hasUserCookie = cookies.some(c => c.name === 'c_user');
        const hasSessionCookie = cookies.some(c => c.name === 'xs');

        if (!hasUserCookie || !hasSessionCookie) {
            throw new Error('Missing required authentication cookies. Please login to Facebook.');
        }

        console.log(`✅ Extracted ${cookies.length} Facebook cookies`);
        return cookies;

    } catch (error) {
        console.error('❌ Cookie extraction error:', error);
        throw error;
    }
}

/**
 * Sync cookies with backend
 */
async function syncCookiesWithBackend(accountId) {
    try {
        const cookies = await extractFacebookCookies();

        // Get auth token from storage
        const { authToken } = await chrome.storage.sync.get(['authToken']);

        if (!authToken) {
            throw new Error('Not authenticated');
        }

        // Send to backend
        const API_URL = 'https://web-production-cc17c.up.railway.app/api';
        const response = await fetch(`${API_URL}/accounts/${accountId}/sync-cookies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ cookies })
        });

        if (!response.ok) {
            throw new Error('Failed to sync cookies with backend');
        }

        console.log('✅ Cookies synced with backend');
        return true;

    } catch (error) {
        console.error('❌ Cookie sync error:', error);
        throw error;
    }
}

/**
 * Auto-sync cookies periodically (optional)
 */
function startAutoSync() {
    // Sync cookies every 24 hours
    const SYNC_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours

    setInterval(async () => {
        try {
            const { authToken, accounts } = await chrome.storage.sync.get(['authToken', 'accounts']);

            if (authToken && accounts && accounts.length > 0) {
                console.log('🔄 Auto-syncing cookies...');

                for (const account of accounts) {
                    await syncCookiesWithBackend(account.id);
                }

                console.log('✅ Auto-sync completed');
            }
        } catch (error) {
            console.error('❌ Auto-sync failed:', error);
        }
    }, SYNC_INTERVAL);
}

// Start auto-sync
// startAutoSync();

/**
 * Monitor Facebook tab changes (optional - detect when user logs out)
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('facebook.com')) {
        // Facebook page loaded - could check if cookies are still valid
        console.log('📱 Facebook page loaded');
    }
});

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('🎉 Extension installed!');

        // Open welcome page
        chrome.tabs.create({ url: 'https://your-website.com/welcome' });
    } else if (details.reason === 'update') {
        console.log('🔄 Extension updated');
    }
});
