console.log("log tooltip.js");

define(['jquery'], function($){

    return {
	init: function init(){
	    // FOR tooltip
	    $( function() {  
		$( document ).tooltip();
	    });
	    // END FOR
	}
    }
});
