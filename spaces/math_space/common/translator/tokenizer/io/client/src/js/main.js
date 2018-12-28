$( document ).ready(function() {

    // FOR import scripts:
    var imports = ["http://localhost:8888/static/src/js/scene.js",
		   "http://localhost:8888/static/src/js/ttable.js",
		   "http://localhost:8888/static/src/js/tables.js",
		   "http://localhost:8888/static/src/js/tpath.js",
		   "http://localhost:8888/static/src/js/path.js"];
    // "http://localhost:8888/static/src/js/net.js"
    // "http://localhost:8888/static/src/js/tree.js",
		   

    var importer = function(imports){
	/*
	  DESCRIPTION:
	  Import scripts from ajax reqursivery.
	*/

	if (imports.length == 0)
	    {
		console.log( "Load was performed." );
		return;
	    }
	    	
	var first = imports.shift();
	
	$.ajax({
	    url: first,
	    dataType: "script",
	    success: function( data, textStatus, jqxhr ) {
		// console.log( data ); // Data returned

		// recursion:
		importer(imports);

	    }}).fail(function( jqxhr, settings, exception ) {
		console.log( first + " fail" );
		console.log(exception);
	    });
	};
    
    
    importer(imports);
    
    // END FOR
    
    // FOR tooltip
    $( function() {  
	$( document ).tooltip();
    });
    // END FOR
    

    // FOR menu
    var menu_items = ["add term to db", ""];


    var menu_hide = function(){
	$("#menu").hide();
    };


    var menu_show = function(event_position){
	//$("#menu").menu("option", "position",
	//		{my: "left top", at: "left top",
	//		 of: event_position});
	var x = event_position.position["x"];
	var y = event_position.position["y"];
	console.log("position:");
	console.log([x, y]);
	
	$("#menu").offset({top: y,
			   left: x})
	console.log("menu offset:");
	console.log($("#menu").offset());
	
	// $("#menu").offset({top: clientY, left: clientX})
	
	$("#menu").show();
	console.log("menu offset:");
	console.log($("#menu").offset());
	
    };

    
    var menu_remove = function(){
	$("#menu").remove();
    };


    var menu_create = function(event_position){
	// FOR create menu region:
	var str = ('<ul id="menu" class="ui-menu ui-widget ui-widget-content">'
		   +'</ul>');
	$("#menu_div").html(str);

	var x = event_position.position["x"];
	var y = event_position.position["y"];
	console.log("position:");
	console.log([x, y]);
	
	var offset = $("#cy").offset();
	var x0 = offset.left;
	var y0 = offset.top;
	console.log("position of menu_div:");
	console.log([x0, y0]);
	
	$("#menu").menu();
	$("#menu").offset({top: y0+y+10, left: x0+x+30});
	//$("#menu").offset({top: y, left: x});
	//$("#menu").menu("option", "position",
	//		{x: x, y: y});

	//$("#menu").menu({position: {of: event_position}});
	// $("#menu").menu({position: {my: "left top", at: "left top", of: event_position}});
	console.log("offset:");
	console.log($("#menu").offset());
	// END FOR

	// FOR add new items:
	list_to_add = menu_items;
	var html_list_to_add = $.map(list_to_add, function(elm, id){
	    return('<li class="ui-menu-item ui-widget ui-widget-content" title="todo">'+elm+'</li>');
	});
	$("#menu").append(html_list_to_add.join(""));
	// END FOR

	// FOR define menu events handlers:
	$("#menu").on("menufocus", function(event, ui){
	    $.each(ui, function(id, elm){
		console.log("elm[0]");
		console.log($(elm).style);
		console.log(elm[0].style);
		$(elm).addClass("ui-state-focus ui-state-active");
		//$(elm).css("background-color", "blue");
		// $(elm[0]).css("color", "blue");
		//elm[0].setAttribute("style", "color: blue");
		//elm[0].style.color = "blue";
            });
            console.log(ui);
	});
	$("#menu").on( "menublur", function( event, ui ) {
	    $.each(ui, function(id, elm){
		console.log("elm[0]");
		console.log($(elm).style);
		console.log(elm[0].style);
		$(elm).removeClass("ui-state-focus ui-state-active");
		//$(elm).css("background-color", "blue");
		// $(elm[0]).css("color", "blue");
		//elm[0].setAttribute("style", "color: blue");
		//elm[0].style.color = "blue";
            });
	});
	$("#menu").on("menuselect", function(event, ui){
	    console.log("select");
	});
	// END FOR
	// $("#menu").offset({top: 300, left: 300});
    };


    $("#create_menu").on("click", function(event){
	$("#menu").menu();
    });
    // END FOR


    // FOR net
    var cy;
    var menu_status = 0;

    var create_net = function(){
	fetch('static/src/css/cy-style.json', {mode: 'no-cors'}) //
	    .then(function(res) {
		return res.json()
	    })
	    .then(function(style){
		cy = cytoscape({
		    container: document.getElementById('cy'), // container to render in
		    maxZoom: 1,
		    minZoom: 0.5,
		    layout: {
			name: 'grid',
			idealEdgeLength: 100,
			nodeOverlap: 20,
			refresh: 20,
			fit: true,
			// padding: 30,
			padding: 100,
			
			randomize: false,
			componentSpacing: 100,
			nodeRepulsion: 400000,
			edgeElasticity: 100,
			nestingFactor: 5,
			gravity: 80,
			numIter: 1000,
			initialTemp: 200,
			coolingFactor: 0.95,
			minTemp: 1.0
		    },
		    //boxSelectionEnabled: false,
		    // autounselectify: true, // if true ignore selection
		    selectionType: 'additive',
		    styleEnabled: true,
		    /*
		    elements: {
			nodes: [
			    { data: { id: 'n', label: 'Tap me', selected: true } }
			]
			
		    },*/
		    style: style,
		    //headless: false,

		    //hideEdgesOnViewport: false,
		    //hideLabelsOnViewport: false,

		    ready: function(){
			window.cy = this;
		    }
		});
	    
	    cy.add([
		{group: "nodes", data: { id: "n1", weight: 75, label: "D[U,{x,2}]"},
		 position: { x: 300, y: 300}},
		{group: "nodes", data: { id: "n2", weight: 35, label:"D[U,{y,2}]"},
		 position: { x: 500, y: 300}},
		{group: "nodes", data: { id: "n3", weight: 35, label:"+"},
		 position: { x: 400, y: 100}},
		{group: "edges", data: { id: "e0", source: "n3", target: "n1",
					 label: "e0"}},
		{group: "edges", data: { id: "e1", source: "n3", target: "n2",
					 label: "e1"}}]);
	    
		cy.style().selector('edge:selected').css({"background-color": "black"}).update();
		//cy.style().selector('node:selected').css({"background-color": "black"}).update();
	    
		// cy.style().selector('edges:selected').css({"background-color": "black"}).update();
		cy.forceRender();
		cy.on("cxttap", "node", function(event){
		    console.log("cxttap");
		    
		    elm = event.target;
		    console.log(elm);
		    console.log("event");
		    console.log(event);
		    var clientX = event.position["x"];
		    var clientY = event.position["y"];
		    
		    console.log("clientX, clientY: ");
		    console.log([clientX, clientY]);
		    if(menu_status == 0){
			menu_create(event);
			menu_status = 1;
		    }else if(menu_status == 1){
			// menu_hide();
			menu_remove();
			menu_status = 2;
		    }else if(menu_status == 2){
			// menu_show(event);
			menu_create(event);
			menu_status = 1;
		    };
		});
		cy.on("tap", function(event){
		    console.log("tap");
		    
		    elm = event.target;
		    console.log(elm);
		    console.log("event");
		    console.log(event);
		    var clientX = event.position["x"];
		    var clientY = event.position["y"];
		    
		    console.log("clientX, clientY: ");
		    console.log([clientX, clientY]);
		    if(menu_status == 1){
			// menu_hide();
			menu_remove();
			menu_status = 2;
		    };
		});

		console.log("net created");
		console.log(cy.elements().jsons());

		var str = ('<input id="button_net_send" type="button"'
			   + ' value="send net">'
			   + '<input id="button_net_get" type="button"'
			   + ' value="get net">');
    
		$("#div_scene").html(str);
		$("#button_net_send").on("click", function(event){
		    net_to_server();
		});
		$("#button_net_get").on("click", function(event){
		    net_from_server();
		});	    
	});
    };


    var net_from_server = function(){

	$.ajax(
	    {
		url: 'api/net',
		method: 'GET',
        
		success: function (jsonResponse) {
		    // _fill_scene();
		    
		    var objresponse = JSON.parse(jsonResponse);
		    console.log(objresponse['els']);
		    
		    data = objresponse['els'];
		    console.log("data from server");
		    console.log(data);
		    
		    // FOR add columns and data dicts:
		    /* 
		    // columns example:
		    var columns = [
		    {title:"username", field: "username"},
		    {title:"memoryused", field: "memoryused"},
		    {title:"memorylimit", field: "memorylimit"},
		    {title:"tsused", field: "tsused"},
		    {title:"tslimit", field: "tslimit"},
		    {title:"expirydate", field: "expirydate"}		
		    ];
		    */
		    // add data to net:
		    cy.add(data);
		    /*
	    // for error checking:

	    $.each(data, function(index, value){
		console.log(value['group']);
		if(value['group'] == 'nodes'){
		    cy.add(value);
		}		
	    });
	    $.each(data, function(index, value){
		console.log(value['group']);
		if(value['group'] == 'edges'){
		    cy.add(value);
		}		
	    });
	    */
		    // _make_admin_table(data, columns, data_add, columns_add);
		    console.log("editor.js success");
		},
		error: function () {
		    //$("#responsefield").text("Error to load api");
		    console.log("Error to load api");
		}
	    });
    };


    var net_to_server = function(){

	var data_to_send = cy.elements().jsons();
	    
	// FOR sending data to server:
	if(data_to_send.length){
	    var to_send = JSON.stringify({els: data_to_send});
	    // var to_send = data_to_send;
	    console.log("\n sending");
	    console.log(to_send);
		    
	    $.ajax(
		{
		    url: 'api/net',
		    type: 'POST',
		    data: to_send,

		    success: function (jsonResponse) {
			var objresponse = JSON.parse(jsonResponse);
			data = objresponse['els'];
			console.log("\ndata");
			console.log(data);
			
			// copy data:
			// var data_local = data.slice();
			// $("#div_editor").text(data[0].kernel);
		    },
		    
		    error: function (data) {
			console.log("error to send");
			console.log(data);
		    }
		});
	}
	else{
	    console.log("\n nothing to send");
	};
    };

    var net_id = 0;
    $("#button_net").on("click", function(event){
	if(net_id == 0){
	    create_net();
	    net_id = 1;
	}else{
	    
	    clear_scene();
	    net_id = 0;
	};
    });
    // END FOR

    
});
