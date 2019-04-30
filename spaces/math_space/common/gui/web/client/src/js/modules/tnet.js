console.log("log tnet.js");


define(['jquery', 'cytoscape/cytoscape.min', "modules/tmenu"],
       function($, cytoscape, tmenu){

	   return {
	       Net: function Net(){
      
		   // FOR global variables:
		   
		   var self = this;

		   // FOR menu:
		   self.menu_status = 0;
		   menu_items = ["add term to db", ""];
		   menu_tooltips = ["TODO_0", "TODO_1"];

		   self.menu = new tmenu.Menu(menu_items, menu_tooltips);
		   console.log("self.menu:");
		   console.log(tmenu);
			       
		   // END FOR
		   // FOR net
		   // var cy;
		   
		   self.remove_net = function(){
		       $("#cy").remove();
		       self.menu.menu_remove();
		   },

		   self.create_net = function(input_data){
		       if(input_data == undefined){
			   data = [
			       {group: "nodes", data: { id: "n1", weight: 75, label: "D[U,{x,2}]"},
				position: { x: 300, y: 300}},
			       {group: "nodes", data: { id: "n2", weight: 35, label:"D[U,{y,2}]"},
				position: { x: 500, y: 300}},
			       {group: "nodes", data: { id: "n3", weight: 35, label:"+"},
				position: { x: 400, y: 100}},
			       {group: "edges", data: { id: "e0", source: "n3", target: "n1",
							label: "e0"}},
			       {group: "edges", data: { id: "e1", source: "n3", target: "n2",
							label: "e1"}}];
		       }else{
			   data = input_data;
		       };
		       console.log("data");
		       console.log(data);

		       // for create net region:
		       console.log("create cy div");
		       var str = ('<div id="cy"> </div>');
		       $("#cy_div").html(str);
		       $("#cy_div").addClass("#cy");
		       console.log("cy div created");
		       fetch('static/src/css/cy-style.json', {mode: 'no-cors'}) //
			   .then(function(res) {
			       return res.json()
			   })
			   .then(function(style){
			       self.cy = cytoscape({
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
			       
			       self.cy.add(data);
			       
			       self.cy.style().selector('edge:selected').css({"background-color": "black"}).update();
			       //cy.style().selector('node:selected').css({"background-color": "black"}).update();
			       
			       // cy.style().selector('edges:selected').css({"background-color": "black"}).update();
			       self.cy.forceRender();
			       
			       self.menu_status = 0;

			       self.cy.on("tap", "node", function(event){
				   console.log("node right click");
				   elm = event.target;
				   
				   console.log(elm.data());
				   console.log("slambda_only:");
				   console.log($("#slambda_only").is(":checked"));
				   // console.log($("#slambda_only").data());

				   data = JSON.stringify(elm.data());
				   console.log("data[slambda]:");
				   console.log((data));
				   
				   if ($("#slambda_only").is(":checked")){
				       if ("nx_data" in elm.data() && elm.data()["nx_data"]){
					   console.log(elm.data()["nx_data"]);
					   if ("slambda" in elm.data()["nx_data"]){
					       console.log(JSON.stringify(elm.data()["nx_data"]["slambda"]));
					       $("#node_data").text(JSON.stringify(elm.data()["nx_data"]["slambda"]));
					   }else{
					       $("#node_data").text("no slambda for node");
					   }
				       }else{
					   $("#node_data").text("no nx_data for node");
				       }
				   }else{
				       $("#node_data").text(data);
				   }
				   console.log("selected:");
				   console.log(self.cy.$(":selected"));
				   
			       });
			       
			       self.cy.on("cxttap", "node", function(event){
				   console.log("cxttap");
				   
				   elm = event.target;

				   // var offset = $("#main").offset();
				   // var x0 = offset.left;
				   // var y0 = offset.top;
		       
				   // console.log("position of main:");
				   // console.log([x0, y0]);
		       
				   // var offset1 = $("#cy").offset();
				   // var x01 = offset1.left;
				   // var y01 = offset1.top;
				   
				   // console.log("position of cy:");
				   // console.log([x01, y01]);
		   
				   console.log(elm);
				   console.log("event");
				   console.log(event);

				   var node_pos_x = event.position["x"];
				   var node_pos_y = event.position["y"];
				   
				   console.log("node_pos: ");
				   console.log([node_pos_x, node_pos_y]);
				   
				   var pan_offset = self.cy.pan();
				   console.log("pan_offset: ");
				   console.log(pan_offset);
				   var pan_offset_x = pan_offset["x"];
				   var pan_offset_y = pan_offset["y"];
				   console.log("pan_offset: ");
				   console.log([pan_offset_x, pan_offset_y]);

				   var cy_offset = $("#cy").offset();
				   var cy_offset_x = cy_offset.left;
				   var cy_offset_y = cy_offset.top;
		       
				   var x = cy_offset_x + pan_offset_x + node_pos_x;
				   var y = cy_offset_y + pan_offset_y + node_pos_y;
				   console.log("cy_offset + pan_offset + node_pos: ");
				   console.log([x, y]);
				   
				   if(self.menu_status == 0){
				       console.log(self);
				       self.menu.menu_create(x, y);
				       self.menu_status = 1;
				   }else if(self.menu_status == 1){
				       // menu_hide();
				       self.menu.menu_remove();
				       self.menu_status = 2;
				   }else if(self.menu_status == 2){
				       // menu_show(event);
				       self.menu.menu_create(x, y);
				       self.menu_status = 1;
				   };
			       });
			       
			       self.cy.on("tap", function(event){
				   console.log("tap");
				   
				   elm = event.target;
				   console.log(elm);
				   console.log("event");
				   console.log(event);
				   var clientX = event.position["x"];
				   var clientY = event.position["y"];
				   
				   console.log("clientX, clientY: ");
				   console.log([clientX, clientY]);
				   if(self.menu_status == 1){
				       // menu_hide();
				       self.menu.menu_remove();
				       self.menu_status = 2;
				   };
			       });
			       
			       console.log("net created");
			       console.log(self.cy.elements().jsons());
			       
			       var src = ('<input id="button_net_send" type="button"'
					  + ' value="send net" class="ui-button">'
					  + '<input id="button_net_get" type="button"'
					  + ' value="get net" class="ui-button">');
			       			       
			       $("#cy_scene_right").addClass("demo_right");
			       $("#cy_scene_right").html(src);
			       

			       $("#button_net_send").on("click", function(event){
				   self.net_to_server();
			       });
			       $("#button_net_get").on("click", function(event){
				   self.net_from_server();
			       });	    
			       // 
			       var src = ('<div id="node_data"' 
					  + ' class="style_editor_static editor_overflow">'
					  + 'click on node for data'
					  + '</div>');

			       var text_node_data = $(src);
			       $("#cy_scene_right").append(text_node_data);


			       //var last_top = $(".editors_above_net_left").last().css("top")
			       // buttons.addClass(".editors_above_net_left");
			       // buttons.css("top", "70px");
			       
			       // $("#cy_texts").html(src);

			   });
		      
		   };
		   
		   
		   self.net_from_server = function(){
		       
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
				   self.cy.add(data);
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
		   
		   
		   self.net_to_server = function(){
		       
		       var data_to_send = self.cy.elements().jsons();
		       
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
		   
		   // END FOR
	       }
	   }
       });
