console.log("log models_editor_scene.js");

define(['jquery'], function($){

    return {
	draw_scene: function draw_scene(div_id){
	    // FOR scene:
	    var scene_str =
		    `<div id="scene_canvas" width="850" height="300"
	                style="border: 1px solid; border-width: 1px; border-color: black;">
		       <table>
		       <tr><td>
		          <canvas id="canvas" style="position: absolute; border: 1px solid; border-width: 1px;
                            border-color: #111111;" width="550" height="300"></canvas>
		       </td></tr></table>
                     </div>
                     <div id="controls"></div>`;

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
		    <div id="controls_save"></div>`;
	    $("#controls").html(controls_str);

	    var controls_draw_str =
		    `<input type="button" value="change draw mode" id="b_change_fabric_mode">
		    <br>
		    draw size: 
		    <input id="sr_draw_size" value="12" min="0.1" max="50" style="display: block" type="range">
		    <br>
		    draw color:
		    <input id="sr_draw_color" value="255" min="1" max="255" style="display: block" type="range">
		    <br>
		    <input id="param_draw_observable" type="checkbox" value="true" checked>observable<br>
		    
		    <input type="button" value="remove selected" id="b_remove_selected">
		    <input type="button" value="remove all" id="b_remove_all">`;
	    $("#controls_draw").html(controls_draw_str);

	    var controls_eq_regions_str =
		    `<input type="button" value="add_eq_region" id="b_add_region">
		    <br>
		    equation number:<br>
		    <input type="text" id="i_eq_num" value="2" class="style_button_number">
		    <br>
		    region color:<br>
		    <input id="sr_eq_color" value="255" min="0" max="255" style="display: block" type="range">
		    <br>
		    <input id="param_observable" type="checkbox" value="true" checked>observable<br>
		    <select id="param_type" style="width: 100px">
		    <option>Rect</option>
		    <option>Circle</option>
		    <option>Text</option>
		    </select><br>`;
	    $("#controls_eq_regions").html(controls_eq_regions_str);

	    var controls_br_regions_str =
		    `<input type="button" value="add_br_region" id="b_add_region_br"><br>
      
		    equation number:<br>
		    <input type="text" id="i_eq_num_br" value="2" class="style_button_number"><br>
		    region color:<br>
		    <input id="sr_eq_color_br" value="255" min="0" max="255" style="display: block" type="range">
		    <br>
      
		    side:
		    <select id="param_side" style="width: 100px">
		    <option>0</option>
		    <option>1</option>
		    <option>2</option>
		    <option>3</option>
		    </select><br>
		type:
		<select id="param_br_type" style="width: 100px">
		<option>Dirichlet</option>
		<option>Neumann</option>
		</select><br>`;		
	    $("#controls_br_regions").html(controls_br_regions_str);

	    var controls_save_str =
		    `<input type="button" value="save" id="b_save_fabric_canvas">
		    <br>
		    Result
		    <br>
		    <img src="none.png" id="result_img"></img>`;
	    $("#controls_save").html(controls_save_str);
	    // END FOR
	    console.log("draw model scene done");
	}
    };
});
