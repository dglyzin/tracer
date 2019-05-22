console.log("log tnet_tabs.js");

define(['jquery'], function($){

    return {
	create_tabs: function create_tabs(div_id, data_vars, data_cpp, data_sympy,
					  data_slambda){

	    $(div_id).addClass("above_net_bottom style_editor_static style_replacer_frame");

	    var board_str = 
		('<p class="ui-widget-header">header</p>'
		 + '<h3>Output:</h3>'
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

	    // FOR replacer
	    var replacer_data = "".concat("<h3>", "cpp:", "</h3>", "<br>",
					  data_cpp, "<br>",
					  "<h3>", "sympy:", "</h3>", "<br>", data_sympy);
	    $("#fragment-2").html(replacer_data);
	    // END FOR

	    // FOR slambda:
	    var slambda_data = ('<input type="checkbox" id="slambda_only"'
				+ ' value="true">'
				+ '<label for=slambda_only>slambda only</label>'
				+ '<br>');
	    slambda_data += ('<table class="style_table">');
	    slambda_data += "<tr>";
	    $.each(data_slambda["vtable_skeleton"],
		   function(elm, id){
		       slambda_data += ('<td>'
					+ id[0]
					+ '</td>');});
	    slambda_data += "</tr><tr>";
	    
	    $.each(data_slambda["vtable_skeleton"],
		   function(elm, id){
		       slambda_data += ('<td>'
					+ id[1]
					+ '</td>');});
	    slambda_data += "</tr></table>";
	    console.log("slambda_data:");
	    console.log(slambda_data);

	    $("#fragment-3").html(slambda_data);
	    // $("#fragment-3").text("implementing now");
	    // END FOR

	    $("#tabs").tabs();
	    $(div_id).draggable({handle: "p.ui-widget-header"});
	    // $("#slambda_only").checkboxradio();
	    console.log("input value");
	    console.log($("#slambda_only"));
	}
    }
});
