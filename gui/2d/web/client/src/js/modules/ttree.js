console.log("log ttree.js");


define(['require', 'jquery', 'jquery-ui-custom/jquery-ui', 'fancytree/modules/jquery.fancytree'],
       function(require, $, ui, fancytree){

	   // jquery_ui = require('jquery-ui-custom/jquery-ui');
	   fancytree = require('fancytree/modules/jquery.fancytree');

	   return {
	       create_tree: function create_tree(net){
		   var self = this;
		   self.net = net;

		   $("#tree").fancytree({
		       source: [
			   // {title: "lex", key: "1"},
			   {title: "available", key: "2", folder: true, children: [
			       {title: "models_editor", key: "3"},
			       {title: "patterns_editor", key: "4"}
			   ]}
		       ],
		        activate: function(event, data){
			    // A node was activated: display its title:
			    if(!data.node.isFolder()){
				var node = data.node;
				console.log(node.title);
				
				if (data.node.title == "models_editor"){
				    
				    self.net.update("models_editor");
				    // window.open("/", "_self");
				    // $("_self").load("/");
				    }
				if (data.node.title=="patterns_editor"){
				    self.net.update("patterns_editor");
				    // window.open("/net", "_self");
				    // $("_self").load("/");
				}				
			    }
			}
		   });
	   
	       }}});
