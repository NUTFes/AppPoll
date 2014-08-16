function init() {
    var ws = new WebSocket('ws://localhost:8888/data')
    ws.onopen = function(){
    };
    ws.onerror = function(error){
    };
    ws.onmessage = function(msg){
    };
}

function Run(){
    init();
}

Run(); 
