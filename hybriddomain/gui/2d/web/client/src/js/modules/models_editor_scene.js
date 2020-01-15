console.log("log models_editor_scene.js");

define(['jquery', 'jquery-ui-custom/jquery-ui'], function($, ui){

    function ModelsScene(net){
	var self = this;
	self.net = net;
    };

    ModelsScene.prototype.get_btype = function(btype_id){
	return(`btype: <select id="`+btype_id+`" style="width: 100px">`
	       + `<option>Dirichlet</option><option>Neumann</option>`
	       + `</select><br>`);
    };

    ModelsScene.prototype.get_equation_input = function(i_eq_num){
	return(`equation number:`
	       + `<input type="text" id="`
	       + i_eq_num + `" value="1" class="style_button_number">`);
    };

    ModelsScene.prototype.draw_scene_welcome = function(div_id){
	var scene_str = "<p>Choice model</p>";
	$(div_id).html(scene_str);
	    
    };

    ModelsScene.prototype.draw_scene = function(div_id, draw_bounds, draw_eq_number){

	var self = this;

	var draw_tables = true;
	
	// FOR scene:
	var scene_str =
		`<div id="controls" class="tree_positioned" ></div>
		    <div id="scene_canvas" width="850" height="300"
	                style="border: 1px solid; border-width: 1px; border-color: black; position: absolute;">
		       <table class="tree_positioned">
		       <tr><td>
		          <canvas id="canvas" style="position: absolute; border: 1px solid; border-width: 1px;
                            border-color: #111111;" width="550" height="300"></canvas>
		       </td></tr></table>
                     </div><br>
                     `;

	$(div_id).html(scene_str);
	// END FOR

	// FOR controls:
	var controls_str = 
		`<ul>
		     <li><a href="#controls_draw">draw mode</a></li>
		     <li><a href="#controls_eq_regions">add eq regions</a></li>
		     <li><a href="#controls_br_regions">add br regions</a></li>
		     <li><a href="#controls_save">save</a></li>
		    </ul>
		    <div id="controls_draw"></div>
		    <div id="controls_eq_regions"></div>
		    <div id="controls_br_regions"></div>
		    <div id="controls_save" style="height: 470px;"></div>`;
	$("#controls").html(controls_str);

	var eq_number_draw = "";
	if (draw_eq_number)
	    eq_number_draw = self.get_equation_input("i_eq_num_draw");
	var table_draw = "";
	if (draw_tables)
	    table_draw = self.net.table.draw("t_eqs_draw", "b_draw_add_eq_num",
					     "b_draw_del_eq_num",
					     draw_bounds, draw_eq_number);
	var btype_draw = "";
	if(draw_bounds)
	    btype_draw = self.get_btype("s_btype_draw");
	console.log("draw_bounds = ", draw_bounds);
	console.log("btype_draw = ", btype_draw);
	
	var controls_draw_str =
		`<input type="button" value="change draw mode" id="b_change_fabric_mode">
		    <br>
		    draw size: 
		    <input id="sr_draw_size" value="12" min="0.1" max="50" style="display: block" type="range">
		    <br>
		    draw color:
		    <input id="sr_draw_color" value="255" min="1" max="255" style="display: block" type="range">
                    <p id="p_draw_sr_val"></p>
		    <br>`
		+ eq_number_draw
		+ `<br>`+ btype_draw
                + `<br>`
		+ table_draw
                + `<br>
		    <input id="param_draw_observable" type="checkbox" value="true" checked>observable<br>
		    
		    <input type="button" value="remove selected" id="b_remove_selected">
		    <input type="button" value="remove all" id="b_remove_all">`;
	console.log("controls_draw_str = ", controls_draw_str);
	
	$("#controls_draw").html(controls_draw_str);
	
	var eq_number_eq = "";
	if (draw_eq_number)
	    eq_number_eq = self.get_equation_input("i_eq_num");
	
	var table_eq = "";
	if (draw_tables)
	    table_eq = self.net.table.draw("t_eqs_eqr", "b_eqr_add_eq_num",
					   "b_eqr_del_eq_num",
					   draw_bounds, draw_eq_number);

	var btype_eq = "";
	if(draw_bounds)
	    btype_eq = self.get_btype("s_btype_eq");

	var controls_eq_regions_str =
		`<input type="button" value="add_eq_region" id="b_add_region">
		    <br>`
		+ eq_number_eq
		+ `<br>
		    region color:<br>
		    <input id="sr_eq_color" value="255" min="0" max="255" style="display: block" type="range">
		    <p id="p_eq_sr_val"></p>                    
                    <br>
                    <br>`+ btype_eq
                + `<br>`
		+ table_eq
                + `<br>
		    <input id="param_observable" type="checkbox" value="true" checked>observable<br>
		    <select id="param_type" style="width: 100px">
		    <option>Rect</option>
		    <option>Circle</option>
		    <option>Text</option>
		    </select><br>`;
	$("#controls_eq_regions").html(controls_eq_regions_str);

	var eq_number_br = "";
	if (draw_eq_number)
	    eq_number_br = self.get_equation_input("i_eq_num_br");
	
	var table_br = "";
	if(draw_tables)
	    table_br = self.net.table.draw("t_eqs_br", "b_br_add_eq_num",
					   "b_br_del_eq_num",
					   draw_bounds, draw_eq_number);

	var btype_br = "";
	if(draw_bounds)
	    btype_br = self.get_btype("s_btype_br");

	var controls_br_regions_str =
		`<input type="button" value="add_br_region" id="b_add_region_br"><br>`
		+ eq_number_br
		+ `<br>
		    region color:<br>
		    <input id="sr_eq_color_br" value="255" min="0" max="255" style="display: block" type="range">
 		    <p id="p_eq_br_sr_val"></p>
		    <br>
                    
                    <br>`+ btype_br
                + `<br>`
		+ table_br
		+ `<br>      

		    side:
		    <select id="param_side" style="width: 100px">
		    <option>0</option>
		    <option>1</option>
		    <option>2</option>
		    <option>3</option>
		    </select><br>`;		
	$("#controls_br_regions").html(controls_br_regions_str);

	/*
	 <br><br>		       
	 <div id="models_tree_wrap" class="tree_positioned">
	 <div id="models_tree_wrap_style" class="style_editor_static editor_overflow tree_positioned">
	 <div id="models_tree"  class="tree_positioned"></div>
	 
         </div>
	 <div id="models_menu"></div> 		     
	 </div>
	 <div id="models_tree_input"></div>
	 <br>
	 */
	// 
	var controls_save_str =
		`	    
                    <input type="button" value="save" id="b_save_fabric_canvas">
	            <input type="button" value="reload" id="b_reload_fabric_canvas">	    
                    <br>
                    <div id="result" style="top: 83px; position: relative;">
		    Result
		    <br>
		    <img src="none.png" id="result_img"></img>
                    </div>
		    `;
	$("#controls_save").html(controls_save_str);
	
	// END FOR
	console.log("draw model scene done");
    };
    
    return {
	
	ModelsScene: ModelsScene
    };});
