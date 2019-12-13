console.log("log models_2d_editor.js");
define(['jquery', 'jquery-ui-custom/jquery-ui',
	'fabric', 'modules/base_editor', 'modules/eqs_regions',
	'modules/models_editor_scene', 'modules/models_table'],
       
       function($, ui, fabric, base_editor, eqs_regions,
		scene, table){
	   
	   function BoardModel(){
	       
	       // FOR global variables:
	       var self = this;
	       self.name = "models_2d_editor";
	       // END FOR
	       base_editor.BoardBase.call(this);

	       self.scene = new scene.ModelsScene(self);
	       console.log("BoardModel.scene = ", self.scene);
	       
	       self.table = new table.ModelsTable(self);
	       self.tables_ids = ["t_eqs_draw", "t_eqs_eqr", "t_eqs_br"];
	   };

	   // inheritance:
	   BoardModel.prototype = Object.create(base_editor.BoardBase.prototype);
	   Object.defineProperty(BoardModel.prototype, 'constructor',
				{value: BoardModel, enumerable: false, writable:true});
	   
	   BoardModel.prototype.remove = function(){

	       // clear scene:
	       var children = $("#scene").children();
	       console.log("children = ", children);
	       $.each(children, function(id, elm){
		   console.log("elm = ", elm);
		   console.log("elm = ", elm);
		   elm.remove();
	       });
	       
	    };
	   
	  
	   BoardModel.prototype.update = function(content_type){
	       var self = this;
	       
	       // clear scene:
	       self.remove();

	       var draw_bounds = undefined;
	       var draw_eq_number = undefined;

	       if(content_type == "initials"){
		   draw_bounds = false;
		   draw_eq_number = false;
	       }
		
	       if(content_type == "centrals"){
		   draw_bounds = false;
		   draw_eq_number = true;
	       }
	       if(content_type == "bounds"){
		   draw_bounds = true;
		   draw_eq_number = true;
	       }
	       if(content_type == undefined){
		   self.scene.draw_scene_welcome("#scene");
		   return;
		   // throw Error("content_type is undefinded");
	       };
		   	       
	       this.draw_scene(draw_bounds, draw_eq_number);
	       base_editor.BoardBase.prototype.init_board.call(this);
	       this.canvas.setBackgroundColor('rgba(0, 0, 0, 1.0)',
					      this.canvas.renderAll.bind(this.canvas));
	       this.canvas.renderAll();

	       console.log("BoardModel.prototype.init_board.this:");
	       console.log(this);

	       // apply controls to divs:
	       this.apply_controls(draw_bounds, draw_eq_number);


	   };
	   BoardModel.prototype.init_board = function(){
	       // TODO:
	       this.update();
	       /*
	       this.draw_scene();
	       
	       base_editor.BoardBase.prototype.init_board.call(this);
	       this.canvas.setBackgroundColor('rgba(0, 0, 0, 1.0)',
					      this.canvas.renderAll.bind(this.canvas));
		*/
	       /*
	       var rect = new fabric.Rect({
		   top : 100,
		   left : 100,
		   width : 60,
		   height : 70,
		   fill : 'red'
	       });
	       
	       this.canvas.add(rect);
		       
	       var circle = new fabric.Circle({
		   radius: 20, fill: "green", left: 70, top: 100
	       });
	       this.canvas.add(circle);
	
	       var text = new fabric.Textbox('hello world',
					     { left: 100, top: 100,
					       fill: "rgba(231, 231, 231, 1.0)",
					       editable: true});
	       this.canvas.add(text);
		*/
	       /*
	       this.canvas.renderAll();

	       console.log("BoardModel.prototype.init_board.this:");
	       console.log(this);

	       // apply controls to divs:
	       this.apply_controls();
	       */
	   };

	   BoardModel.prototype.draw_scene = function(draw_bounds, draw_eq_number){
	       var self = this;
	       self.scene.draw_scene("#scene", draw_bounds, draw_eq_number);
	   };

	   BoardModel.prototype.apply_controls = function(draw_bounds, draw_eq_number){
	       var self = this;
	       $("#controls").tabs();
	       $("#models_tree_wrap_style").resizable();

	       this.apply_eqs_tables(draw_bounds, draw_eq_number);

	       this.apply_draw("sr_draw_size", self.tables_ids,
			       "param_draw_observable", "b_change_fabric_mode");

	       // BoardModel.prototype.apply_draw("sr_draw_size", "b_change_fabric_mode");
	       
	       this.apply_remove_all("b_remove_all");
	       this.apply_remove_selected("b_remove_selected");
	       this.apply_regions("b_add_region", "b_add_region_br");
	       // this.apply_save("b_save_fabric_canvas");
	       // this.apply_tree();
	   };


	   BoardModel.prototype.get_color_val_from_input = function(color_input_id){
	       /*Owerride Get value from input value. Stored table value used*/
	       var self = this;
	       return(parseInt(self.table.eqs_table_selected_row_val, 10));
	   };

	   BoardModel.prototype.apply_draw_color = function(tables_ids){

	       /*Owerride default input for color. Table used */
	       var self = this;
	       self.table.set_on_row_click(tables_ids);
	       /*
	       // "t_eqs_draw"
	       $("#"+color_input_id).on("click", function(){
		   console.log("freeDrawingBrush:");
		   console.log(self.canvas.freeDrawingBrush);
		   var color_val = this.value;
		   var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		   self.canvas.freeDrawingBrush.color = color;
		   console.log(self.canvas.freeDrawingBrush.color);
	       });
		*/
	   };

	   BoardModel.prototype.apply_remove_all = function(b_id){
	       var self = this;
	       $("#"+b_id).on("click", function(){
		   self.remove_all();
	       });
	   };

	   BoardModel.prototype.apply_remove_selected = function(b_id){
	       var self = this;
	       $("#"+b_id).on("click", function(){
		   self.remove_selected_obj();
	       });
	   };
	   
	   BoardModel.prototype.apply_eqs_tables = function(draw_bounds, draw_eq_number){
	       var self = this;

	       var btype_draw = undefined;
	       var btype_eq = undefined;
	       var btype_br = undefined;
	       
	       var eq_number_draw = undefined;
	       var eq_number_eq = undefined;
	       var eq_number_br = undefined;

	       if (draw_eq_number){
		   eq_number_draw = "i_eq_num_draw";
		   eq_number_eq = "i_eq_num";
		   eq_number_br = "i_eq_num_br";
	       };

	       if (draw_bounds){
		   btype_draw = "s_btype_draw";
		   btype_eq = "s_btype_eq";
		   btype_br = "s_btype_br";
		   }
	       

	       self.table.apply_eqs_table("b_draw_add_eq_num", self.tables_ids,
					  eq_number_draw, "sr_draw_color",
					  btype_draw);
	       
	       self.table.apply_eqs_table("b_eqr_add_eq_num", self.tables_ids,
					  eq_number_eq, "sr_eq_color",
					  btype_eq);
	       
	       self.table.apply_eqs_table("b_br_add_eq_num", self.tables_ids,
					  eq_number_br, "sr_eq_color_br",
					  btype_br);
	   };


	   BoardModel.prototype.apply_regions = function(b_add_region_id, b_add_region_br_id){
	       
	       /*Apply add bound and equation regions to according divs
		*/

	       var self = this;
	       
	       // create all needed subclasses:
	       eqs_regions.create_regions_cls(self);

	       //"#b_add_region_br" 
	       $("#"+b_add_region_br_id).on("click", function(){
		   var color_val = self.get_color_val_from_input();
		   // var color_val = $("#sr_eq_color_br").val();
		   var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		   var eq_number = $("#i_eq_num_br").val();
		   console.log("color");
		   console.log(color);
		   console.log("side:");
		   console.log($("#param_side").val());
		   console.log($("#param_side").val());

		   var rect = new fabric.BRegion({
		       side: parseInt($("#param_side").val(), 10),
		       observable: true,
		       equation_number: eq_number,
		       convas_width: self.canvas.get("width"),
		       convas_height: self.canvas.get("height"),
		       fill : color
		   });
		   
		   self.canvas.add(rect);
		   /*
		    console.log("toObject");
		    console.log(rect.toObject());
		    console.log("json data:");
		    console.log(JSON.stringify(rect));
		    */
	       });

	       // "#b_add_region" 
	       $("#"+b_add_region_id).on("click", function(){
		   
		   /*If observable checkbox is up, then region will appear
		    in both saved img and canvas, if not it will only in canvas.
		    
		    Type of region can be: Text, Circle, Rect. Type will be taken
		    from ``param_type`` selector
		    
		    Color and equation number are correlate with each other.
		    Color will be used for defining equation number in backend.
		    */

		   // choice color and equation number:
		   var color_val = self.get_color_val_from_input();
		   // var color_val = $("#sr_eq_color").val();
		   var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		   var eq_number = $("#i_eq_num").val();
		   console.log("color");
		   console.log(color);
		   
		   var observable = $("#param_observable").is(":checked");
		   console.log("observable:");
		   console.log(observable);

		   // choice type of region (Text, Circle, Rect):
		   var param_type = $("#param_type").val();
		   console.log("param_type");
		   console.log(param_type);
		   // var rect = new eqs_regions.EquationRegion({
		   var obj = eqs_regions.choice_region(param_type,
						       {observable: observable,
							equation_number: eq_number,
							color: color});
		   self.canvas.add(obj);
		   /*
		    console.log("toObject");
		    console.log(rect.toObject());
		    console.log("json data:");
		    console.log(JSON.stringify(rect));
		    */
	       });   
	   };
	   BoardModel.prototype.apply_tree = function(){
	       var self = this;
	       // self.tree = mtree.ModelsTree(self);
	   };

	   BoardModel.prototype.apply_save = function(b_save_fabric_canvas_id){
	       
	       /*Save model to img and send it to server.
		Some regions will be converted, some ignored
		(depend's on obj.observable value)

		if parent of obj is bRegion, it will be converted to
		1px width (for sides 0, 1) or height(for sides 2, 3)
		in resulting img.
		*/

	       var self = this;

	       // "#b_save_fabric_canvas"
	       $("#"+b_save_fabric_canvas_id).on("click", function(){
		   
		   var to_send = self.save();

		   // FOR send data to server:
		   console.log("\n sending");
		   console.log(to_send);
		   $.ajax(
		       {
			   url: '/',
			   type: 'POST',
			   data: to_send,
			   
			   success: function (jsonResponse) {
			       var objresponse = JSON.parse(jsonResponse);
			       
			       var data = objresponse;
			       console.log("\ndata_successfuly_recived:");
			       console.log(data);

			       var models_id = $.map(data["models_id"], function(elm, id){
				   console.log(elm);
				   console.log(id);
				   return('<li class="ui-menu-item ui-widget ui-widget-content"'
					  + 'title="title">'+elm+'</li>');
			       });
			       $("#m_models").append(models_id.join(""));
			   },

			   error: function (data) {
			       console.log("error to send");
			       console.log(data);
			   }
		       });
		   // END FOR
	       });

	   };
	   
	   BoardModel.prototype.load = function(data){
	       var self = this;
	       
	       // TODO:
	       var content_type = data["content_type"];
	       console.log("content_type:");
	       console.log(data["content_type"]);
	       self.update(content_type);
	       
	       console.log("data[canvas_src]:");
	       console.log(data["canvas_src"]);
	       self.canvas.loadFromJSON(data["canvas_src"],
					self.canvas.renderAll.bind(self.canvas),
					function(o, object) {
					    console.log("from fabric.loadFromJosn:");
					    console.log(o);
					    console.log(object);
					    fabric.log(o, object);
					});
	       self.canvas.requestRenderAll();

	   };

	   BoardModel.prototype.save = function(){
	       
	       var self = this;

	       // for filter unobservable:
	       console.log("unobservable objects:");
	       var uo_objects = self.canvas._objects.filter(function(elm){return(!elm.observable);});
	       console.log(uo_objects);

	       // FOR hiding unobservable by changing they color to canvas.background
	       uo_objects.forEach(function(elm){
		   elm.old_fill = elm.fill;
		   // elm.set("fill", 'rgba(255, 255, 255, 1.0)');
		   elm.setColor('rgba(0, 0, 0, 1.0)');
	       });
	       console.log("recolored done");
	       self.canvas.renderCanvas(self.canvas.getContext(), uo_objects);
	       // END FOR

	       console.log("br objects:");
	       var br_objects = self.canvas._objects.filter(function(elm){return(elm.type == "bRegion");});
	       console.log(br_objects);

	       // FOR set bRegion's width's to 1px:
	       br_objects.forEach(function(elm){
		   if(elm.side == 0){
		       elm.old_width = elm.width;
		       elm.set("width", 1);
		   }
		   if(elm.side == 1){
		       elm.old_width = elm.width;
		       elm.set("width", 1);
		       elm.set("left", elm.left+elm.old_width-1);
		   }
		   if(elm.side == 2){
		       elm.old_height = elm.height;
		       elm.set("height", 1);
		   }
		   if(elm.side == 3){
		       elm.old_height = elm.height;
		       elm.set("height", 1);
		       elm.set("top", elm.top+elm.old_height-1);
		   }
		   
	       });
	       self.canvas.renderCanvas(self.canvas.getContext(), br_objects);
	       // END FOR

	       self.canvas.setBackgroundColor('rgba(0, 0, 0, 1.0)',
					      self.canvas.renderAll.bind(self.canvas));

	       // convert to img:
	       var data = self.canvas.toDataURL({format: 'png',
						 left: 0, top: 0, width: 550, height: 300});

	       // var data = self.canvas.toDataURL({format: 'jpeg', quality: 1,
	       // left: 0, top: 0, width: 550, height: 300});

	       // FOR restore bRegions width:	
	       br_objects.forEach(function(elm){
		   if(elm.side == 0){
		       elm.set("width", elm.old_width);
		   }
		   if(elm.side == 1){
		       elm.set("width", elm.old_width);
		       elm.set("left", elm.left-elm.old_width+1);
		   }
		   if(elm.side == 2){
		       elm.set("height", elm.old_height);
		   }
		   if(elm.side == 3){
		       elm.set("height", elm.old_height);
		       elm.set("top", elm.top-elm.old_height+1);
		   }
	       });
	       self.canvas.renderCanvas(self.canvas.getContext(), br_objects);
	       // END FOR

	       // FOR restore unobservable:
	       uo_objects.forEach(function(elm){
		   // elm.set("fill", elm.old_fill);
		   elm.setColor(elm.old_fill);
	       });
	       self.canvas.renderCanvas(self.canvas.getContext(), uo_objects);
	       // END FOR
	       
	       self.canvas.requestRenderAll();

	       // for extracting image:
	       var img = document.getElementById('result_img');
	       img.src = data;

	       $("#controls").tabs("refresh");
	       
	       console.log("canvas json obj:");
	       console.log(data);
	       var to_send = JSON.stringify({canvas_img: data,
					     canvas_source: JSON.stringify(self.canvas),
					     eqs_table: JSON.stringify(self.eqs_table)});
	       
	       return(to_send);
	   };
	   
	   return {
	       Board: BoardModel 		   
	   };
       });
