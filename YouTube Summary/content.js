// content.js

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "ExtractInfo") {
        // Perform your information extraction logic here

        // As an example, let's say you want to extract the video title
        const videoTitle = document.querySelector('h1.title').textContent;

        // Creating an information object to send as a response
        const info = {
            title: videoTitle
            // You can add more properties as needed
        };

        // Send the extracted information back to the sender (e.g., popup.js or background.js)
        sendResponse(info);
    }
});
