console.log("log tnet_tabs.js");

define(['jquery'], function($){

    return {
	create_tabs: function create_tabs(div_id, data_vars, data_cpp, data_sympy){

	    $(div_id).addClass("above_net_bottom style_editor_static style_replacer_frame");

	    var board_str = 
		('<h3>Output:</h3>'
		 + '<div id="tabs">'
		 + '<ul>'
		 + '<li><a href="#fragment-1">Vars</a></li>'
		 + '<li><a href="#fragment-2">Replacer</a></li>'
		 + '<li><a href="#fragment-3">sLambda</a></li>'
		 + '</ul>'
		 + '<div id="fragment-1">'
		 + '</div>'
		 + '<div id="fragment-2">'
		 + '</div>'
		 + '<div id="fragment-3">'
		 + '</div>'
		 + '</div>')
	    $(div_id).html(board_str);
	    
	    // FOR vars:
	    var vars_list_str = (('<ul/ id="vars_list"'
				  +'class="ui-menu ui-widget ui-widget-content">')
				 +'</ul>');
	    $("#fragment-1").html(vars_list_str);
	    
	    // add vars to list:
	    var vars_to_add = $.map(data_vars, function(elm, id){
		return(('<li class="ui-menu-item ui-widget'
			+ ' ui-widget-content border_vars_width">')
		       + 'term_id: ' + elm['id']['term_id']
		       + '; var: ' + elm['id']['var']
		       + '; val: ' + elm['id']['val'] + '</li>');
	    });
	    $("#vars_list").append(vars_to_add.join(""));
	    // $("#fragment-1").text(data_vars);
	    // END FOR
	    var replacer_data = "".concat("<h3>", "cpp:", "</h3>", "<br>",
					  data_cpp, "<br>",
					  "<h3>", "sympy:", "</h3>", "<br>", data_sympy);
	    $("#fragment-2").html(replacer_data);
	    $("#fragment-3").text("implementing now");
	    
	    $("#tabs").tabs();	    
	}
    }
});
