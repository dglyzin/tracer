var clear_scene = function(){
	if($("#div_scene").children().length){
	    // FOR remove tables
	    try
	    {
		s_index = 0;
		add_checker = 0;
		data_add = [];
		data = [];
		columns = [];
		columns_add = [];

		if($("#div_table").length){
		    $("#div_table").tabulator("destroy");
		};
		if($("#div_table_add").length){
		    $("#div_table_add").tabulator("destroy");
		};
	    }
	    catch(e)
	    {
		console.log("tables div_table div_table_add not exist");
	    }
	    
	    // END FOR

	    $("#div_scene").children().each(function(index, value){
		value.remove();
	    });
	    
	    console.log("scene cleared");
	};
    };
