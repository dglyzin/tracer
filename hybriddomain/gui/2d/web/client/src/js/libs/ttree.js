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

	       self.container_div_id = options["container_div_id"];
	       self.tree_div_id = options["tree_div_id"];
	       self.menu_div_id = options["menu_div_id"];
	       self.input_div_id = options["input_div_id"];

	       console.log('options["menu_shift"]=', options["menu_shift"]);
	       self.menu_shift = options["menu_shift"]?options["menu_shift"]:[0,0];

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

	   // FOR reload:
	   Tree.prototype.reload_container = function(){
	       
	       /*
		Reload tree container before rewrite tree.

		$("#main_tree").empty(); not work
		TODO:
		use reload winth init_data (as well for menu)
		// var tree = $(self.tree_div_id).fancytree('getTree');
		// tree.reload(init_data);
		// tree.render(true);
		*/
	       var self = this;
	       
	       $(self.tree_div_id).remove();
	       $(self.menu_div_id).remove();
	       $(self.input_div_id).remove();
	       
	       var original_tree_div_id = self.tree_div_id.slice(1);
	       var original_menu_div_id = self.menu_div_id.slice(1);
	       var original_input_div_id = self.input_div_id.slice(1);
	       
	       $(self.container_div_id).append(
		   ('<div id="'
		    + original_tree_div_id
		    + '" class="tree_positioned" style="top: 70px;"></div>'));
	       $(self.container_div_id).append(
		   ('<div id="' + original_menu_div_id + '"></div>'));
	       $(self.container_div_id).append(
		   ('<div id="' + original_input_div_id + '"></div>'));
	   };
	   // END FOR

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

		   // add tree roots:
		   self.roots = data["roots"];
	       };
	       this.send_data(url, to_send, succ);
	   };
	   
	   Tree.prototype.add_node_server = function(url, node, node_data,
						     parent_node, parents_list){
	       
	       /*Add node in js and server.*/

	       var self = this;

	       // add node to js tree:
	       self.add_node(node);
	       
	       // convert to json and send to server:
	       // var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "add",
			      node: node,
			      node_data: node_data,
			      // tree: tree
			      parent: parent_node,
			      parents_list: parents_list
			     };
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };

	   Tree.prototype.rename_node_server = function(url, node, node_name){
	       var self = this;

	       // rename node to js tree:
	       var old_name = self.rename_node(node, node_name);
	       var parents_list = self.get_parents_list(node);

	       var node_dict = node.toDict();

	       // fix old name in old data:
	       node_dict["title"] = old_name;
	       // convert to json and send to server:
	       // var tree = this.convert_tree_to_dict();
	       var to_send = {mode: "rename",
			      node: node_dict,
			      node_data: {title: node_name},
			      // tree: tree
			      parent: {},
			      parents_list: parents_list
			     };
	      
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };

	   Tree.prototype.remove_selected_node_server = function(url, check_empty){
	       
	       /* Remove selected and put children nodes to common parent.
		Report to server.*/

	       var self = this;

	       // remove selected node to js tree:
	       var selected_node = self.get_selected_node();
			
	       var parents_list = self.get_parents_list(selected_node);
			
	       var node = self.remove_selected_node(check_empty);
	       
	       // var tree = this.convert_tree_to_dict();

	       // convert to json and send to server:	       
	       var to_send = {mode: "remove",
			      node: node.toDict(),
			      node_data: {},
			      // tree: tree
			      parent: {},
			      parents_list: parents_list
			     };
	       
	       /*
	       var succ = function(data){
		   self.add_node(node_name, is_folder);
	       };
	       */
	       this.send_data(url, to_send);
	   };


	   Tree.prototype.save_node_server = function(url, node, node_data){

	       /* Use selected node as storage for current model.
		Report to server.
		When clicked at env_content*/

	       var self = this;

	       // var node = self.get_selected_node();
	       var node_dict = node.toDict();
	       node_dict["node_data"] = node_data;

	       var node_parent = self.get_node_parent(node);
	       // var node_parent_dict = node_parent.toDict();
	       var parents_list = self.get_parents_list(node);
	       
	       // convert to json and send to server:
	       // var tree = this.convert_tree_to_dict();
	       
	       var to_send = {mode: "save",
			      node: node_dict,
			      parent: {},
			      parents_list: parents_list};
	       /*
	       var to_send = {mode: "rewrite",
			      node_name: node.title,
			      node_data: node_data,
			      tree: tree};
		*/
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
	   Tree.prototype.get_node_parent = function(node){
	       return(node.parent);
	   };
	   
	   Tree.prototype.get_parents_list = function(node){
	       return($.map(node.getParentList(), function(elm, id){
		   return(elm.title);
	       }));
	   };

	   Tree.prototype.add_node = function(node){
	       
	       /* Add node to js tree. */

	       var self = this;
	       
	       var parent_node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!parent_node)
		   parent_node = $(self.tree_div_id).fancytree("getRootNode");
	       console.log("parent_node = ", parent_node);
	       self.check_node_unique(parent_node, node["title"]);
	       /*
	       if (!self.active_node)
		   return;
		var node = self.active_node;
		*/
	       
	       parent_node.addChildren(node);
	       console.log("done");
	       //node.fromDict({title: node.title,
	       //children: [{title: name, folder: is_folder}]});
	   };
	   
	   Tree.prototype.check_node_unique = function(parent_node, name){
	       /*Check if name is unique in parent_node.children,
		generate error, if not.
		Also remove input, if not.*/

	       var children_titles = $.map(parent_node.children, function(elm, id){
		   return(elm.title);
	       });
	       console.log("children_titles = ", children_titles);
	       console.log("node.title = ", name);
	       // here + "" used for convert int to string, if any:
	       if(children_titles.indexOf(name+"") >= 0){
		   // remove input:
		   self.menu.input.remove_input();
		   // console.error("node with such name alredy exist: "+node["title"]);
		   throw new Error("node with such name alredy exist: "+node["title"]);
	       }

	   };

	   Tree.prototype.remove_selected_node = function(check_empty){
	       
	       /*.*/

	       var self = this;

	       /*
	       if (!self.active_node)
		   return;
		*/
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;
	       if(check_empty)
		   while( node.hasChildren() ) {
		   
		       throw new Error("node not empty!");
		       // And keep children:
		       // node.getFirstChild().moveTo(node.parent, "child");
		   }
	       var title = node.title;
	       node.remove();
	       return(node);
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
	   

	   Tree.prototype.rename_node = function(node, name){

	       /* In js tree. */

	       var self = this;
	       /*
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;
		*/
	       
	       var parent_node = self.get_parent_node(node);
	       self.check_node_unique(parent_node, name);
	       /*
	       if (!self.active_node)
		   return;
		*/
	       var old_name = node.title;
	       node.setTitle(name);
	       return(old_name);
	   };

	   Tree.prototype.get_parent_node = function(node){
	       return(node.parent);
	   };

	   Tree.prototype.get_selected_node = function(){
	       var self = this;
	       var node = $(self.tree_div_id).fancytree("getActiveNode");
	       if(!node)
		   return;
	       return(node);
	   };
	   
	   Tree.prototype.get_root_node = function(){
	       var self = this;
	       return($(self.tree_div_id).fancytree("getRootNode"));
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

		   self.menu.update(x+self.menu_shift[0], y+self.menu_shift[1]);
		   
	       });
	       
	       // $(self.container_div_id).resizable();
	       // console.log("self.container_div_id = ", self.container_div_id);
	   };
	   
	   return {
	       Tree: Tree
	   }});
