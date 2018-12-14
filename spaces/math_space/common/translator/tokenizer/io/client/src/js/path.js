console.log("log path.js");

var path_scene_checker = 0;

$("#setup_db_path").on("click", function(event){
    
    if(path_scene_checker == 0){
	
	path = new Path();

	path.make_path();

	path_scene_checker = 1;
    }
    else
    {
	clear_scene();
	console.log("path scene cleared");
	path_scene_checker = 0;
    }
});
