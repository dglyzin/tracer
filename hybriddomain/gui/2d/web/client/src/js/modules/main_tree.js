console.log("log main_tree.js");


define(['ttree'],
       function(ttree){

	 
	   function MTree(net, url){

	       /*Node object for main net. It uses
		 ttree template with add some data to it.
		
		net method used:
		-- ``net.update(mode)`` - mode must be equal to
		one of ``tree_data`` dict title (see activator below).
		*/

	       var self = this;
	       self.net = net;
	       self.url = url;

	       // self.env_content = ["bounds", "centrals", "initials"];

	       var mtree = new ttree.Tree({		  
	
		   container_div_id: "#nav",
		   tree_div_id: "#main_tree",
		   menu_div_id: "#main_tree_menu_div",
		   input_div_id: "#main_tree_input",
		   
		   menu_shift: [-100, 0],
		   
		   url: url,
		   /*
		   tree_data:[
		       // {title: "lex", key: "1"},
		       {title: "available", key: "2", type: "root", children: [
			   {title: "models_envs", key: "3", type: "folder",
			    children:[]},
			   {title: "patterns_editor", key: "4", type: "board"}
		       ]}
		   ],
		   */

		   activator: function(event, data){
		       console.log("data.node.toDict() = ", data.node.toDict());
		       /*
		       var parents = [];
			   if(data.node.type != "folder"){
			       if(data.node.type == "envs_root"){
				   
			       }
			       else
			       {
				   return;
			       }
			   }
			*/
		       // var node = self.tree.get_selected_node();
		       var rootNode = self.tree.get_root_node();
		       
		       var parent = self.tree.get_node_parent(data.node);
		       console.log("node.parent = ", parent);

		       //console.log("rootNode = ", rootNode.title);
		       
		       var to_send = {mode: "activate",
				      node: data.node.toDict(),
				      // vertex_idx: data.node.title,
				      parents_list: self.tree.get_parents_list(data.node)};
		       console.log("parents_list = ", self.tree.get_parents_list(data.node));
		       
					   
		       // console.log("to_send:");
		       // console.log(to_send);

		       var succ = function(recived_data){
			   recived_data["out"]["in"] = to_send;
			   console.log("recived_data = ", recived_data);
			   var entries_idxs = [];
			   
			   /*
			   for(var idx in recived_data["entries_idxs"]){
			       entries_idxs.push({title: recived_data["entries_idxs"][idx],
						  folder: false});
			   }
			    */
			   console.log("data.node.title:");
			   console.log(data.node.title);
			   console.log("entries_idxs = ", entries_idxs);
			   if(parent.type=="env"){
			       // if recived_data["out"]["content_type"] == equations
			       // self.net.update("equations_editor")
			       // self.net.update("field_editor")
			       // load env content:
			       console.log("self.net.current_mode = ", self.net.current_mode);       
			       if (recived_data["out"]["content_type"] == "equations"){
				   self.net.update("equations_mode");
				   // TODO to_send
				   
			       }
			       else{
				   if (recived_data["out"]["content_type"] == "equations_bs"){
				       self.net.update("equations_bs_mode");
				   }else{
				       // (recived_data["out"]["content_type"] == "centrals")
				       self.net.update("models_envs");
				       }
			       }
			       self.net.boards[self.net.current_mode].load(recived_data["out"]);
			       }
			   else{
			       // load children:
			       data.node.fromDict({
				   title: data.node.title,
				   type: data.node.type,
				   children: recived_data["out"]
			       });
			   }
			   
		       };
		       self.tree.send_data(url, to_send, succ);

		       // A node was activated: display its title:
		       if(!data.node.isFolder()){
			   var node = data.node;
			   console.log(node.title);
			   if(self.net.boards.hasOwnProperty(node.title))
			       self.net.update(data.node.title);
			   // window.open("/", "_self");
			   // $("_self").load("/");
		       }
		   },
		   
		   // FOR menu:
		   menu_items: ["save", "rename", "mk env", "mk folder", "rm"],

		   menu_tooltips: ["save current model", "rename",
				   "make new model", "make new collection", "rm"],

		   // keys here must be equal to ``menu_items``:
		   menu_callbacks: {
		       "save": function(){
			   
			   /* it call 
			    tree.add_node_server func and send
			    self.net.board data to it.
			    When clicked at env_content*/
			   
			   var selected_node = self.tree.get_selected_node();
			   // var parent = self.tree.get_parent_node(selected_node);
			   // var parent_node = selected_node; 
			   if (selected_node.type != "env_content"){
			       var msg = ("cannot save node with type: "
					  + selected_node.type);
			       alert(msg);
			       throw new Error(msg);
			   }
			 
			   // var parents_list = self.tree.get_parents_list(selected_node);

			   console.log("save callback");
			   // console.log(self);
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   
			   var node_data = self.net.boards[self.net.current_mode].save();
			   
			   // console.log("node_data:");
			   // console.log(node_data);
			   
			   self.tree.save_node_server(url, selected_node, node_data);
			   
			   // self.tree.menu.input.create_input(x, y, succ);

		       },

		       "rename": function(){
			   
			   var selected_node = self.tree.get_selected_node();
			   
			   var node_dict = selected_node.toDict();
			   if(node_dict["type"] != "folder"
			      & node_dict["type"] != "env"){
			       var msg = ("rename for not supported type:"
					  + node_dict["type"]);
			       alert(msg);
			       throw new Error(msg);
			       return;
			   }
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   var succ = function(node_name){
			       
			       self.tree.rename_node_server(url, selected_node,
							    node_name);
			   };
			   self.tree.menu.input.create_input(x, y, succ);

		       },

		       "mk env":  function(){
			   
			   console.log("create new env callback");
			   console.log(self);

			   var selected_node = self.tree.get_selected_node();
			   var parent_node = selected_node;
			   var parent_node_dict = parent_node.toDict();
			   var parents_list = self.tree.get_parents_list(parent_node);
			   if(parent_node_dict["type"] != "folder" &
			      parent_node_dict["type"] != "envs_root"){
			       var msg = ("mk folder for not supported type:"
					  + parent_node_dict["type"]);
			       alert(msg);
			       throw new Error(msg);
			       return;
			   }
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   var succ = function(node_name){
			       var node = {title: node_name, type: "env",
					   folder: true};
			       self.tree.add_node_server(url, node,
							 {}, parent_node_dict,
							 parents_list);
			   };
			   self.tree.menu.input.create_input(x, y, succ);

			   // self.tree.add_node("test_folder", true);
		       },

		       "mk folder": function(){
			   
			   console.log("create new folder callback");
			   console.log(self);

			   var selected_node = self.tree.get_selected_node();
			   var parent_node = selected_node;
			   var parent_node_dict = parent_node.toDict();
			   var parents_list = self.tree.get_parents_list(parent_node);
			   if(parent_node_dict["type"] != "folder" &
			      parent_node_dict["type"] != "envs_root"){
			       var msg = ("mk folder for not supported type:"
					  + parent_node_dict["type"]);
			       alert(msg);
			       throw new Error(msg);
			       return;
			   }
			   var x = self.tree.menu.offset[0];
			   var y = self.tree.menu.offset[1];
			   console.log("x, y:");
			   console.log([x, y]);

			   var succ = function(node_name){
			       var node = {title: node_name, type: "folder",
					   folder: true};
			       self.tree.add_node_server(url, node,
							 {}, parent_node_dict,
							 parents_list);
			   };
			   self.tree.menu.input.create_input(x, y, succ);

			   // self.tree.add_node("test_folder", true);
		       },
		       
		       "rm": function(){
			       
			   console.log("remove callback");
			   // console.log(self);
			   var selected_node = self.tree.get_selected_node();
			   var selected_node_dict = selected_node.toDict();
			   
			   if(selected_node_dict["type"] != "folder" &
			      selected_node_dict["type"] != "envs_root" &
			      selected_node_dict["type"]!= "env"){
			       var msg = ("cannot remove node with type: "
					  + selected_node_dict["type"]);
			       alert(msg);
			       throw new Error(msg);
			   }
			   var check_empty = true;
			   if(selected_node_dict["type"] == "env")
			       check_empty = false;

			   self.tree.remove_selected_node_server(url, check_empty);
			   // self.tree.remove_selected_node();
		       }

		   }
		   // END FOR
	       });
	       self.tree = mtree;
	   };
	   return{MTree: MTree};
       });
