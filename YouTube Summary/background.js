chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "getSummary") {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            var activeTab = tabs[0];
            var activeTabUrl = activeTab.url;

            if (activeTabUrl.includes("youtube.com/watch")) {
                fetch('http://localhost:5000/summary?url=' + encodeURIComponent(activeTabUrl))
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.error) {
                            sendResponse({summary: 'Error processing summary: ' + data.error});
                        } else {
                            sendResponse({summary: data.summary});
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        sendResponse({summary: 'Error fetching summary: ' + error.message});
                    });
            } else {
                sendResponse({summary: "Not a YouTube video."});
            }
        });

        return true; // Required to use sendResponse asynchronously
    }
    if (request.action === "analyzeComments") {
        console.log("Analyze comments clicked"); // Debug log
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            var activeTab = tabs[0];
            var activeTabUrl = activeTab.url;
            console.log("URL: " + activeTabUrl); // Debug log
    
            if (activeTabUrl.includes("youtube.com/watch")) {
                var fetchUrl = 'http://localhost:5000/analyze_comments?url=' + encodeURIComponent(activeTabUrl);
                console.log("Fetching: " + fetchUrl); // Debug log
    
                fetch(fetchUrl)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => sendResponse({sentiments: data.sentiments}))
                    .catch(error => {
                        console.error('Error:', error);
                        sendResponse({error: 'Error fetching comments: ' + error.message});
                    });
            } else {
                sendResponse({error: "Not a YouTube video."});
            }
        });
        return true; // Required for asynchronous sendResponse
    }
    

});
