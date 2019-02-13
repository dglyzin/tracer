console.log("log scene.js");

//
//
define(['require', 'jquery'],
       function(require, $){

	   // $ = require('jquery');
	   // jquery_ui = require('jquery-ui-custom/jquery-ui');
	   // tabulator = require('tabulator/tabulator.min');

	   return {
	       clear_scene: function clear_scene(){
		   if($("#div_scene").children().length){
		       // FOR remove tables       
		       // END FOR
		       
		       $("#div_scene").children().each(function(index, value){
			   value.remove();
		       });
		       
		       console.log("scene cleared");
		   };
	       }
	   }
       });
