console.log("log net.js");


define(['jquery', 'modules/tnet'],
       function($, tnet){
	   return {
	       loop_net: function loop_net(){
		   
		   // create/remove net at each click at button_net
		   // button

		   net = new tnet.Net();
		   net_id = 0;
		   
		   $("#button_net").on("click", function(event){
		       if(net_id == 0){
			   net.create_net();
			   net_id = 1;
		       }else{
			   
			   // scene.clear_scene();
			   net.remove_net();
			   net_id = 0;
		       };
		   });
	       }
	   }
       });
