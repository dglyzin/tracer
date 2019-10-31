console.log("log tables.js");

define(["jquery", "modules/ttable"],
       function($, ttable){
	   
	   return {
	       self: this,

	       loop_dialect_table: function loop_dialect_table(){

		   // create/remove table at each click at edit_dialect
		   // button

		   ////// FOR dialect table:
		   var dialect_table_scene_checker = 0;

		   $('#edit_dialect').on('click', function(event){
    
		       console.log("file object:");
		       console.log($("#choice_db"));
		       console.log(document.getElementById('choice_db'))
		       // console.log(document.getElementById('choice_db').files[0])
		       console.log($("#choice_db").data());
		       console.log($("#choice_db")[0]);
		       // $("#choice_db").files[0]
		       
		       console.log("self.dialect_table");
		       console.log(self.dialect_table);
		       
		       if(self.dialect_table == undefined){
			   dialect_table = new ttable.Table("id", "dialect");
			   self.dialect_table = dialect_table;
		       }else{
			   dialect_table = self.dialect_table;
			   console.log("old dialect_table used");
		       }

		       console.log("dialect_table");
		       console.log(dialect_table);


		       if(dialect_table_scene_checker == 0){
			   
			   dialect_table.make_table();
			   dialect_table_scene_checker = 1;
		       }
		       else
		       {
			   dialect_table.remove_table();
			   console.log("dialect_table scene cleared");
			   dialect_table_scene_checker = 0;
		       }
		       console.log("dialect_table success");
		       
		   });
		   ////// END FOR
	       },
	       
	       loop_users_table: function loop_users_table(){
		   
		   // create/remove table at each click at edit_users
		   // button

		   
		   ////// FOR user table:
		   var user_table_scene_checker = 0;
		 
		   $('#edit_users').on('click', function(event){
		     
		       console.log("self.user_table");
		       console.log(self.user_table);
		       
		       if(self.user_table == undefined){
			   user_table = new ttable.Table("id", "user");
			   self.user_table = user_table;
		       }else{
			   user_table = self.user_table;
			   console.log("old user_table used");
		       }
		
		       console.log("user_table");
		       console.log(user_table);
		
       
		       if(user_table_scene_checker == 0){
			 
			   user_table.make_table();
			   user_table_scene_checker = 1;
		       }
		       else
		       {
			   user_table.remove_table();
			   console.log("user_table scene cleared");
			   user_table_scene_checker = 0;
		       }
		       console.log("user_table success");
		       
		   });
		   ////// END FOR

	       }
	   }
       });
