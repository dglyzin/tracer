console.log("log parser.js");


define(['jquery', 'modules/tnet'],
       function($, tnet){
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
			 
		       var str = ('<div id="to_parse_div" title="click to edit"'
				  + ' class="style_editor_static">'
				  + "U'=a*(sin(a+b)+U)+c*D[U,{x,2}]"
				  + '</div>'+'<br>'
				  + '<input id="button_parse" type="button"'
				  + ' value="parse" class="ui-button"><br>'
				  + '<div id="lex_out_div" class="style_editor_static" title="lex out"> </div>'+'<br>'

				  + '<div id="edit_parser_input" class="">'
				  + '<div id="epi_editor" contenteditable="true"'
				  + ' class=""></div>'
				  +'</div>');

		       $("#parser_div").html(str);
		       $("#parser_div").tooltip();
		       // $("#to_parse_div").css("width", "350");
		       // $("#to_parse_div").css("height", "50");
		       
		       $("#to_parse_div").on("click", function(event){
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
				       $("#to_parse_div").text(text);
				       $( this ).dialog( "close" );
				   },
				   Cancel: function() {
				       $( this ).dialog( "close" );
				   }
			       }
			   });
			   // $("#to_parse_div").toggleClass("ui-widget ui-corner-all ui-widget-shadow");
			   // $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");

			   $("#epi_editor").text($("#to_parse_div").text());
			   console.log("dialog created");
		       });

		       $("#button_parse").on("click", function(event){
			   var text = $("#to_parse_div").text();
			   
			   console.log("text for parsing:");
			   console.log(text);
			   self.parse("eqs", text);
		       });


		   };
		   
		   self.parse = function(dialect, text){
		       
		       // FOR sending data to server:
		       if(text.length){
			   var to_send = JSON.stringify({dialect: dialect,
							 text: text});
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
				       console.log("\ndata_lex");
				       console.log(data_lex);
				       console.log("\ndata_net");
				       console.log(data_net);
				       $("#lex_out_div").text(data_lex);
				       self.net.create_net(data_net);
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
