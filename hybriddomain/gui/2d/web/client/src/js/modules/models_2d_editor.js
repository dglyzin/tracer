console.log("log models_2d_editor.js");
define(['jquery', 'jquery-ui-custom/jquery-ui',
	'fabric', 'modules/base_editor', 'modules/eqs_regions',
	'modules/models_editor_scene'],
       
       function($, ui, fabric, base_editor, eqs_regions,
		scene){
	   
	   function BoardModel(){
	       
	       // FOR global variables:
	       var self = this;
	       self.name = "models_2d_editor";
	       // END FOR
	       base_editor.BoardBase.call(this);
	       
	   };

	   // inheritance:
	   BoardModel.prototype = Object.create(base_editor.BoardBase.prototype);
	   Object.defineProperty(BoardModel.prototype, 'constructor',
				{value: BoardModel, enumerable: false, writable:true});
	   
	   BoardModel.prototype.init_board = function(){
	       
	       this.draw_scene();
	       
	       base_editor.BoardBase.prototype.init_board.call(this);
	       this.canvas.setBackgroundColor('rgba(0, 0, 0, 1.0)',
					      this.canvas.renderAll.bind(this.canvas));

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
	       this.canvas.renderAll();

	       console.log("BoardModel.prototype.init_board.this:");
	       console.log(this);

	       // apply controls to divs:
	       this.apply_controls();
	       
	   };

	   /*
	   BoardModel.prototype.remove = function(){
	       
	    };
	    */
	   BoardModel.prototype.draw_scene = function(){
	       scene.draw_scene("#scene");
	   };

	   BoardModel.prototype.apply_controls = function(){
	       $("#controls").tabs();
	       $("#models_tree_wrap_style").resizable();

	       this.apply_eqs_tables();
	       this.apply_draw("sr_draw_size", "t_eqs_draw",
			       "param_draw_observable", "b_change_fabric_mode");

	       // BoardModel.prototype.apply_draw("sr_draw_size", "b_change_fabric_mode");
	       
	       this.apply_remove_all("b_remove_all");
	       this.apply_remove_selected("b_remove_selected");
	       this.apply_regions("b_add_region", "b_add_region_br");
	       // this.apply_save("b_save_fabric_canvas");
	       this.apply_tree();
	   };


	   BoardModel.prototype.get_color_val_from_input = function(color_input_id){
	       /*Get value from input value. Stored table value used*/
	       var self = this;
	       return(parseInt(self.eqs_table_selected_row_val, 10));
	   };

	   BoardModel.prototype.apply_draw_color = function(color_input_id){

	       /*Undefault input for color. Table used */
	       var self = this;
	       // this will work dynamically i.e. applies to tr which
	       // was added with $.append:
	       $("#"+color_input_id).on("click", "tr", function(){
	       // $("#"+color_input_id+" tr").on("click", function(){
		   console.log("tr click |-> color_val:");
		   var color_val = $.text(this.children[0]);
		   console.log(color_val);

		   // add to selected row value:
		   self.eqs_table_selected_row_val = color_val;

		   // FOR set color:
		   console.log("tr.style:");
		   console.log(this.parentElement.children);
		   $.each(this.parentElement.children, function(id, elm){
		       elm.setAttribute("style", "background-color: white");
		   });
		   // this.setAttribute("style", "color: blue");
		   this.setAttribute("style", "background-color: blue");
		   // END FOR

		   // FOR apply to canvas:
		   console.log("freeDrawingBrush:");
		   console.log(self.canvas.freeDrawingBrush);
		   
		   var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		   self.canvas.freeDrawingBrush.color = color;
		   console.log(self.canvas.freeDrawingBrush.color);
		   // END FOR
	       });

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
	   
	   BoardModel.prototype.apply_eqs_tables = function(){
	       var self = this;
	       self.eqs_table = self.eqs_table || [];
	       self.eqs_table_selected_row_val = self.eqs_table_selected_row_val || 255;

	       self.apply_eqs_table_draw("b_draw_add_eq_num", "t_eqs_draw",
					"i_eq_num_draw", "sr_draw_color");
	       // TODO:
	       // apply_eqs_table_eregions
	       // apply_eqs_table_br #  may be separately from here
	   };

	   BoardModel.prototype.apply_eqs_table_draw = function(b_add_eq_id, table_id,
								i_eq_num_id, sr_eq_color_id){
	       
	       /*Apply colors/equations_numbers table's button callback for draw tab*/
	       
	       var self = this;
	        $("#"+b_add_eq_id).on("click", function(){
		    var color_val = $("#"+sr_eq_color_id).val();
		    var eq_num = $("#"+i_eq_num_id).val();
		    
		    if($.map(self.eqs_table, function(elm, id){
			return(elm[0]);}).indexOf(color_val) < 0)
		    {
			$("#"+table_id).append( '<tr><td>'+color_val+ '</td>'
						+ ' <td>'+eq_num+'</td></tr>');
			self.eqs_table.push([color_val, eq_num]);
		    }else{
			throw new Error("cannot add more then one eq to"
					+ " one color");
		    }
		    console.log("self.eqs_table = ", self.eqs_table);
		});
	   };

	   BoardModel.prototype.apply_regions = function(b_add_region_id, b_add_region_br_id){
	       
	       /*Apply add bound and equation regions to according divs
		*/

	       var self = this;
	       
	       // create all needed subclasses:
	       eqs_regions.create_regions_cls(self);

	       //"#b_add_region_br" 
	       $("#"+b_add_region_br_id).on("click", function(){
		   var color_val = $("#sr_eq_color_br").val();
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
		   var color_val = $("#sr_eq_color").val();
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
					     canvas_source: JSON.stringify(self.canvas)});
	       
	       return(to_send);
	   };
	   
	   return {
	       Board: BoardModel 		   
	   };
       });
