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
	/*
	  DESCRIPTION:
	  Import scripts from ajax reqursivery.
	*/

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
    
    
});
