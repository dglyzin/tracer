console.log("log models_table.js");
define(['jquery', 'jquery-ui-custom/jquery-ui'],
       
       function($, ui){
	   
	   function ModelsTable(net){
	       
	       // FOR global variables:
	       var self = this;
	       self.net = net;
	       self.eqs_table = self.eqs_table || [];
	       self.eqs_table_selected_row_val = self.eqs_table_selected_row_val || 255;
	       // END FOR    	       
	   };

	   ModelsTable.prototype.set_on_row_click = function(tables_ids){
	       var self = this;

	       $.each(tables_ids, function(id, table_id){
		   
		   // this will work dynamically i.e. applies to tr which
		   // was added with $.append:
		   $("#"+table_id).on("click", "tr", function(){
		       // $("#"+color_input_id+" tr").on("click", function(){
		       console.log("tr click |-> color_val:");
		       var color_val = $.text(this.children[0]);
		       console.log(color_val);

		       // add to selected row value:
		       self.eqs_table_selected_row_val = color_val;

		       // FOR set color:
		       console.log("tr.style:");
		       console.log(this.parentElement.children);
		       $.each(this.parentElement.children, function(id, elm){
			   elm.setAttribute("style", "background-color: white");
		       });
		       // this.setAttribute("style", "color: blue");
		       this.setAttribute("style", "background-color: blue");
		       // END FOR

		       // FOR apply to canvas:
		       console.log("freeDrawingBrush:");
		       console.log(self.net.canvas.freeDrawingBrush);
		       
		       var color = "rgba("+ color_val+","+ color_val+","+ color_val+","+"1.0)";
		       self.net.canvas.freeDrawingBrush.color = color;
		       console.log(self.net.canvas.freeDrawingBrush.color);
		       // END FOR
		   });
	       });
	   };

	   ModelsTable.prototype.apply_eqs_table = function(b_add_eq_id, tables_ids,
						            i_eq_num_id, sr_eq_color_id, s_btype_id){
	       
	       /*Apply colors/equations_numbers table's button callback for draw tab
		if s_btype_id given, rows format will be:
		[color_val, eq_num, btype]
		if i_eq_num_id is given:
		[color_val, eq_num]
		else:
		[color_val]
		*/
	       
	       var self = this;
	        $("#"+b_add_eq_id).on("click", function(){
		    var color_val = $("#"+sr_eq_color_id).val();
		    
		    // if i_eq_num_id is given:
		    if(i_eq_num_id)
			var eq_num = $("#"+i_eq_num_id).val();
		    
		    if($.map(self.eqs_table, function(elm, id){
			return(elm[0]);}).indexOf(color_val) < 0)
		    {
			if(i_eq_num_id){
			    // if i_eq_num_id is given:

			    if(s_btype_id){
				// if s_btupe_id is given:

				var param_type = $("#"+s_btype_id).val();
				console.log("param_type");
				console.log(param_type);
				$.each(tables_ids, function(id, table_id){
				    $("#"+table_id).append( '<tr><td>'+color_val+ '</td>'
							    + ' <td>'+eq_num+'</td>'
							    +' <td>'+param_type+'</td></tr>');
				});
				
				self.eqs_table.push([color_val, eq_num, param_type]);
			    }
			    else{
				$.each(tables_ids, function(id, table_id){
				    $("#"+table_id).append( '<tr><td>'+color_val+ '</td>'
							    + ' <td>'+eq_num+'</td></tr>');
				});
				self.eqs_table.push([color_val, eq_num]);
			    }}
			else{
			    $.each(tables_ids, function(id, table_id){
				
				$("#"+table_id).append( '<tr><td>'+color_val+ '</td></tr>');
			    });
			    self.eqs_table.push([color_val]);
			}
		    }else{
			throw new Error("cannot add more then one eq to"
					+ " one color");
		    }
		    console.log("self.eqs_table = ", self.eqs_table);
		});
	   };


	   ModelsTable.prototype.draw = function(table_id, b_id, draw_bounds,
						 draw_eq_number){

	       /*get difer table depend on draw_bounds/ draw_eq_number*/

	       var header = (`<tr class="style_table">`
			     + `<td class="style_table">color</td>`);
	       var number = "eq_num";
	       if(draw_bounds)
		   number = "br_num";

	       if(draw_eq_number)
		   header += `<td class="style_table">`+number+`</td>`;

	       if(draw_bounds)
		   header += `<td class="style_table">btype</td>`;
	       header += `</tr>`;

	       return(`<input type="button" value="add color" id="`+b_id+`">
                    <br>
                    <table id="`+ table_id +`" class="style_table">`
		      + header 
		      + `</table>`);
	   };
	   return {
	       ModelsTable: ModelsTable 		   
	   };

       });
