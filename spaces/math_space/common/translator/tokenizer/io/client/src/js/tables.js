console.log("log tables.js");

var dialect_table_scene_checker = 0;

$('#edit_dialect').on('click', function(event){
    
    console.log("file object:");
    console.log($("#choice_db"));
    console.log(document.getElementById('choice_db'))
    // console.log(document.getElementById('choice_db').files[0])
    console.log($("#choice_db").data());
    console.log($("#choice_db")[0]);
    // $("#choice_db").files[0]

    dialect_table = new Table("id", "dialect");
    console.log("dialect_table");
    console.log(dialect_table);

    if(dialect_table_scene_checker == 0){
	
	dialect_table.make_table();
	dialect_table_scene_checker = 1;
    }
    else
    {
	clear_scene();
	console.log("dialect_table scene cleared");
	dialect_table_scene_checker = 0;
    }
    console.log("dialect_table success");

});


var user_table_scene_checker = 0;

$('#edit_users').on('click', function(event){
    
   
    user_table = new Table("id", "user");
    console.log("user_table");
    console.log(user_table);

    if(user_table_scene_checker == 0){
	
	user_table.make_table();
	user_table_scene_checker = 1;
    }
    else
    {
	clear_scene();
	console.log("user_table scene cleared");
	user_table_scene_checker = 0;
    }
    console.log("user_table success");

});

