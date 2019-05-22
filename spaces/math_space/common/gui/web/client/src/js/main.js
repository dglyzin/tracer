// For any third party dependencies, like jQuery, place them in the lib folder.

// Configure loading modules from the lib directory,
// except for 'app' ones, which are in a sibling
// directory.
requirejs.config({
    baseUrl: 'static/src/js/libs',
    paths: {
        modules: '../modules'
    }
});

// Start loading the main app file. Put all of
// your application logic in there.
// 
requirejs(['jquery', 'jquery-ui-custom/jquery-ui', 'modules/scene',
	   'modules/tables', 'modules/path', 'modules/net',
	   'modules/parser', 'modules/ttree', 'modules/sampler'],
	  function($, ui, scene, tables, path, net, tparser, tree, sampler){
	     
	      console.log("all files loaded");
	      console.log(path);
	      $( document ).ready(function() {
		  console.log("widget:");
		  console.log($.widget);
		  console.log("ui:");
		  console.log(ui);
		  console.log("scene:");
		  console.log(scene);
		  
		  tree.create_tree();
		  
		  // FOR path
		  path.init_path();
		  // END FOR
		  
		  // for checking what to write: sampling or parse pages:
		  var checker = $("#frame_sampling").val() != undefined;
		  console.log("checker:");
		  console.log(checker);
		  
		  if(checker){
		      // FOR sampler    
		      sampler = new sampler.Sampler();
		      sampler.create_sampler();
		      // END FOR    
		  }else{
		      // FOR parser
		      parser = new tparser.Parser();
		      parser.create_parser();
		      // END FOR
		  };
		  
		  
		  // FOR net:
		  // net.loop_net();
		  // END FOR
		  
		  // FOR tables:
		  tables.loop_dialect_table();
		  tables.loop_users_table();
		  // END FOR
	      });
	  });


/*
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
	*
	  DESCRIPTION:
	  Import scripts from ajax reqursivery.
	*

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
*/    

    
//});
