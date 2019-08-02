console.log("log base_editor.js");
define(['jquery', 
	'fabric'],
              
       function($, fabric){
	   function BoardBase(){
	       // FOR global variables:
	       var self = this;
	       // END FOR
	   }
	   
	   BoardBase.prototype.init_board = function(){
	       var self = this;

	       self.canvas = new fabric.Canvas('canvas',
					       {isDrawingMode: false});
	       
	       self.canvas.freeDrawingBrush.width = 10;
		       
	   };

	   BoardBase.prototype.apply_draw = function(sr_size_id, sr_color_id,
						     c_observable_id, b_element_id){
	       
	       /*Apply free drawing mode switch to button
		with ``b_element_id`` div. Value from
		``sr_element_id`` used for brush size.*/
	       
	       var self = this;
	       console.log("this:");
	       console.log(this);
	
	       /*
	       $("#"+sr_element_id).on("click", function(){
		   console.log("clicked");
	       });
		*/
	       // "sr_draw_size"
	       $("#"+sr_color_id).on("change", function(){
		   console.log("freeDrawingBrush:");
		   console.log(self.canvas.freeDrawingBrush);
		   var color_val = this.value;
		   var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		   self.canvas.freeDrawingBrush.color = color;
		   console.log(self.canvas.freeDrawingBrush.color);
	       });
	       // "sr_draw_size"
	       $("#"+sr_size_id).on("change", function(){
		   console.log("onchange");
		   self.canvas.freeDrawingBrush.width = parseInt(this.value, 10);
		   console.log(self.canvas.freeDrawingBrush.width);
	       });
	       /*
	       var draw_size = document.getElementById(sr_size_id);
	       draw_size.onchange = function(){
		   console.log("onchange");
		   self.canvas.freeDrawingBrush.width = parseInt(this.value, 10);
		   console.log(self.canvas.freeDrawingBrush.width);
	       };
		*/
	       // "#b_change_fabric_mode"
	       $("#"+b_element_id).on("click", function(){
		   self.canvas.isDrawingMode=!self.canvas.isDrawingMode;

		   if (self.canvas.isDrawingMode){
		       var color_val = parseInt($("#"+sr_color_id).val(), 10);
		       console.log("color_val:");
		       console.log(color_val);
		       var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		       self.canvas.freeDrawingBrush.color = color;
		       
		       var observable = $("#"+c_observable_id).is(":checked");
		       console.log("observable:");
		       console.log(observable);
		       self.canvas.freeDrawingBrush.observable = observable;
		       
		       console.log("freeDrawingBrush:");
		       console.log(self.canvas.freeDrawingBrush);
		   };
		   
	       });
	   };

	   BoardBase.prototype.remove_all = function(){
	       
	       /*Remove all objects from default canvas*/

	       this._remove_all(this.canvas);
	   };

	   BoardBase.prototype._remove_all = function(canvas){
	       
	       /*Remove all objects from given canvas.*/

	       var objs = canvas.getObjects();
	       objs.forEach((obj)=>{canvas.remove(obj);});
	       canvas.requestRenderAll();
	   };

	   BoardBase.prototype.remove_selected_obj = function(){
	       this._remove_selected_obj(this.canvas);
	   };

	   BoardBase.prototype._remove_selected_obj = function(canvas){

	       /*Remove active object from given canvas*/

	       var selected = canvas.getActiveObjects();
	       if (!selected) {
		   return;
		   }
	       /*
	       if (selected.type !== 'activeSelection') {
		   console.log("unactive objects:");
		   console.log(selected);
		   return;
	       }
		*/
	       console.log("selected for remove:");
	       console.log(selected);
	       
	       selected.forEach((obj)=>{canvas.remove(obj);});
	       canvas.discardActiveObject().requestRenderAll();
	       console.log("objects removed");
	   };

	   BoardBase.prototype.remove = function(){

	       /*Clear canvas and remove it*/

	       this.canvas.clear();
	       this.canvas.dispose();
	       $("#canvas").remove();
	       // $("#controls").remove();
	       this.clear_scene("#scene");
	   };

	  BoardBase.prototype.clear_scene = function(scene_id){
	      
	      /*Remove all content from scene_id div.*/
	      
	      if($(scene_id).children().length){
		  // FOR remove tables       
		  // END FOR
		  
		  $(scene_id).children().each(function(index, value){
		      console.log("item "+index);
		      console.log(value);
		      value.remove();
		  });
		  
		  console.log("scene cleared");
	      };
	  };

	   return {
	       BoardBase: BoardBase 
	   };
       });
