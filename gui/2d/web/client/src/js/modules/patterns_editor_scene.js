console.log("log patterns_editor_scene.js");

define(['jquery'], function($){

    return {
	draw_scene: function draw_scene(div_id){
	    // FOR scene:
	    var scene_str =
		    `<div id="scene_canvas" width="850" height="300"
	                style="border: 1px solid; border-width: 1px; border-color: black;">
		       <table><tr><td>
		          <canvas id="canvas" style="position: absolute; border: 1px solid; border-width: 1px;
                            border-color: #111111;" width="550" height="300"></canvas>
		        </td>
		        <td>
	                 <canvas id="canvas_patterns" style="position: absolute;border: 1px solid; black;"
	                   width="300" height="300"></canvas>
		        </td></tr></table>
                     </div>
                     <div id="controls"></div>`;
	    
	    $(div_id).html(scene_str);
	    // END FOR

	    // FOR controls:
	    var controls_str = 
		    `<ul>
		     <li><a href="#controls_draw">draw mode</a></li>
                     <li><a href="#controls_regions">regions</a></li>
		     <li><a href="#controls_patterns">patterns</a></li>
                     <li><a href="#controls_save">save</a></li>
		    </ul>
		    <div id="controls_draw"></div>
		    <div id="controls_regions"></div>
                    <div id="controls_patterns"></div>
		    <div id="controls_save"></div>`;
	    $("#controls").html(controls_str);

	    var controls_draw_str =
		    `<input type="button" value="change draw mode" id="b_change_fabric_mode">
		    <br>
		    <input id="sr_draw_size" value="12" min="0.1" max="50" style="display: block" type="range">
		    <br>
		    draw color:
		    <input id="sr_draw_color" value="1" min="1" max="255" style="display: block" type="range">
		    <br>
		    <input type="button" value="remove selected" id="b_remove_selected">
		    <input type="button" value="remove all" id="b_remove_all">`;
	    $("#controls_draw").html(controls_draw_str);

	    var controls_regions_str =
		    `<input type="button" value="add_region" id="b_add_region">
		    <br>
		    equation number:<br>
		    <input type="text" id="i_eq_num" value="2" class="style_button_number">
		    <br>
		    region color:<br>
		    <input id="sr_eq_color" value="12" min="0" max="255" style="display: block" type="range">
		    <br>
		    <select id="param_type" style="width: 100px">
		    <option>Rect</option>
		    <option>Sphere</option>
		    <option>Text</option>
		    </select><br>`;
	    $("#controls_regions").html(controls_regions_str);
	    
	    var controls_patterns_str =
		    `<input type="button" value="group selected" id="b_group">
		    <input type="button" value="ungroup selected" id="b_ungroup">`;
	    $("#controls_patterns").html(controls_patterns_str);
	    // END FOR
	    console.log("draw patterns scene done");
	}
    };
});
