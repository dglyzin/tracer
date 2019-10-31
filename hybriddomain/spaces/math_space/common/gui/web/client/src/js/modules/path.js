console.log("log path.js");

define(['jquery', 'modules/tpath'],
       function($, tpath){
	   return {
	       init_path: function init_path(){

		   var path_scene_checker = 0;
		   
		   $("#setup_db_path").on("click", function(event){
    
		       if(path_scene_checker == 0){
	
			   path = new tpath.Path();

			   path.make_path();

			   path_scene_checker = 1;
		       }
		       else
		       {
			   // scene.clear_scene();
			   path.remove_path();
			   console.log("path scene cleared");
			   path_scene_checker = 0;
		       }
		   });
	       }
	   }
       });
