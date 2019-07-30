console.log("log sampler.js");


define(['jquery', 'modules/parser_base', 'modules/tnet',
	'modules/tnet_tabs'],
       function($, parser_base, tnet, tnet_tabs){
	   return {
	       Sampler: function Sampler(){
      		   /*
		     Create to_parse_div editable div for
		     writing sent to parse.
		     Call NetHandlerParsing at server side.
		     Get lex step result to lex_out_div.
		     Get net step result.
		    */
 		   var self = this;
		   self.pbase = new parser_base.ParserBase();
		   self.net = new tnet.Net();
		   		   
		   self.create_sampler = function(){
		       $("#frame_parser").css("top","20px");

		       // FOR input tabs:

		       var input_names = ["cs_0"];
		       var input_default_contents = ["abelian(G) \\and subgroup(H, G,) => abelian(H)"];
		       var input_buttons_callbacks = [self.get_button_sampling_callback_cs];
		       
		       self.pbase.create_input_field("#parser_div", "parser",
						     input_names, input_default_contents,
						     input_buttons_callbacks);
		       // END FOR
		   };
		   

		   self.get_button_sampling_callback_cs = function(to_parse_div_id){
			   return(function(event){
			       var text = $(to_parse_div_id).text();
			       var params = {};   
			       // self.run("cs", text, params);
			       self.parse("cs", text, params);
			       // self.parse("eqs", text, params);
			   });
		   };

		   
		   self.parse = function(dialect, text, params){
		       
		       /*parse text with dialect parser
			 and print parsed cytoscape net
			 and set result to "#frame_after_parser"
			 result will be: lex out, cpp/sympy out
		         vars, slambda out*/
		       
		       // FOR sending data to server:
		       if(text.length){
			   // mode parse, sampling:
			   var to_send = JSON.stringify({mode: "parse",
							 dialect: dialect,
							 text: text,
							 params: params});
			   // var to_send = data_to_send;
			   console.log("\n sending");
			   console.log(to_send);
			   
			   $.ajax(
			       {
				   url: '/sampling',
				   type: 'POST',
				   data: to_send,
				   
				   success: function (jsonResponse) {
				       var objresponse = JSON.parse(jsonResponse);
				       
				       var data_slambda = objresponse["slambda"];
				       console.log("\ndata_output_slambda");
				       console.log(data_slambda);

				       $("#lex_out_div").text("done");
				       // self.net.create_net(data_net);

				       // FOR create tabs:
				       var board_str =
					   ('<div id="sampling_board">');
				       board_str = self.create_vtable(board_str,
								      data_slambda["vtable_skeleton"]);
				       board_str = self.create_stable(board_str,
								      data_slambda["stable"]);
				       self.create_button(board_str);
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
		
		   self.create_vtable = function(board_str, vtable_data){
		       
		       // FOR vtable
		       board_str += "<h3>vtable:</h3>";
		       board_str += "<p>Each value can be seated or not.</p>";
		       board_str += "<p>All missing values will be generated.</p>";
		       board_str += "<p>(according to signatures availability)</p>";

		       board_str += ('<table'
				     + ' class="style_table">');
		       board_str += '<tr id="sampling_vtable_names">';
		       $.each(vtable_data,
			      function(elm, id){
				  board_str += ('<td class="style_table">'
						+ id[0]
						+ '</td>');});
		       board_str += "</tr><tr>";
		       
		       $.each(vtable_data,
			      function(elm, id){
				  board_str += ('<td class="style_table">'
						+ id[1]
						+ '</td>');});
		       board_str += '</tr><tr id="sampling_vtable_values">';
		       
		       $.each(vtable_data,
			      function(id, elm){
				  board_str += ('<td class="style_table">');
				  board_str += ('<input type="text"'
						+ ' class="style_table_input"');
				  console.log("found");
				  console.log(elm[0]);
				  console.log(elm[0].indexOf("s")!==-1);
				  
				  // set default values for predicates terms:
				  if(elm[0].indexOf("s")!==-1){
				      board_str += ('value="True"');
				  };
				  board_str += '>';
				  board_str += '</td>';});
		       board_str += "</tr></table>";
		       // END FOR
		       return(board_str);
		   };
		   
		   self.create_stable = function(board_str, stable_data){
		       // FOR stable:
		       board_str += "<h3>stable:</h3>";
		       board_str += "<p>Signature for each node.</p>";
		       board_str += "<p>There is generator behind each signature.</p>";
		       board_str += '<p>(see "sampling/slambda/data/gens/algebra/group.py").</p>';
		       board_str += ('<table class="style_table">');

		       $.each(stable_data,
			      function(elm, id){
				  board_str += "<tr>";
				  
				  board_str += ('<td class="style_table">'
						+ elm
						+ '</td>');
				  $.each(id,
					 function(elm, id){
					     board_str += ('<td class="style_table">'
							   + id
							   + '</td>');
					 });
				  board_str += "</tr>";
			      });
		       board_str += "</tr></table>";
		       // END FOR
		       return(board_str);
		   };

		   self.create_button = function(board_str){
		       
		       board_str += ('<input id="button_sampling" type="button"'
				     + ' value="run" class="ui-button">');
		       board_str += "</div>";
		       
		       $("#sampling_div").html(board_str);
		       // END FOR

		       $("#button_sampling").on("click", function(){
			   self.run();
		       });

		   };

		   self.run = function(){
		   		       
		       // FOR sending data to server:
		       if(true){
			   vtnames = self.get_vtable_names();
			   vtvalues = self.get_vtable_values();
			   
			   // reparse for clear
			   // var text = $(to_parse_div_id).text();

			   // mode parse, sampling:
			   var to_send = JSON.stringify({mode: "sampling",
							 vtnames: vtnames,
							 vtvalues: vtvalues});
			   // var to_send = data_to_send;
			   console.log("\n sending");
			   console.log(to_send);
			   
			   $.ajax(
			       {
				   url: '/sampling',
				   type: 'POST',
				   data: to_send,
				   
				   success: function (jsonResponse) {
				       var objresponse = JSON.parse(jsonResponse);
				       
				       var data_slambda = objresponse;
				       console.log("\ndata_output_slambda");
				       console.log(data_slambda);

				       // FOR changing vtable according to sampling result:		
				       var names = self.get_vtable_names();
				       var successors = data_slambda["successors"];
				       var net = data_slambda["vesnet"];
				       self.net.create_net(net);

				       if(successors.length == 0){
					   $("#lex_out_div").text("no results");
					   return("");
				       };
				       var new_values = data_slambda["successors"][0];
				       
				       $("#sampling_vtable_values td input").each(
					   function(id, elm){
					       // console.log($(elm).text());
					       $(elm).val(new_values[names[id]]);
					       // console.log(id);
					   });
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

		   self.get_vtable_names = function(){
		       
		       var names = [];
		       $("#sampling_vtable_names td").each(
			   function(id, elm){
			       // console.log($(elm).text());
			       names.push($(elm).text());
			       // console.log(id);
			   });
		       console.log(names);
		       return(names);
		   };
		   
		   self.get_vtable_values = function(){
		       var values = [];
		       $("#sampling_vtable_values td input").each(
			   function(id, elm){
			       // console.log($(elm).text());
			       values.push($(elm).val());
			       // console.log(id);
			   });
		       console.log(values);
		       return(values);
		   }
	       }
	   }
       });
