document.addEventListener('DOMContentLoaded', function() {
    const summaryElement = document.getElementById('summary');
    const readAloudButton = document.getElementById('read-aloud-btn');
    const closeButton = document.getElementById('close-btn');
    let currentSummary = '';

    function readSummaryAloud() {
        chrome.tts.speak(currentSummary, {'rate': 1.0});
    }

    function closePopup() {
        window.close(); // Closes the popup
    }

    // Fetch and display summary
    chrome.runtime.sendMessage({action: "getSummary"}, function(response) {
        if (response.summary) {
            currentSummary = response.summary;
            summaryElement.textContent = response.summary;
        } else {
            summaryElement.textContent = 'Failed to load summary.';
        }
    });

    // Event listeners
    readAloudButton.addEventListener('click', readSummaryAloud);
    closeButton.addEventListener('click', closePopup);
});
