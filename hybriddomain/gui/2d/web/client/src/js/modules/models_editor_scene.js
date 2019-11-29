console.log("log models_editor_scene.js");

define(['jquery', 'jquery-ui-custom/jquery-ui'], function($, ui){

    return {
	draw_scene: function draw_scene(div_id){
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

	    var controls_draw_str =
		    `<input type="button" value="change draw mode" id="b_change_fabric_mode">
		    <br>
		    draw size: 
		    <input id="sr_draw_size" value="12" min="0.1" max="50" style="display: block" type="range">
		    <br>
		    draw color:
		    <input id="sr_draw_color" value="255" min="1" max="255" style="display: block" type="range">
		    <br>
                    <input type="text" id="i_eq_num_draw" value="0" class="style_button_number">
                    <br>
                    <input type="button" value="add color" id="b_draw_add_eq_num">
                    <br>
                    <table id="t_eqs_draw" class="style_table">
                      <tr class="style_table">
                       <td class="style_table">color</td><td class="style_table">eq_num</td>
                      </tr>
                      <tr>
                       <td>1 </td> <td>2</td>
                      </tr>
                    </table>
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

	    // <input type="button" value="save" id="b_save_fabric_canvas">
	    var controls_save_str =
		    `
		    <br><br>		       
		    <div id="models_tree_wrap" class="tree_positioned">
		     <div id="models_tree_wrap_style" class="style_editor_static editor_overflow tree_positioned">
		      <div id="models_tree"  class="tree_positioned"></div>

                     </div>
		      <div id="models_menu"></div> 		     
		    </div>
		    <div id="models_tree_input"></div>
		    <br>
		    <input type="button" value="open" id="b_open_fabric_canvas">
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
	}
    };
});
