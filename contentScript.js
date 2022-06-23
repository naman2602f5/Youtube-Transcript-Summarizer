let resultText;
let tab_id;
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse){
    if(request.todo == "Summarize")
    {
        //call the api to summarize the text

          var oReq = new XMLHttpRequest();
          console.log(request);
          console.log(sender);

          oReq.open("GET", "http://127.0.0.1:5000/api/summarize?youtube_url="+request.url+"&choice="+request.type+"&percent="+request.percent, true);

          oReq.onreadystatechange = function() {
            if (oReq.readyState == 4 && oReq.status == 200) {
              // textContent does not let the attacker inject HTML elements.
              if(oReq.status == 200){
                resultText = oReq.response;
                console.log(resultText);
                sendResponse({summary: resultText});
              }
            }
          }
          oReq.send();
          return true;
    }
});

