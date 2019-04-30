console.log("log parser.js");


define(['jquery', 'modules/tnet', 'modules/tnet_tabs', 'modules/parser_params_tabs'],
       function($, tnet, tnet_tabs, params_tabs){
	   return {
	       Parser: function Parser(){
      		   /*
		     Create to_parse_div editable div for
		     writing sent to parse.
		     Call NetHandlerParsing at server side.
		     Get lex step result to lex_out_div.
		     Get net step result.
		    */
 		   var self = this;
		   self.net = new tnet.Net();
		   		   
		   self.create_parser = function(){
		       $("#frame_parser").css("top","20px");
		       // ui-widget ui-widget-content 
		       //	  + "Let(G: group(G) in: abelian(G)=>commutative(G),"
		       //	   + " commutative(G)=>abelian(G),)"

		       params_tabs.create_parser("#frame_before_parser");
		       
		       // FOR input tabs:
		       var board_str = 
			   ('<div id="tabs_input">'
			    + '<ul>'
			    + '<li><a href="#tif-0">lex</a></li>'
			    + '<li><a href="#tif-1">cs_0</a></li>'
			    + '<li><a href="#tif-2">cs_1</a></li>'
			    + '</ul>'
			    + '<div id="tif-0">'
			    + '</div>'
			    + '<div id="tif-1">'
			    + '</div>'
			    + '<div id="tif-2">'
			    + '</div>'
			    + '</div>'
			    + '<div id="lex_out_div" class="style_editor_static"'
			    + ' title="lex out"> </div>'+'<br>'
			    + '<div id="edit_parser_input" class="">'
			    + '<div id="epi_editor" contenteditable="true"'
			    + ' class=""></div>'
			    +'</div>');
		       $("#parser_div").html(board_str);
		       $("#parser_div").addClass("above_net_left");

		       ////// FOR lex:
		       var str_input0 = ('<div id="to_parse_div_0" title="click to edit"'
					+ ' class="style_editor_static ">'
					+ "U'=a*(D[U,{x,2}]+ D[U,{y,2}])"
					+ '</div>'
					+ '<br>'
					+ '<input id="button_parse_0" type="button"'
					+ ' value="parse" class="ui-button"><br>');
		       $("#tif-0").html(str_input0);
		       // $("#to_parse_div_0").addClass("above_net_left");
		       $("#to_parse_div_0").tooltip();
		       ////// END FOR

		       ////// FOR cs:
		       var str_input1 = ('<div id="to_parse_div_1" title="click to edit"'
					+ ' class="style_editor_static ">'
					+ "abelian(G) \\and subgroup(H, G,) => abelian(H)"
					+ '</div>'
					+ '<br>'
					+ '<input id="button_parse_1" type="button"'
					+ ' value="parse" class="ui-button"><br>');
		       $("#tif-1").html(str_input1);
		       // $("#to_parse_div_1").addClass("above_net_left");
		       $("#to_parse_div_1").tooltip();
		       ////// END FOR
		       $("#tabs_input").tabs();

		       /// $("#to_parse_div").css("width", "350");
		       /// $("#to_parse_div").css("height", "50");
		       
		       ////// FOR input editor:
		       var get_to_parse_div_callback = function(to_parse_div_id){
			   return(function(event){
			       // create dialog
			       console.log("create dialog");
			       console.log("dialog created");
			       $("#edit_parser_input").dialog({
				   resizable: true,
				   height: "auto",
				   width: 400,
				   modal: true,
				   open: function(event, ui){
				       console.log("dialog opend");
				       $("#edit_parser_input").toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
				       $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");
				       
				   },
				   close: function(event, ui){
				       console.log("dialog closed");
				       $("#edit_parser_input").toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
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

		       $("#to_parse_div_0").on("click",
					       get_to_parse_div_callback("#to_parse_div_0"));
		       $("#to_parse_div_1").on("click",
					       get_to_parse_div_callback("#to_parse_div_1"));
		       ////// END FOR

		       ////// FOR parse button:
		       var get_button_parse_callback = function(dialect, to_parse_div_id){
			   return(function(event){
			       var text = $(to_parse_div_id).text();
			       var params = {};
			       if (dialect == "eqs"){
				   params["dim"] = $("#param_dim").val();
				   params["blockNumber"] = $("#param_bn").val();
				   params["vars_idxs"] = $("#param_vidxs").val();
				   params["coeffs"] = $("#param_coeffs").val();
				   params["diffType"] = "pure";
				   params["diffMethod"] = $("#param_dm").val();
				   params["btype"] = $("#param_btype").val();
				   params["side"] = $("#param_side").val();
				   params["vertex_sides"] = $("#param_sn").val();
				   params["func"] = $("#param_func").val();
				   params["firstIndex"] = $("#param_fi").val();
				   params["secondIndexSTR"] = $("#param_si").val();
				   params["shape"] = $("#param_shape").val();
				   console.log("text for parsing:");
				   console.log(text);
				   console.log("params for parsing:");
				   console.log(params);
			       };
			   
			       self.parse(dialect, text, params);
			       // self.parse("eqs", text, params);
			   });
		       };

		       $("#button_parse_0").on("click",
					       get_button_parse_callback("eqs",
									 "#to_parse_div_0"));

		       $("#button_parse_1").on("click",
					       get_button_parse_callback("cs",
									 "#to_parse_div_1"));
		       ////// END FOR
		       // END FOR
		   };
		   
		   self.parse = function(dialect, text, params){
		       
		       // FOR sending data to server:
		       if(text.length){
			   var to_send = JSON.stringify({dialect: dialect,
							 text: text,
							 params: params});
			   // var to_send = data_to_send;
			   console.log("\n sending");
			   console.log(to_send);
			   
			   $.ajax(
			       {
				   url: 'api/net_parsing',
				   type: 'POST',
				   data: to_send,
				   
				   success: function (jsonResponse) {
				       var objresponse = JSON.parse(jsonResponse);
				       data_lex = objresponse['lex'];
				       data_net = objresponse['net'];
				       data_vars = objresponse["vars"];
				       data_output_cpp = objresponse["eq_cpp"];
				       data_output_sympy = objresponse["eq_sympy"];
				       data_output_slambda = objresponse["slambda"];

				       console.log("\ndata_lex");
				       console.log(data_lex);
				       console.log("\ndata_net");
				       console.log(data_net);
				       console.log("\ndata_vars");
				       console.log(data_vars);
				       console.log("\ndata_output_cpp");
				       console.log(data_output_cpp);
				       console.log("\ndata_output_sympy");
				       console.log(data_output_sympy);
				       console.log("\ndata_output_slambda");
				       console.log(data_output_slambda);

				       $("#lex_out_div").text(data_lex);
				       self.net.create_net(data_net);

				       // FOR create tabs:
				       tnet_tabs.create_tabs("#frame_after_parser", data_vars,
							     data_output_cpp, data_output_sympy,
							     data_output_slambda);
				       // END FOR

				       // copy data:
				       // var data_local = data.slice();
				       // $("#div_editor").text(data[0].kernel);
				   },
				   
				   error: function (data) {
				       console.log("error to send");
				       console.log(data);
				   }
			       });
		       }
		       else{
			   console.log("\n nothing to send");
		       };
		   };
		   
	       }
	   }
       });
