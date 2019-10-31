console.log("log ttree.js");


define(['require', 'jquery', 'jquery-ui-custom/jquery-ui', 'fancytree/modules/jquery.fancytree'],
       function(require, $, ui, fancytree){

	   jquery_ui = require('jquery-ui-custom/jquery-ui');
	   fancytree = require('fancytree/modules/jquery.fancytree');

	   return {
	       create_tree: function create_tree(){
		   $("#tree").fancytree({
		       source: [
			   // {title: "lex", key: "1"},
			   {title: "available", key: "2", folder: true, children: [
			       {title: "lex", key: "3"},
			       {title: "net", key: "4"},
			       {title: "sampling", key: "5"},
			       
			       {title: "sampling_desk", key: "6"},
			       {title: "lex_tutorial_0", key: "7"}
			   ]}
		       ],
		        activate: function(event, data){
			    // A node was activated: display its title:
			    if(!data.node.isFolder()){
				var node = data.node;
				console.log(node.title);
				
				if (data.node.title == "lex"){
				
				    window.open("/", "_self");
				    // $("_self").load("/");
				    }
				if (data.node.title=="net"){
				    
				    window.open("/net", "_self");
				    // $("_self").load("/");
				}
				if (data.node.title=="sampling"){
				    
				    window.open("/sampling", "_self");
				    // $("_self").load("/");
				}
				if (data.node.title=="sampling_desk"){
				    
				    window.open("/sampling_desk", "_self");
				    // $("_self").load("/");
				}
				if (data.node.title=="lex_tutorial_0"){
				    
				    window.open("/lex_tutorial_0", "_self");
				    // $("_self").load("/");
				}
				
				
			    }
			},
		   });

		   }}});
