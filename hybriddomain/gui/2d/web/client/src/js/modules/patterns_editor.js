console.log("log patterns_editor.js");
define(['jquery', 'jquery-ui-custom/jquery-ui',
	'fabric', 'modules/base_editor', 'modules/patterns_editor_scene'],
       
       function($, ui, fabric, base_editor, scene){

	   function BoardPatterns(){
	       
	       // FOR global variables:
	       var self = this;
	       self.name = "patterns_editor";
	       // END FOR
	       base_editor.BoardBase.call(this);
	   };

	   // inheritance:
	   BoardPatterns.prototype = Object.create(base_editor.BoardBase.prototype);
	   Object.defineProperty(BoardPatterns.prototype, 'constructor',
				 {value: BoardPatterns, enumerable: false, writable:true});
	   
	   BoardPatterns.prototype.remove = function(){
	       this.canvas_patterns.clear();
	       this.canvas_patterns.dispose();

	       $("#canvas_patterns").remove();
	       base_editor.BoardBase.prototype.remove.call(this);
	   };

	   BoardPatterns.prototype.init_board = function(){
	       var self = this;

	       this.draw_scene();
	       
	       base_editor.BoardBase.prototype.init_board.call(this);

	       self.canvas_patterns = new fabric.Canvas('canvas_patterns',
							{isDrawingMode: false});

	       this.apply_controls();
	   };

	   BoardPatterns.prototype.draw_scene = function(){
	       scene.draw_scene("#scene");
	   };

	   BoardPatterns.prototype.apply_controls = function(){

	       $("#controls").tabs();

	       this.apply_remove_all("b_remove_all");
	       this.apply_remove_selected("b_remove_selected");
	       this.apply_draw("sr_draw_size", "sr_draw_color", "none",
			       "b_change_fabric_mode");
	       this.apply_group("b_group", "b_ungroup");
	   };
	   
	   BoardPatterns.prototype.apply_remove_all = function(b_id){
	       var self = this;
	       $("#"+b_id).on("click", function(){
		   self.remove_all();
	       });
	   };

	   BoardPatterns.prototype.apply_remove_selected = function(b_id){
	       var self = this;
	       $("#"+b_id).on("click", function(){
		   if(self.canvas.getActiveObjects()){
		       self._remove_selected_obj(self.canvas);
		   }
		   if(self.canvas_patterns.getActiveObjects()){
		       self._remove_selected_obj(self.canvas_patterns);
		   };		   
	       });
	   };

	   BoardPatterns.prototype.apply_group = function(b_group_id, b_ungroup_id){
	       
	       var self = this;

	       // #b_group
	       $("#"+b_group_id).on("click",function() {
		   if (!self.canvas.getActiveObject()) {
		       return;
		   }
		   if (self.canvas.getActiveObject().type !== 'activeSelection') {
		       return;
		   }

		   var active_objects = self.canvas.getActiveObject();
		   var br = active_objects.getBoundingRect();
		   console.log("old_group.getBoundingRect:");
		   console.log(br);
		   
		   // old_group.toGroup();
		   var objs = $.map(active_objects.getObjects(), function(elm, id){
		       var new_elm = fabric.util.object.clone(elm);
		       // new_elm.set("top", elm.top+0.01);
		       //var new_elm = elm.clone();
		       
		       // console.log(new_elm);
		       self.canvas.remove(elm);
		       console.log("new_elm");
		       console.log(new_elm);
		       return(new_elm);
		   });
		   
		   // console.log("old_group.toSVG()");
		   // console.log(active_objects.toSVG());
		   // console.log(active_objects.getObjects());
		   
		   var boundRect =  new fabric.Rect({
		       top : br.top,
		       left : br.left,
		       width : br.width,
		       height : br.height,
		       fill : 'green'
		   });
		   // canvas.add(boundRect);
		   // canvas.requestRenderAll();
		   // objs.push(boundRect);
		   console.log("objs:");
		   console.log(objs);

		   var new_group = new fabric.Group(objs, {
		       top : br.top,
		       left : br.left,
		       width : br.width,
		       height : br.height,
		       fill: 'red'
		   });
		   // canvas.requestRenderAll();
		   // new_group.addWithUpdate(boundRect);
		   self.canvas.add(new_group);
		   /*
		    $.each(new_group.getObjects(), function(id, elm){
		    console.log(`index ${id} of element ${elm}`);
		    canvas1.add(fabric.util.object.clone(elm));
		    });
		    */
		   var data = new_group.toObject();
		   console.log("data");
		   console.log(data);
		   /*
		    canvas1.add(fabric.util.enlivenObjects([data], function(objects){
		    objects.forEach(function(o) {
		    if(o.type === 'activeSelection' || o.type === 'group'){
		    // active selection needs a reference to the canvas.
		    o.canvas = canvas1;
		    o.forEachObject(function(obj) {
		    canvas1.add(obj);
		    obj.setCoords();
		    });
		    }
		    // this should solve the unselectability
		    o.setCoords();

		    o.set('top', o.top + 0.15);
		    o.set('left', o.left + 0.15);
		    canvas1.add(o);
		    });
		    canvas1.renderAll();
		    }));
		    */
		   // var data1 = new_group.toJSON();
		   var data1 = '{"version":"3.1.0","objects":[' + JSON.stringify(new_group)+"]}";
		   // var data1 = JSON.stringify(canvas);
		   console.log("data1");
		   console.log(data1);
		   // {version:"3.1.0",objects:[data1]}
		   self.canvas_patterns.loadFromJSON(data1, self.canvas_patterns.renderAll.bind(self.canvas_patterns), function(o, object) {
		       fabric.log(o, object);
		   });
		   // var new_group1 = new fabric.Group([]);
		   // console.log(new_group1);
		   // canvas1.loadFromJSON(data1);
		   // new_group1.fromJSON(data1);
		   // canvas1.add(new_group1);
		   
		   // canvas1.add(fabric.util.object.clone(new_group));
		   // new_group.setColor("#AAAAAA");
		   new_group.set({"fill":"red"});
		   // new_group.backgroundColor = "AAAAAA";
		   
		   self.canvas.requestRenderAll();
		   self.canvas_patterns.requestRenderAll();
	       });

	       // #b_ungroup
	       $("#"+b_ungroup_id).on("click", function() {
		   if (!self.canvas.getActiveObject()) {
		       return;
		   }
		   if (self.canvas.getActiveObject().type !== 'group') {
		       return;
		   }
		   self.canvas.getActiveObject().toActiveSelection();
		   self.canvas.requestRenderAll();
	       });

	   };
	   
	   return {
	       Board: BoardPatterns
	   };
});
