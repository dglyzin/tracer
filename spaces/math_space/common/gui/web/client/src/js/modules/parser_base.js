console.log("log parser_base.js");


define(['jquery'],
       function($){
	   return {
	       ParserBase: function ParserBase(){

		   var self = this;

		   self.create_input_field = function(div_id, subdiv_id_name,
						      input_names, input_default_contents,
						      input_buttons_callbacks){
		       /*
			 Create editable field tab for each input in ``input_names``
			 All ``input_names``, ``input_default_content``,
			 ``input_buttons_callbacks`` must have some length.
			 
			 - ``div_id`` -- id for div, which be used.
			 
			 - ``subdiv_id_name`` -- name for sub id's, which be used.

			 - ``input_names`` -- list with names for each tab.
			 (ex: ["lex", "cs_0"])

			 - ``input_default_contents`` -- default content of each field.
			 (ex: ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])",
			 "abelian(G) \\and subgroup(H, G,) => abelian(H)"])

			 - ``input_buttons_callbacks`` -- callbacks for buttons.
			*/

		       
		       var board_str = 
			   ('<p class="ui-widget-header">header</p>'
				   + '<div id="tabs_input">'
			    + '<ul>');
		       $.each(input_names,
			      function(elm, id){
				  board_str += ('<li><a href="#tif-'
						+ elm
						+ '">'+id+'</a></li>');});
		       board_str += '</ul>';
		       
		       $.each(input_names,
			      function(elm, id){
				  board_str += ('<div id="tif-'
						+ elm
						+ '"></div>'
					       );});
		       
		       board_str +=
		       ('</div>'
			+ '<div id="lex_out_div" class="style_editor_static"'
			+ ' title="lex out"> </div>'+'<br>'
			+ '<div id="edit_'+ subdiv_id_name +'_input" class="">'
			+ '<div id="epi_editor" contenteditable="true"'
			+ ' class=""></div>'
			+'</div>');
		       $(div_id).html(board_str);
		       $(div_id).addClass("above_net_left");
		       
		       $.each(input_default_contents,
			      function(elm, id){
				  var str_input =
				      ('<div id="to_'+subdiv_id_name
				       +'_div_'+ elm +'" title="click to edit"'
				       + ' class="style_editor_static ">'
				       + id
				       + '</div>'
				       + '<br>'
				       + '<input id="button_'+subdiv_id_name+ '_'+elm+'" type="button"'
				       + ' value="'+subdiv_id_name+'" class="ui-button"><br>');
				  $("#tif-"+elm).html(str_input);
				  $("#to_"+subdiv_id_name+"_div_"+elm).tooltip();
			      });

		       $("#tabs_input").tabs();
		       $(div_id).draggable({handle: "p.ui-widget-header"});
		       /// $("#to_parse_div").css("width", "350");
		       /// $("#to_parse_div").css("height", "50");
		       
		       $.each(input_default_contents,
			      function(elm, id){
				  // for editor:
				  var edit_id = "#to_"+subdiv_id_name+"_div_"+elm;
				  $(edit_id).on("click",
						self.get_to_parse_div_callback(subdiv_id_name,
									       edit_id));
				  // for parse button:
				  var but_id = "#button_"+subdiv_id_name+"_"+elm;
				  $(but_id).on("click",
					       input_buttons_callbacks[elm](edit_id));
				  
			      });
		       // END FOR
		   };


		   self.get_to_parse_div_callback = function(subdiv_name, to_parse_div_id){

		       /* for input editor
			  (with contenteditable="true" attribute)
			  with use of jquery.dialog.
		       */

		       return(function(event){
			   // create dialog
			   console.log("create dialog");
			   console.log("dialog created");
			   var subdiv_id = "#edit_" + subdiv_name + "_input";
			   $(subdiv_id).dialog({
			       resizable: true,
			       height: "auto",
			       width: 400,
			       modal: true,
			       open: function(event, ui){
				   console.log("dialog opend");
				   $(subdiv_id).toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
				   $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");
				   
			       },
			       close: function(event, ui){
				   console.log("dialog closed");
				   $(subdiv_id).toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
				   $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");
				   
			       },
			       buttons: {
				   "Edit": function() {
				       console.log("dialog text");
				       var text = $("#epi_editor").text();
				       console.log(text);
				       $(to_parse_div_id).text(text);
				       // $("#to_parse_div").text(text);
				       $( this ).dialog( "close" );
				   },
				   Cancel: function() {
				       $( this ).dialog( "close" );
				   }
			       }
			   });
			   // $("#to_parse_div").toggleClass("ui-widget ui-corner-all ui-widget-shadow");
			   // $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");
			       
			   $("#epi_editor").text($(to_parse_div_id).text());
			   console.log("dialog created");
		       });
		   };
		   
	       }}});
