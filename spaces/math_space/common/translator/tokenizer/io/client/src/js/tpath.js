console.log("log tpath.js");

function Path(){
    var self = this;

    this.make_path = function(){
	var str = ('<div id="div_path">'
		   + 'new path: <input id="path_value" type="text" name="path"><br>'
		   + '<input id="set_up_path" type="button" value="set up path"><br>'
		   + 'current path: <div id="div_path_result"></div>'
		   + '</div>');
    
	$("#div_scene").html(str);
	self.get_path();
	self.set_path();
    };

    this.get_path = function(){

	// FOR get path:
	$.ajax(
	    {
		url: 'api/tables/path',
		method: 'GET',
		
		success: function (jsonResponse) {
		    
		    var objresponse = JSON.parse(jsonResponse);
		    data = objresponse['path'];
		
		    console.log("path:");
		    console.log(data);
		    $("#div_path_result").text(data);
		    },
		
		error: function () {
		    console.log("error to get");
		}
	    });
	// END FOR
    };

    this.set_path = function(){
	
	$("#set_up_path").on("click", function(event){
	    var to_send = JSON.stringify({path: $("#path_value").val()});
	    console.log("to_send:")
	    console.log(JSON.stringify(to_send))

	    $.ajax(
		{
		    url: 'api/tables/path',
		    type: 'POST',
		    data: to_send,

		    success: function(jsonResponse){
			
			// send
			var objresponse = JSON.parse(jsonResponse);
			data = objresponse['path'];
			console.log("\ndata");
			console.log(data);
			
			// update div_path_result:
			$("#div_path_result").text(data);
			// $("#div_path_result").show();
		    },
		    
		    error: function () {
			console.log("error to send");
		    }
		});
	});
    };
};
