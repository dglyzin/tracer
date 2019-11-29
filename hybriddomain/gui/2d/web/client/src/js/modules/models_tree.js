console.log("log models_tree.js");


define(['ttree'],
       function(ttree){

	 
	   function ModelsTree(net, url){

	       /*Node object for main net. It uses
		 ttree template with add some data to it.
		
		net method used:
		-- ``net.update(mode)`` - mode must be equal to
		one of ``tree_data`` dict title (see activator below).
		*/

	       var self = this;
	       self.net = net;
	
	       var menu_shift_controls_top = document.getElementById("controls").offsetTop;
	       console.log("controls:");
	       console.log(menu_shift_controls_top);
	       var mtree = new ttree.Tree({		  
	
		   tree_div_id: "#models_tree",
		   menu_div_id: "#models_menu",
		   input_div_id: "#models_tree_input",

		   // for avoiding canvas influence:
		   menu_shift: 0, // parseInt(menu_shift_controls_top, 10),

		   url: url,

		   /*
		   tree_data:[
		       // {title: "lex", key: "1"},
		       {title: "available", key: "2", folder: true, children: [
			   {title: "models_editor", key: "3"},
			   {title: "patterns_editor", key: "4"}
		       ]}
		   ],
		   */
		   activator: function(event, data){
		       console.log("data.node.toDict() = ", data.node.toDict());

		       // A node was activated: display its title:
		       if(!data.node.isFolder()){
			   var node = data.node;
			   console.log(node.title);
			   // self.net.update(data.node.title);
			   // window.open("/", "_self");
			   // $("_self").load("/");
		       }
		   },
		   
		   // FOR menu:
		   menu_items: ["load", "save", "rewrite", "remove", "rename",
				"mk folder"],

		   menu_tooltips: ["load previously saved model",
				   "create new model", "rewrite selected model",
				   "remove selected and keep children",
				   "rename selected node",
				   "make new collection"],

		   // keys here must be equal to ``menu_items``:
		   menu_callbacks: {

		       "load": function(){

			   /* After user enter node name it call 
			    tree.add_node_server func.*/

			   var selected_node = self.tree.get_selected_node();
			   // console.log("selected node:");
			   // console.log(selected_node);

			   var node_name = selected_node.title;
			   var to_send = {mode: "load",
					  node_name: node_name};
	       
			   // console.log("to_send:");
			   // console.log(to_send);

			   var succ = function(recived_data){
			       self.net.load(recived_data["canvas_src"]);
			   };
			   self.tree.send_data("api/tree", to_send, succ);
			   
		       },
		       
		       "save": function(){

			   /* After user enter node name it call 
			    tree.add_node_server func.*/
			   
			   var selected_node = self.tree.get_selected_node();
			   var parent_node = selected_node; 
			   var parents_list = self.tree.get_parents_list(parent_node);

			   console.log("save callback");
			   // console.log(self);
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   
			   var node_data = self.net.save();
			   
			   // console.log("node_data:");
			   // console.log(node_data);

			   var succ = function(node_name){
			       var node = {title: node_name, folder: false};
			       self.tree.add_node_server("api/tree", node,
							 node_data, parent_node,
							parents_list);
			   };
			   // self.tree.menu.input.create_input(x, y, succ);
		       },

		       "rewrite": function(){
			   
			   console.log("rewrite callback");
			   console.log(self);

			   var node_data = self.net.save();
			   
			   self.tree.rewrite_node_server("api/tree", node_data);
		       },

		       "remove": function(){
			   
			   console.log("remove callback");
			   // console.log(self);

			   self.tree.remove_node_server("api/tree");
			   // self.tree.remove_selected_node();
		       },


		       "rename": function(){
			   
			   console.log("rename callback");
			   // console.log(self);
			   
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   var succ = function(node_name){
			       
			       self.tree.rename_node_server("api/tree", node_name);
			   };
			   self.tree.menu.input.create_input(x, y, succ);
			   
		       },


		       "mk folder": function(){
			   
			   console.log("create new folder callback");
			   console.log(self);

			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   var succ = function(node_name){
			       self.tree.add_node_server("api/tree", node_name, true);
			   };
			   self.tree.menu.input.create_input(x, y, succ);

			   // self.tree.add_node("test_folder", true);
		       }
		   }
		   // END FOR
	       });
	       self.tree = mtree;
	       
	   };
	   return{ModelsTree: ModelsTree};
       });
