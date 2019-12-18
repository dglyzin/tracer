// For any third party dependencies, like jQuery, place them in the lib folder.

// Configure loading modules from the lib directory,
// except for 'app' ones, which are in a sibling
// directory.
requirejs.config({
    baseUrl: 'static/src/js/libs',
    paths: {
        modules: '../modules',
	
	fabric: "fabric/dist/fabric"
	// fancytree: "fancytree/modules/jquery.fancytree"
    },
    shim: {	
	
        'fabric': {
            //These script dependencies should be loaded before loading
            //backbone.js
            deps: [],
            //Once loaded, use the global 'Backbone' as the
            //module value.
            exports: 'fabric'
        }
    }
});

// Start loading the main app file. Put all of
// your application logic in there.
// 
requirejs(['jquery', 'jquery-ui-custom/jquery-ui', 'modules/main_tree',
	   'modules/models_2d_editor', 'modules/patterns_editor',
	   'modules/equations_table'],
	  function($, ui, mtree, tmeditor, tpeditor, tetable){

	      var self = this;
	      
	      // boards:
	      self.boards = {
		  models_envs: new tmeditor.Board(),
		  patterns_editor: new tpeditor.Board(),
		  equations_mode: new tetable.ETable(self)
	      };
	      
	      // board for patterns:
	      self.pboard = undefined;
	      self.current_mode = undefined;
	      
	      self.update = function(mode){
		  /* Choice what board to draw in index.htm
		   mode is a key in self.boards
		   */
		  console.log(self.current_mode);
		  console.log(mode);
		  if (self.current_mode != undefined){
		      if(self.current_mode == mode){
			  return;	  
		      }else{
			  console.log("current_mode: "+self.current_mode);
			  console.log("new_mode: "+mode);
			  self.boards[self.current_mode].remove();
			  self.boards[mode].init_board();
		      }
		  }else{
		      self.boards[mode].init_board();
		  }
		  self.current_mode = mode;
	      };

	      // create tree:
	      self.tree = new mtree.MTree(self, "api/tree");
	      
	      console.log("all files loaded");
	      
	      $( document ).ready(function() {

		
		  // self.update("patterns_editor");
		  self.update("models_envs");
		  // var board = new tmeditor.Board();
		  //board.init_board();
	      });
	  });

