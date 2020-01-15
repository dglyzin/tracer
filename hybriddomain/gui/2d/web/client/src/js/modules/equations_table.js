console.log("log equations_table.js");
define(['jquery', 'jquery-ui-custom/jquery-ui'],
       
       function($, ui){
	   
	   function EquationsTable(net){
	       
	       // FOR global variables:
	       var self = this;
	       self.net = net;
	       self.eqs_table = self.eqs_table || [];
	       self.eqs_table_selected_row_val = self.eqs_table_selected_row_val || 255;

	       self.button_save_id = "b_save_table";
	       self.button_add_id = "b_add_equation";
	       self.button_del_id = "b_del_equation";
	       self.table_id = "t_equations";
	       self.table_editor_id = "d_te_equations";
	       self.selected_rowIndex = undefined;
	       // END FOR    	       
	   };

	   EquationsTable.prototype.save= function(){
	       /*save table to list of lists*/
	       var self = this;
	       
	       var table_rows = $("#"+ self.table_id +" tr");
	       console.log("table_rows = ", table_rows);
	       var table = $.map(table_rows, function(row, id){
		   return([$.map(row.children, function(column, id){
		       return($(column).text());
		   })]);
		   // console.log(row);
	       });
	       /*
	       var table = $.map(table_rows, function(row, id){
		   return($.map(row, function(column, id){
		       return(column);
		   }));
	       });
		*/
	       console.log("table = ", table);
	       
	       return(table);
	   };

	   EquationsTable.prototype.remove = function(){

	       // clear scene:
	       var children = $("#scene").children();
	       console.log("children = ", children);
	       $.each(children, function(id, elm){
		   console.log("elm = ", elm);
		   console.log("elm = ", elm);
		   elm.remove();
	       });
	       
	    };
	   
	  
	   EquationsTable.prototype.update = function(content_type){
	       var self = this;
	       
	       // clear scene:
	       self.remove();

	       self.draw("#scene");
	   };

	   EquationsTable.prototype.init_board = function(){
	       console.log("EquationsTable.init_board");
	   };


	   EquationsTable.prototype.load = function(data){
	       var self = this;
	       var table_list = data["table"];
	       var to_send = data["in"];

	       self.remove();
	       console.log("EquationsTable.load:");
	       self.draw("#scene", table_list);
	       self.set_on_row_click();
	       self.set_editor_callback();
	       self.apply_buttons(to_send);
	   };


	   EquationsTable.prototype.draw_table = function(wt_id, table_list){
	       var self = this;

	       var table_str = ('<table id="'+ self.table_id +'" class="style_table">');

	       var content = "";
	       $.each(table_list, function(id, row){
		   content += '<tr>';
		   $.each(row, function(id, column){
		       content += '<td class="style_table">' + column + "</td>";
		   });
		   content += "</tr>";
	       });
	       
	       table_str += content;
	       table_str += '</table>';
	       $(wt_id).html(table_str);
	   };

	   EquationsTable.prototype.draw = function(div_id, table_list){

	       /*draw wrapper to div_id, fill it with table_list*/

	       var self = this;

	       // wrapper:
	       var wrapper_str = ('<div id="d_table_controls" class="wrapper_table_top"></div><br>'
				  + '<div id="d_table" class="wrapper_table_center"></div><br>'
				  + '<div id="d_table_edit" class="wrapper_table_bottom"></div>');
	       $(div_id).html(wrapper_str);
	       
	       var table_controls_str = ('<input type="button" value="add new" id="'
					 + self.button_add_id+'">'
					 + '<input type="button" value="del row" id="'
					 + self.button_del_id+'">'
					 + '<input type="button" value="save table" id="'
					 + self.button_save_id+'">');
	       $("#d_table_controls").html(table_controls_str);

	       self.draw_table("#d_table", table_list);
	       
	       var table_edit_str = ('<h3>Row Editor</h3><p>(Click at row to edit)<p>'
				     + '<div id="'+self.table_editor_id+'"'
				     + 'class="table_editor"'
				     // + 'style="display: block"'
				     +'contenteditable="true"'+'>'
				     + '</div>');
	       $("#d_table_edit").html(table_edit_str);

	       /*
	       var number = "eq_num";
	       if(draw_bounds)
		   number = "br_num";

	       if(draw_eq_number)
		   header += `<td class="style_table">`+number+`</td>`;

	       if(draw_bounds)
		   header += `<td class="style_table">btype</td>`;
	       header += `</tr>`;

	       return(`<input type="button" value="add new" id="`+b_id+`">
                    <br>
                    <table id="`+ table_id +`" class="style_table">`
		      + header 
		      + `</table>`);
		*/
	   };

	   EquationsTable.prototype.apply_buttons = function(to_send){
	       
	       var self = this;
	       
	       $("#"+self.button_save_id).on("click", function(){
		   /*Save table*/
		   
		   to_send["mode"] = "save";
		   to_send["node"]["node_data"] = {};
		   to_send["node"]["node_data"]["table"] = self.save();
		   console.log("to_send:");
		   console.log(to_send);
		   self.net.tree.tree.send_data(self.net.tree.url, to_send);
		   
	       });	       
	       
	       $("#"+self.button_del_id).on("click", function(){
		   /*Del selected row*/
		   $("#"+ self.table_id +" tr.table_selected_row").remove();
		   
	       });
	       
	       $("#"+self.button_add_id).on("click", function(){
		   /*Add row either after selected or after last.*/

		   var selected_rows = $("#"+ self.table_id +" tr.table_selected_row");
		   console.log("selected_rows = ", selected_rows);

		   var new_rowIndex = undefined;

		   if(selected_rows.length){
		       // if(self.selected_rowIndex)
		       // insert after selected:

		       new_rowIndex = selected_rows[0].rowIndex+1;
		       $("#"+ self.table_id +" tr.table_selected_row").after('<tr><td class="style_table">'
									     + 'new entry '+ new_rowIndex
									     +'</td></tr>');
		   }
		   else{
		       // insert to the end:

		       var last_rowIndex = $("#"+self.table_id+" tr").last()[0].rowIndex;
		       console.log("last_rowIndex = ", last_rowIndex);
		       
		       new_rowIndex = last_rowIndex + 1;
		       
		       $("#"+self.table_id).append('<tr><td class="style_table">'
						   + 'new entry '+ new_rowIndex
						   +'</td></tr>');
		   }
	       });
	   };			    

	   EquationsTable.prototype.set_editor_callback = function(){
	       /*
		Change selected table row.td when chenging editor text.
		*/
	       var self = this;
	       
	       $("#"+self.table_editor_id).on("keyup",  function(){
		   		   
		   console.log("table:");
		   console.log($("#" + self.table_id));
		 
		   var selected_rows = $("#"+ self.table_id +" tr.table_selected_row");
		   console.log("selected_rows = ", selected_rows);
		   
		   if(selected_rows.length){
		       $(selected_rows[0].children[0]).text($.text(this));
		   }		   
		   
	       });
	   };
	   
	   EquationsTable.prototype.set_on_row_click = function(){
	       var self = this;
	       	   
	       // this will work dynamically i.e. applies to tr which
	       // was added with $.append:
	       $("#"+self.table_id).on("click", "tr", function(){
		   // $("#"+color_input_id+" tr").on("click", function(){
		   console.log("tr click |-> color_val:");
		   console.log(this);
		   self.selected_rowIndex = this.rowIndex;
		   console.log("selected_row (this.rowIndex):");
		   console.log(self.selected_rowIndex);

		   var td_val = $.text(this.children[0]);
		   console.log(td_val);

		   // add to selected row value:
		   self.eqs_table_selected_row_val = td_val;
		   
		   // FOR set color:
		   $("#"+self.table_id+" tr.table_selected_row").removeClass("table_selected_row");
		   
		   $(this).addClass("table_selected_row");
		   /*
		   console.log("tr.style:");
		   console.log(this.parentElement.children);
		   $.each(this.parentElement.children, function(id, elm){
		       elm.setAttribute("style", "background-color: white");
		   });
		   // this.setAttribute("style", "color: blue");
		   this.setAttribute("style", "background-color: blue");
		    */
		   // END FOR

		   // FOR add to editor:
		   $("#"+self.table_editor_id).text(td_val);
		   // console.log('$("#"+self.table_editor_id)');
		   // console.log($("#"+self.table_editor_id));
		   // END FOR
	       });
	       

	   };
	   return {
	       ETable: EquationsTable 		   
	   };

       });
