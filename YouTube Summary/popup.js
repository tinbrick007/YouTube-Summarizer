document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('summary').textContent = 'Loading summary...';

    // Send message to background script to get summary
    chrome.runtime.sendMessage({action: "getSummary"}, function(response) {
        if (response.summary) {
            document.getElementById('summary').textContent = response.summary;
        } else {
            document.getElementById('summary').textContent = 'Failed to load summary.';
        }
    });
});
