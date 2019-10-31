console.log("log main_tree.js");


define(['ttree'],
       function(ttree){

	 
	   function MTree(net){

	       /*Node object for main net. It uses
		 ttree template with add some data to it.
		
		net method used:
		-- ``net.update(mode)`` - mode must be equal to
		one of ``tree_data`` dict title (see activator below).
		*/

	       var self = this;
	       self.net = net;
	
	       var mtree = new ttree.Tree({		  
	
		   tree_div_id: "#tree",
		   menu_div_id: "#menu_div",

		   tree_data:[
		       // {title: "lex", key: "1"},
		       {title: "available", key: "2", folder: true, children: [
			   {title: "models_editor", key: "3"},
			   {title: "patterns_editor", key: "4"}
		       ]}
		   ],
		   
		   activator: function(event, data){
		       
		       // A node was activated: display its title:
		       if(!data.node.isFolder()){
			   var node = data.node;
			   console.log(node.title);
			   self.net.update(data.node.title);
			   // window.open("/", "_self");
			   // $("_self").load("/");
		       }
		   },
		   
		   // FOR menu:
		   menu_items: ["save as new", "rewrite", "create new folder"],

		   menu_tooltips: ["create new model", "rewrite selected model",
				   "make new collection"],

		   // keys here must be equal to ``menu_items``:
		   menu_callbacks: {
		       "save as new": function(){
			   
			   console.log("save as new callback");
			   console.log(self);
		       },

		       "rewrite": function(){
			   
			   console.log("rewrite callback");
			   console.log(self);
		       },

		       "create new folder": function(){
			   
			   console.log("create new folder callback");
			   console.log(self);
		       }
		   }
		   // END FOR
	       });
	   };
	   return{MTree: MTree};
       });
