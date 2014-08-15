
var ws;
var userCnt = {{ n_connections }};
var userID=userCnt;
var selectedElement = 0;
var currentX = 0;
var currentY = 0;
var mode = 0;
var Name = 0;

function btn_send_message(){
    var canvas = document.getElementById('canvas');
    var msg  = document.getElementById("message").value;
    data = new Array(userID, userCnt, Name, mode, currentX, currentY, msg);
    ws.send( data.join(',') );
}
window.onload = function(){
    console.log('start Server Acessing');
    if ("WebSocket" in window) {
        ws = new WebSocket("ws://localhost:8888/websocket");
        ws.onopen = function() {
            document.getElementById("enter").disabled = false;
            var canvas = document.getElementById('canvas');
            for(var i=0; i < userCnt; i++){
                canvas.appendChild(createUser('unknown', 'Yo!', 'black', i));
            }
        };
        ws.onmessage = function(message) {
            updateUser(message)
            var txtNode = document.createTextNode(message.data);
            var brNode = document.createElement('br');
            var cnode = document.getElementById("content");
            cnode.appendChild(txtNode);
            cnode.appendChild(brNode);
        };
        document.getElementById("enter").onclick = function(){
            var canvas = document.getElementById('canvas');
            var name = document.getElementById("name").value;
            var msg  = document.getElementById("message").value;
            canvas.appendChild(
                    createUser(name, msg, 'red', userID));
            userID = userCnt ;

            Name = name;
            document.getElementById("enter").onclick = btn_send_message
            btn = document.getElementById("enter");
            btn.value = 'Send'

            data = new Array(userID, userCnt, Name, mode, currentX, currentY, msg);
            console.log(data.join(','));
            ws.send( data.join(',') );
            document.getElementById("name").disabled = true;
        };
    }else{
        alert("You have no web sockets");
    };
};
window.onunload = function() {ws.close();};
