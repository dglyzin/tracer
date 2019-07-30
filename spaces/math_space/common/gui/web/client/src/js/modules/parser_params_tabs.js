console.log("log parser_params_tabs.js");

define(['jquery'], function($){

    return {
	create_parser: function create_parser(div_id){
	    $(div_id).addClass("right_net_center style_editor_static style_params_frame editor_overflow ui-draggable ui-draggable-handle");
	    
	    var board_str = 
		('<h4>parser params:</h4>'
		 + '<div id="tabs_parser_params">'
		 + '<ul>'
		 + '<li><a href="#params_general">General</a></li>'
		 + '<li><a href="#params_diff">Diff</a></li>'
		 + '<li><a href="#params_bdp">Bdp</a></li>'
		 + '</ul>'
		 + '<div id="params_general">'
		 + 'dim: <input type="text" id="param_dim" value="2" class="style_button_number"><br>'
                 + 'block number: <input type="text" id="param_bn" value="0" class="style_button_number"><br>'
                 + 'vars idxs: <input type="text" id="param_vidxs" value="[('+"'U'"+', 0), ('+"'V'"+', 1)]"><br>'
		 + ('coeffs: <input type="text" id="param_coeffs" value="[('+"'a'"+', 0), ('+"'b'"
		    +', 1), ('+"'c'"+', 2), ('+"'r'"+', 3), ('+"'d'"+', 4)]"><br>')
		 + '</div>'
		 + '<div id="params_diff">'
		 + ('diff method: <select id="param_dm" style="width: 100px">'
		    + '<option>common</option>'
		    + '<option>borders</option>'
		    + '<option>interconnect</option>'
		    + '<option>vertex</option>'
		    +'</select><br>')
		 + ('btype: <select id="param_btype" style="width: 10px">'
		    + '<option>0</option>'
		    + '<option>1</option>'
		    +'</select><br>')
		 + ('side: <select id="param_side" style="width: 10px">'
		    + '<option>0</option>'
		    + '<option>1</option>'
		    + '<option>2</option>'
		    + '<option>3</option>'
		    +'</select><br>')
		 + ('sides nums: <select id="param_sn" style="width: 100px">'
		      + '<option>[0, 2]</option>'
		      + '<option>[1, 2]</option>'
		      + '<option>[1, 3]</option>'
		      + '<option>[0, 3]</option>'
		      +'</select><br>')
		 + 'func: <input type="text" id="param_func" value="sin(x)" class="style_button_word"><br>'
		 + 'firstIndex: <input type="text" id="param_fi" value="0" class="style_button_number"><br>'
		 + 'secondIndexSTR: <input type="text" id="param_si" value="1" class="style_button_number"><br>'
		 + '</div>'
		 + '<div id="params_bdp">'
		 + 'shape: <input type="text" id="param_shape" value="[3, 3]" class="style_button_word"><br>'
		 + '</div>'
		 + '</div>');
	    //  
	    $(div_id).html(board_str);
	    $("#tabs_parser_params").tabs();
	    
	    }
    }
});
