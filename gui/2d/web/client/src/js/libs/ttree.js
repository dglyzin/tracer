console.log("log ttree.js");


define(['require', 'jquery', 'jquery-ui-custom/jquery-ui',
	'fancytree/modules/jquery.fancytree', 'tmenu', 'tinput'],
       function(require, $, ui, fancytree, tmenu){

	   // jquery_ui = require('jquery-ui-custom/jquery-ui');
	   fancytree = require('fancytree/modules/jquery.fancytree');

	   function Tree(options){

	       /*Create tree with context menu in it.
		
		Input:
		
		-- ``activator(event, data)`` - function, that define
		what hapend if user click right button.

		-- ``menu_items, menu_tooltips, menu_callbacks`` - for menu.

		-- ``tree_data, url`` - if tree_data is not specified,
		url will be used for ajax to get it.
		*/

	       options || (options = {});

	       var self = this;
	       // self.net = net;

	       self.tree_div_id = options["tree_div_id"];
	       self.menu_div_id = options["menu_div_id"];
	       self.input_div_id = options["input_div_id"];

	       console.log('options["menu_shift"]=', options["menu_shift"]);
	       self.menu_shift = options["menu_shift"]?options["menu_shift"]:0;

	       // FOR activate:
	       self.activator = options["activator"];
	       // END FOR

	       // FOR menu:
	       self.menu_items = options["menu_items"];
	       self.menu_tooltips = options["menu_tooltips"];

	       // dict, whose keys must be equal to ``self.manu_items``:
	       self.menu_callbacks = options["menu_callbacks"];

	       self.menu = new tmenu.Menu(self.menu_div_id, self.input_div_id,
					  self.menu_items,
					  self.menu_tooltips,
					  self.menu_callbacks);
	       
	       // END FOR

	       
	       // FOR init data:
	       
	       if ("tree_data" in options){
		
		   var init_data = options["tree_data"];
		   self.create_tree(init_data);
	       }
	       else
		   if ("url" in options){
		       
		       self.set_tree_from_server(options["url"]);
		       // self.init_data = server_respounse;
		   }		   
	       // END FOR
	   }

	   // FOR server side:
	   Tree.prototype.set_tree_from_server = function(url){
	       
	       /*Take data from url and use it for creating tree*/

	       var self = this;
	       var to_send = {mode: "init"};
	       var succ = function(data){
		   var init_data = data["tree"];
		   console.log("set_tree_from_server init_data:");
		   console.log(init_data);
		   self.create_tree(init_data);
	       };
	       this.send_data(url, to_send, succ);
	   };
	   
	   Tree.prototype.add_node_server = function(url, node_name, is_folder, node_data){
	       
	       /*Add node in js and server.*/

	       var self = this;

	       // add node to js tree:
	       self.add_node(node_name, is_folder);
	       
	       // convert to json and send to server:
	       var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "add",
			      node_name: node_name, is_folder: is_folder,
			      node_data: node_data,
			      tree: tree};
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };

	   Tree.prototype.rename_node_server = function(url, node_name){
	       var self = this;

	       // rename node to js tree:
	       self.rename_selected_node(node_name);

	       // convert to json and send to server:
	       var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "rename",
			      node_name: node_name,
			      tree: tree};
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };

	   Tree.prototype.remove_node_server = function(url){
	       
	       /* Remove selected and put children nodes to common parent.
		Report to server.*/

	       var self = this;

	       // remove selected node to js tree:
	       var node_name = self.remove_selected_node();
	       
	       // convert to json and send to server:
	       var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "remove",
			      node_name: node_name,
			      tree: tree};
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };


	   Tree.prototype.rewrite_node_server = function(url, node_data){

	       /* Use selected node as storage for current model.
		Report to server.*/

	       var self = this;

	       var node = self.get_selected_node();

	       // convert to json and send to server:
	       var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "rewrite",
			      node_name: node.title,
			      node_data: node_data,
			      tree: tree};
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };

	   Tree.prototype.convert_tree_to_dict = function(){
	       var self = this;

	       // Convert the whole tree into an dictionary
	       var tree = $(self.tree_div_id).fancytree("getTree");
	       var d = tree.toDict(true);
	       return(JSON.stringify(d));
	   };
	   
	   Tree.prototype.send_data = function(url, to_send, succ){

	       /*
		-- ``succ`` - if given, will be called after success
		with data as arg.
		*/
	       console.log("send_data to_send:");
	       console.log(to_send);
	       $.ajax(
		   {
		       url: url,
		       type: 'POST',
		       data: JSON.stringify(to_send),
			   
		       success: function (jsonResponse) {
			   var objresponse = JSON.parse(jsonResponse);
			   
			   var data = objresponse;
			   console.log("\ndata_successfuly_recived:");
			   console.log(data);
			   // to_send["result"] = data;
			   if (succ)
			       succ(data);
		       },

		       error: function (data) {
			   console.log("error to send");
			   console.log(data);
		       }
		   });
	       
	   };
	   // END FOR

	   // FOR node editing:
	   Tree.prototype.add_node = function(name, is_folder){
	       
	       /* Add node to js tree. */

	       var self = this;
	       
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   node = $(self.tree_div_id).fancytree("getRootNode");
	       console.log("node = ", node);
	       
	       /*
	       if (!self.active_node)
		   return;
		var node = self.active_node;
		*/
	      
	       node.addChildren({title: name, folder: is_folder});
	       console.log("done");
	       //node.fromDict({title: node.title,
	       //children: [{title: name, folder: is_folder}]});
	   };
	   
	   
	   Tree.prototype.remove_selected_node = function(){
	       
	       /*And keep children.*/

	       var self = this;

	       /*
	       if (!self.active_node)
		   return;
		*/
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;
	       while( node.hasChildren() ) {
		       node.getFirstChild().moveTo(node.parent, "child");
		   }
	       var title = node.title;
	       node.remove();
	       return(title);
	       /*
	       var tree = $(self.tree_div_id).fancytree("getTree"),
		   selNodes = tree.getSelectedNodes();
	       console.log("selNodes = ", selNodes);
		
	       selNodes.forEach(function(node) {
		   while( node.hasChildren() ) {
		       node.getFirstChild().moveTo(node.parent, "child");
		   }
		   node.remove();
	       });
		*/
	   };
	   

	   Tree.prototype.rename_selected_node = function(name){

	       /* In js tree. */

	       var self = this;
	       
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;

	       /*
	       if (!self.active_node)
		   return;
		*/
	       node.setTitle(name);
	   };
	   Tree.prototype.get_selected_node = function(){
	       var self = this;
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;
	       return(node);
	   };
	   // REF: http://wwwendt.de/tech/fancytree/demo/#sample-api.html
	   // END FOR


	   Tree.prototype.create_tree = function(init_data){

	       /*Create tree with contextmenu.*/

	       var self = this;

	       

	       var original_tree_div_id = self.tree_div_id.slice(1);
	       console.log("self.tree_div_id = ", self.tree_div_id);
	       
	       // prevent default:
	       document.getElementById(original_tree_div_id)
		   .addEventListener("contextmenu", function(event){
		       event.preventDefault();
		       console.log("event prevent = ", event);
		       
		   }, false);

	       // remove menu on left click:
	       document.getElementById(original_tree_div_id)
		   .addEventListener("click", function(event){
		       self.menu.update_remove();
		       
		   }, false);

	       $(self.tree_div_id).fancytree({
		   /*
		   click: function(event, data){
		       console.log("event click = ", event);
		       // self.menu.update_remove();
		   },
		    */
		   source: init_data,
		   checkbox: true,

		   activate: function(event, data){
		       console.log("data.node:");
		       console.log(data.node);
		       $(data.node).addClass("ui-state-focus ui-state-active");
		       self.activator(event, data);
		       self.active_node = data.node;
		   },
		   deactivate: function(event, data){
		       $(data.node).removeClass("ui-state-focus ui-state-active");
		       self.active_node = undefined;
		   }
	       }).on("contextmenu", function(event, data){
		   
		   /*Create menu on right click.*/

		   console.log("event contextmenu = ", event);
		   var tree = $(self.tree_div_id).fancytree("getTree");
		   var d = tree.toDict(true);
		   console.log(JSON.stringify(d));
		   var x = event.originalEvent.clientX;
		   var y = event.originalEvent.clientY;
		   console.log("x, y = ", [x,y]);
		   console.log("self.menu_shift = ", self.menu_shift);

		   self.menu.update(x, y+self.menu_shift);
		   
	       });	       
	   };

	   return {
	       Tree: Tree
	   }});
