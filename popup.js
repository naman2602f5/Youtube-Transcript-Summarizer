const summarize_button = document.getElementById("summarize");
const percent_dropdown = document.getElementById('percent-dropdown');
const choice_dropdown = document.getElementById('summary-dropdown');

// Making Summarize button disabled on start
summarize_button.disabled = true;

// Adding EventListeners on both dropdowns to enable button when both dropdowns have selected a valid choice.
percent_dropdown.addEventListener("change", buttonUpdate);
choice_dropdown.addEventListener("change", buttonUpdate);


function buttonUpdate() {

    if(choice_dropdown.selectedIndex == 3)
    {
        summarize_button.disabled = false;
    }
    else
    {
        summarize_button.disabled = ((percent_dropdown.selectedIndex <= 0 || choice_dropdown.selectedIndex <= 0));
    }
}

function parse_choice(choice_index) {
    switch (choice_index) {
        case 1:
            return "freq-based";
        case 2:
            return "luhn-algo";
        case 3:
            return "abstractive";
    }
}

document.getElementById('summarize').onclick = function()
{
    document.getElementById('contents').style.visibility="hidden";
    document.getElementById('load-icon').style.visibility="visible";
    

    let percent_value = percent_dropdown.options[percent_dropdown.selectedIndex].text;
    let choice_index = choice_dropdown.selectedIndex;

    const percent = percent_value.split("%")[0];
    const choice = parse_choice(choice_index);
    
    //Message Passing -> Notify contentScript.js to execute summary generation
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
        var tab_id = tabs[0].id;
        var tab_url = tabs[0].url;
        chrome.tabs.sendMessage(tab_id, {todo: "Summarize", url: tab_url, percent:percent, type:choice}, function (message) {

            let summarized_text = message.summary;
            document.getElementById("contents").innerHTML ="<b>Summarized Text: </b>"+"<br>"+summarized_text;
            document.getElementById('load').remove();
            document.getElementById('contents').style.visibility="visible";
            console.log(message.summary);
        });
    });
}
