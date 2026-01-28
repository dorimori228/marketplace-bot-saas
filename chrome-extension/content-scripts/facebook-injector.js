/**
 * Facebook Content Script
 * Injects into Facebook pages - can be used for future features
 * Currently monitors session and provides helper functions
 */

console.log('🔵 Facebook Marketplace Automation - Content script loaded');

// Monitor if user is logged in
function checkFacebookSession() {
    // Check if user is logged in by looking for specific DOM elements
    const userNavigation = document.querySelector('[aria-label="Account"]') ||
                          document.querySelector('[data-click="profile_icon"]');

    return !!userNavigation;
}

// Send session status to background script
function reportSessionStatus() {
    const isLoggedIn = checkFacebookSession();

    chrome.runtime.sendMessage({
        action: 'sessionStatus',
        isLoggedIn: isLoggedIn
    });
}

// Check session on page load
if (document.readyState === 'complete') {
    reportSessionStatus();
} else {
    window.addEventListener('load', reportSessionStatus);
}

/**
 * Helper function to detect if we're on a marketplace page
 */
function isMarketplacePage() {
    return window.location.href.includes('marketplace.facebook.com') ||
           window.location.href.includes('facebook.com/marketplace');
}

/**
 * Future feature: Auto-fill listing form
 * This can be used when implementing direct form filling from extension
 */
function autoFillListingForm(data) {
    if (!isMarketplacePage()) {
        console.warn('Not on marketplace page');
        return false;
    }

    // Find form fields and auto-fill
    // Implementation would go here for future features
    console.log('Auto-fill functionality - to be implemented');

    return true;
}

/**
 * Future feature: Extract listing data from current page
 */
function extractListingData() {
    if (!isMarketplacePage()) {
        return null;
    }

    // Extract listing data from page
    // Useful for copying existing listings
    console.log('Extract listing functionality - to be implemented');

    return null;
}

// Make functions available to extension
window.marketplaceAutomation = {
    checkSession: checkFacebookSession,
    isMarketplace: isMarketplacePage,
    autoFill: autoFillListingForm,
    extractData: extractListingData
};

// Listen for messages from extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkSession') {
        sendResponse({ isLoggedIn: checkFacebookSession() });
        return true;
    }

    if (request.action === 'extractListingData') {
        sendResponse({ data: extractListingData() });
        return true;
    }
});

console.log('✅ Content script ready');
