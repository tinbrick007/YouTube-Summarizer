document.addEventListener('DOMContentLoaded', function() {
    const summaryElement = document.getElementById('summary');
    const readAloudButton = document.getElementById('read-aloud-btn');
    const analyzeCommentsButton = document.getElementById('analyze-comments-btn');
    const sentimentResultsElement = document.getElementById('sentiment-results');
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

    // Event listener for the analyze comments button
    analyzeCommentsButton.addEventListener('click', function() {
        sentimentResultsElement.innerHTML = '<p>Loading comments analysis...</p>';
        
        chrome.runtime.sendMessage({action: "analyzeComments"}, function(response) {
            if(response.error) {
                sentimentResultsElement.innerHTML = `<p>Error: ${response.error}</p>`;
            } else if (response.sentiments && response.sentiments.length > 0) {
                let resultsHtml = response.sentiments.map(sentiment => 
                    `<p>${sentiment}</p>`).join('');
                sentimentResultsElement.innerHTML = resultsHtml;
            } else {
                sentimentResultsElement.innerHTML = '<p>No comments found or no sentiments detected.</p>';
            }
        });
    });

    // Event listeners
    readAloudButton.addEventListener('click', readSummaryAloud);
    closeButton.addEventListener('click', closePopup);
});
