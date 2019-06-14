console.log("log ttable.js");


//['jquery', 'jquery-ui-custom/jquery-ui'],
//
define(['require', 'jquery', 'jquery-ui-custom/jquery-ui', 'tabulator/tabulator.min',
	
	"codemirror", "codemirror/mode/python/python",
        "codemirror/keymap/emacs",
	"codemirror/addon/edit/matchbrackets",
	"codemirror/addon/comment/comment",
	"codemirror/addon/dialog/dialog",
	"codemirror/addon/search/searchcursor",
	"codemirror/addon/search/search",
        ],
       function($, ui, tabulator, CodeMirror){

	   $ = require('jquery');
	   jquery_ui = require('jquery-ui-custom/jquery-ui');
	   tabulator = require('tabulator/tabulator.min');
	   CodeMirror = require('codemirror');
	   return {
	       Table: function Table(table_index, table_name){
      
		   // FOR global variables:

		   var self = this;
		   
		   self.editor = [];
		   // checker for test table button state:
		   this.scene_checker = 0;
	       
		   // index for using like primary key
		   // (in uniqueness rows check):
		   this.table_index = typeof table_index !== 'undefined' ? table_index : "id";  // "id";
    
		   // name of table to wait from server:
		   this.table_name = typeof table_name !== 'undefined' ? table_name : "unnamed_table";
		   // index for selecting:
		   this.s_index = 0;
		   
		   // checker for add button state:
		   this.add_checker = 0;
		   
		   // for main and add tables:
		   // this.data = [];
		   this.data_add = [];
		   this.data_add_storage = [];
		   this.data_delete_storage = [];
		   this.columns = [];
		   this.columns_add = [];
		   // END FOR

		   // for replacer set:
		   self.row_data = "none";
		   
		   // for replacer delete:
		   self.row_data_delete = "none";

		   this.remove_table = function(){

		       if (self.table_name == "dialect"){
			   console.log("replacer");
			   console.log($("#replacer"));
			   if($("#replacer").length){
			       // console.log(self);
			       // console.log(self.editor);
			       self.editor.toTextArea();
			       console.log("codemirror.toTextArea done");
			       $("#replacer").remove();
			       $("#replacer_info").remove();
			   }
		       };
		       $("#controls").remove();
		       try
		       {
			   self.s_index = 0;
			   self.add_checker = 0;
			   self.data_add = [];
			   self.data = [];
			   self.columns = [];
			   self.columns_add = [];
			   
			   if($("#div_table").length){
			       $("#div_table").tabulator("destroy");
			   };
			   if($("#div_table_add").length){
			       $("#div_table_add").tabulator("destroy");
			   };
			   
		       }
		       catch(e)
		       {
			   console.log("tables div_table div_table_add not exist");
		       }
		       
		   };

		   this._fill_scene_table = function(){
		       var str = ('<div id="div_table" style="height: 300px; overflow: auto; border-width: 3px"></div>'
				  + '<div id="controls">'
				  + '<input id="add" type="button" value="Добавить">'
				  + '<input id="delete" type="button" value="Удалить">'
				  + '<input id="save" type="button" value="Сохранить">'
				  + '</div>'
				  + '<div id="div_table_add"></div>'
				  + '<div id="div_table_log"></div>');

		       if(self.table_name == "dialect"){
			   str += (('<div id="replacer_info">'
				    + '<p>replacer editor:</p>'
				    + '<div id="replacer_terms"></div>'
				    + '<input id="code_button" type="button" value="set" class="ui-button"><br>'
				    + '</div>')
				   + '<div id="replacer" class="style_replacer_static">'
				   + '<ul>'
				   + '<li><a href="#tif-0"> cpp </a></li>'
				   + '</ul>'
				   + '<div id="tif-0" style="background: #CCCCCC;">'
				   + '<textarea id="code" name="code" class="frame_codemirror"></textarea>'
				   + '</div>'
				   
				   + '</div>');
		       };
		       $("#div_scene").html(str);
		       $("#replacer").tabs();
		   };
		   
		   
		   this._fill_scene_components = function(){
		   
		       // FOR add button:
		       $("#add").on("click", function(){
			   if(self.add_checker == 0)
			   {
			       // create new changeable table.
			       
			       /*
				 var data_add = [{id:"3", name:"enter name"}];
				 var columns_add = [
				 {title:"id", field: "id", editor:true},
				 {title:"name", field: "name", editor:true},
				 ];
			       */
			       // for prevent clearing arrays when destroy tabular:
			       var data_add_local = self.data_add.slice();
			       var columns_add_local = self.columns_add.slice();
			       console.log("data_add"+JSON.stringify(data_add_local));
			       console.log("columns_add"+JSON.stringify(columns_add_local));
			       
			       // FOR adding table for add data:
			       $("#div_table_add").tabulator({
				   tooltips:true,
				   data: data_add_local,
				   columns: columns_add_local,
			       });
			       
			       // select first row:
			       // $("#div_table_add").tabulator("selectRow", 1);
			       // END FOR
			       
			       self.add_checker = 1;
			   }
			   else
			   {
			       // add data to main table from changeable table.
			       // after second click at add button
			       
			       // var selectedData = $("#div_table_add").tabulator("getSelectedData");
			       
			       // get new data:
			       var data_to_add = $("#div_table_add").tabulator("getData");
			       console.log("data_to_add ");
			       console.log(data_to_add);
			       
			       ////// FOR check if element exist in old data:
			       var data_old = $("#div_table").tabulator("getData");
			       
			       _exist = false;
			       $.each(data_old, function(id_old, entry_old){
				   
				   if(entry_old[self.table_index] == data_to_add[0][self.table_index]){
				       _exist = true;
				       
				       // break
				       return false;
				   }
			       });
			       ////// END FOR
			       
			       if(_exist)
			       {
				   // write log:
				   console.log("alredy exist");
				   $("#div_table_log").text("значение поля "
							    + self.table_index
							    + " не уникально");
				   $("#div_table_log").show();
			       }
			       else
			       {
				   // hide log:
				   $("#div_table_log").hide();
				   
				   // add to table:
				   $("#div_table").tabulator("addRow", data_to_add[0]);
				   
				   // add to storage for saving:
				   self.data_add_storage.push(data_to_add[0]);
				   console.log("data_add_storage:")
				   console.log(JSON.stringify(self.data_add_storage))
				   
				   // remove table_add:
				   $("#div_table_add").tabulator("destroy");
				   self.add_checker = 0;
				   
				   console.log("data_add_storage:")
				   console.log("(after div_table_add destroy)")
				   console.log(JSON.stringify(self.data_add_storage))
			       }
			   }
			   console.log("add_checker " + self.add_checker);
		       });
		       // END FOR
		       
		       // FOR delete
		       $("#delete").on("click", function(){
			   
			   //get array of currently selected data
			   var selectedData = $("#div_table").tabulator("getSelectedData"); 
			   console.log("selected data " + Object.keys(selectedData[0]));
			   
			   var selectedRows = $("#div_table").tabulator("getSelectedRows"); 
			   console.log("selectedRows.row.getIndex() selectedRows.row.table.options.index");
			   console.log(selectedRows);
			   
			   // copy data to sorage
			   self.data_delete_storage = self.data_delete_storage.concat(selectedData.slice());
			   
			   self.row_data_delete = self.row_data;
			   // delete from table:
			   $("#div_table").tabulator("deleteRow", self.s_index);
		       });
		       // END FOR
		       
		       // FOR save
		       $("#save").on("click", function(){
			   
			   // FOR update:
			   succ = function (jsonResponse) {
			       
			       // rewrite data from server
			       // clear self.data_add_storage
			       
			       var objresponse = JSON.parse(jsonResponse);
			       data = objresponse['table'];
			       console.log("\ndata");
			       console.log(data);
			       
			       // copy data:
			       var data_local = data.slice();
			       
			       // update table from response:
			       $("#div_table").tabulator("setData", data_local);
			       
			       // clear data_add_storage:
			       self.data_add_storage = [];
			   }
			   action = "update";
			   if(self.data_add_storage.length > 0){
			       self.send_data_to_server(self.data_add_storage, succ, action);
			   }else{
			       var table_data = $("#div_table").tabulator("getData");
			       self.send_data_to_server(table_data, succ, action);
			   }
			   // END FOR
			   
			   // FOR delete
			   succ = function (jsonResponse) {
			       
			       // rewrite data from server
			       // clear data_delete_storage
			       
			       var objresponse = JSON.parse(jsonResponse);
			       data = objresponse['table'];
			       console.log("\ndata");
			       console.log(data);
			       
			       // copy data:
			       var data_local = data.slice();
			       
			       // update table from response:
			       $("#div_table").tabulator("setData", data_local);
			       
			       // clear data_delete_storage:
			       self.data_delete_storage = [];
			   }
			   action = "delete";
			   if(self.data_delete_storage.length > 0){
			       self.send_data_to_server(self.data_delete_storage, succ, action);

			       // self.row_data_delete was chosen
			       // at delete button click
			       // as self.row_data = self.row_data_delete:
			       var row_data = self.row_data_delete;
			       var term_name = row_data.term_name;
			       var brackets = row_data.grammar_type;
			       // console.log(term_name);
 			       
			       // FOR remove term's replacer:
			       var to_send = JSON.stringify({
				   action: "remove",
				   dialect_name: "cpp",
				   term_name: term_name,
				   brackets: brackets,
			       });
			       console.log("\n sending (from delete (save button))");
			       console.log(to_send);
			       
			       // remove term replacer data from server:
			       $.ajax(
				   {
				       url: 'api/tables/replacer',
				       method: 'POST',
				       data: to_send,
				       
				       success: function (jsonResponse) {
					   console.log("from remove replacer success:");
							   
					   var objresponse = JSON.parse(jsonResponse);
					   data = objresponse
					   console.log(data["source"]);
							   
					   // set value
					   self.editor.setOption("value", data["source"]);
					   console.log(data);

					   console.log("available_terms:");
					   console.log(data["available_terms"]);
					   $("#replacer_terms").text(data["available_terms"]);
				       },
				       
				       error: function () {
					   //$("#responsefield").text("Error to load api");
					   console.log("Error to load api");							   				
					   // set value
					   self.editor.setOption("value",
								 "# error while removing term "+term_name);
					   
				       }
				   }
			       );
			       // END FOR
			   }
			   // END FOR
			   // console.log("\ndata ");
			   // console.log(self.data);
		       });
		   };
		   
		   
		   this.send_data_to_server = function(data, succ, action){
		       
		       // - ``data`` -- dict with data to be send
		       // - ``succ`` -- function, describing what to
		       // do after success.
		       
		       var data_to_send = data;
		       
    		       console.log("\ndata_to_send");
		       console.log(data_to_send);
		       
		       console.log("\n data_to_send.length");
		       console.log(data_to_send.length);
		       
		       // FOR sending data to server:
		       if(data_to_send.length){
			   var to_send = JSON.stringify({table_name: self.table_name,
							 action: action,
							 table: data_to_send});
			   console.log("\n sending");
			   
			   console.log(to_send);
			   
			   $.ajax(
			       {
				   url: 'api/tables/'+self.table_name,
				   type: 'POST',
				   data: to_send,
				   
				   success: succ,
				   
				   error: function () {
				       console.log("error to send");
				   }
			       });
		       }
		       else
			   console.log("\n nothing to send");
		       // END FOR
		       
		   };
		   
		   
		   this.make_table = function(){
		       console.log("self.table_name");
		       console.log(self.table_name);
		       
		       $.ajax(
			   {
			       url: 'api/tables/'+self.table_name,
			       method: 'GET',
			       
			       success: function (jsonResponse) {
				   console.log("self:");
				   console.log(self);
				   
				   self._fill_scene_table();
				   
				   var objresponse = JSON.parse(jsonResponse);
				   console.log(objresponse['table']);
				   
				   data = objresponse['table'];
				   
				   // FOR add columns and data dicts:
				   /* 
				   // columns example:
				   var columns = [
				   {title:"username", field: "username"},
				   {title:"memoryused", field: "memoryused"},
				   {title:"memorylimit", field: "memorylimit"},
				   {title:"tsused", field: "tsused"},
				   {title:"tslimit", field: "tslimit"},
				   {title:"expirydate", field: "expirydate"}		
				   ];
				   */
				   
				   var entry_data_add = {};
				   console.log("FROM ajax.get:");
				   console.log("data[0] ");
				   console.log(data[0]);
				   $.each(data[0], function(index, value){
				       // make collumns for both tables:
				       
				       var entry = {};
				       var entry_columns_add = {};
				       
				       console.log(index);
				       entry.title = index;
				       entry.field = index;

				       // don't make id editable:
				       if (index == "id"){
					   entry.editor = false;
				       }else{
					   entry.editor = true;
				       }				       
				       
				       entry_columns_add.title = index;
				       entry_columns_add.field = index;
				       
				       // make entry editable (inluding id):
				       entry_columns_add.editor = true;

				       entry_data_add[index] = value;
				       // make entry editable:
				       // entry.editor = true;
				       // console.log("entry " + Object.keys(entry));
				       
				       self.columns.push(entry);
				       self.columns_add.push(entry_columns_add);
				       
				   });
				   
				   self.data_add.push(entry_data_add);
				   console.log("columns");
				   console.log(self.columns);
				   console.log("columns_add");
				   console.log(self.columns_add);
				   console.log("data_add");
				   console.log(self.data_add);
				   // END FOR
				   
				   
				   // FOR fill table:
				   // copy data to prevent deleting:
				   var data_local = data.slice();
				   var columns_local = self.columns.slice();
				   $("#div_table").tabulator(
				       {
					   tooltips:true,
					   data: data_local,
					   columns: columns_local,
					   index: self.table_index,
					   rowClick:function(e, row){
					       self.s_index = row.getIndex();
					       console.log("from rowClick:");
					       console.log("Row " + self.s_index + " Clicked!!!!")
					       // console.log(row);
					       var row_data = row.getData();
					       console.log(row_data);
					       var term_name = row_data.term_name;
					       var brackets = row_data.grammar_type;
					       console.log(term_name);
 					       
					       // deselect all rows:
					       $("#div_table").tabulator("deselectRow");
			
					       // select selected row:
					       // $("#div_table").tabulator("selectRow", self.s_index);
					       row.select();
					       // row.deselect();
					       
					       // FOR load dialect:
					       var to_send = JSON.stringify({
						   action: "load",
						   dialect_name: "cpp",
						   term_name: term_name,
						   brackets: brackets,
					       });
					       console.log("\n sending (from rowClick)");
					       console.log(to_send);
					       
					       
					       // save for father use in set:
					       self.row_data = row_data;

					       // get replacer data from server:
					       $.ajax(
						   {
						       url: 'api/tables/replacer',
						       method: 'POST',
						       data: to_send,

						       success: function (jsonResponse) {
							   console.log("from replacer get success:");
							   
							   var objresponse = JSON.parse(jsonResponse);
							   data = objresponse
							   // console.log(data["source"]);
							   
							   // set value
							   self.editor.setOption("value", data["source"]);
							   // console.log(data);
							   console.log("available_terms:");
							   console.log(data["available_terms"]);
							   $("#replacer_terms").text(data["available_terms"]);
						       },
						       
						       error: function () {
							   //$("#responsefield").text("Error to load api");
							   console.log("Error to load api");							   				
							   // set value
							   self.editor.setOption("value",
										 "# no such term "+term_name);

						       }
						   }
					       );
					       // END FOR
					   },	
				       });
				   // END FOR
				   
				   // fill scene component:
				   self._fill_scene_components();

				   if(self.table_name == "dialect"){
				       
				       CodeMirror.commands.save = function() {
					   
					   var elt = editor.getWrapperElement();
					   elt.style.background = "#def";
					   setTimeout(function() { elt.style.background = ""; }, 300);
					   console.log("saved");
					   console.log(elt);
				       };
				       
				   
				       var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
					   lineNumbers: true,
					   mode: {name: "python",
						  version: 3,
						  singleLineStringErrors: false},
					   matchBrackets: true,
					   keyMap: "emacs"
				       });
				       self.editor = editor

				       $("#code_button").on("click", function(event){

					   if (self.row_data !== "none"){
					       console.log("from code_button.click:");

					       // FOR get value:
					       self.editor.save();
					       console.log(self.editor.getTextArea().value);  
					       var code = self.editor.getTextArea().value;
					       // var code = self.editor.getOption("value");
					       
					       // console.log(code);
					       // END FOR

					       // console.log("from code_button.click: code.text1");
					       // console.log($("#code").text());
					       // console.log(document.getElementById("code").value);
					   
					       var term_name = self.row_data.term_name;
					       var brackets = self.row_data.grammar_type;
					       
					       var to_send = JSON.stringify({
						   action: "set",
						   dialect_name: "cpp",
						   brackets: brackets,
						   term_name: term_name,
						   code: code
					       });
					       console.log("\n sending (from code_button)");
					       console.log(to_send);
					       			   
					       // set replacer data from server:
					       $.ajax(
						   {
						       url: 'api/tables/replacer',
						       method: 'POST',
						       data: to_send,

						       success: function (jsonResponse) {
							   console.log("from replacer set");
							   
							   var objresponse = JSON.parse(jsonResponse);
							   data = objresponse
							   // console.log(data["source"]);
							   
							   // set value
							   self.editor.setOption("value", data["source"]);
							   // console.log(data);
							   console.log("available_terms:");
							   console.log(data["available_terms"]);
							   $("#replacer_terms").text(data["available_terms"]);
						       },
						       
						       error: function () {
							   //$("#responsefield").text("Error to load api");
							   console.log("Error to load api");							   				
							   // set value
							   self.editor.setOption("value",
										 "# no such term "+term_name);

						       }
						   }
					       );
					       // END FOR
					       
					       }else{
						   console.log("self.row_data is none");
					       }
				       });
				       
				       // set value
				       self.editor.setOption("value", "# click at row to see replacer source\n");
				      				       
				       // console.log("code.text");
				       // console.log($("#code").text());
				   };
				   
				   // self.make_table(data, columns, data_add, columns_add);
				   console.log("ttables.js success");
			       },
			       error: function () {
				   //$("#responsefield").text("Error to load api");
				   console.log("Error to load api");
				   
			       }
			   });
		   };
		   
	       }
	   }
	   
       });
    
/*
  
// usage:
$('#button_table').on('click', function(event){

    words_table = new Table();
    console.log("words_table");
    console.log(words_table);

    if(words_table.scene_checker == 0){
	
	words_table.make_table();
	words_table.scene_checker = 1;
    }
    else
    {
	clear_scene();
	words_table.scene_checker = 0;
    }	
});
*/
