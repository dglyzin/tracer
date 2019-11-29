console.log("log tmenu.js");

define(['jquery', 'jquery-ui-custom/jquery-ui', 'tooltip'],
       
       function($, ui, tooltip){

	   function Input(net, i_id){
	       /* Dinamic text input (see desk in create_input method).
		      
		-- ``net`` - where it used.

		-- ``i_id`` - actual div id of index.htm,
		where input will be stored.
	       */
	       
	       // FOR global variables:
	       var self = this;
	       self.net = net;

	       // FOR menu
	       // inter menu id:
	       self.input_id = "#input_key";

	       // actual menu div id in index.htm:
	       self.input_div_id = i_id;

	       self.input_status = 0;
	   };

	   Input.prototype.remove_input = function(){
	       this.text_acc = undefined;
	       $(this.input_id).remove();
	   };
	
	   Input.prototype.create_input = function(x, y, succ){
	       
	       /*Create input in coords x, y.
		Whait and collect all words to self.text_acc.
		Call succ with collected words. Finely remove input.

		-- ``succ`` - is func, that will be called
		when Enter will be pressed in input. Entered
		string (from self.text_acc) will be given to it: succ(self.text_acc)*/

	       var self = this;

	       // FOR create input region:
	       var str = ('<input type="text" title="press enter" id="'+self.input_id.slice(1)+'"'
			  + ' style="position: absolute;" class="">');
	       $(self.input_div_id).html(str);
	       
	       // var x = event_position.position["x"];
	       // var y = event_position.position["y"];
	       console.log("event position:");
	       console.log(x);
	       console.log(y);
	       
	       // $(this.input_id).menu();
	       $(this.input_id).offset({top: y+10, left: x+30});
	       
	       /* When input created, it whaiting for keys,
		collect them into self.text_acc, and when
		Enter arraive, it call succ and remove item*/
	       $(this.input_id).on("keypress", function(event){
		   
		   if (!self.text_acc)
		       self.text_acc = event.originalEvent.key;
		   else
		       if(event.originalEvent.key!="Enter" && event.originalEvent.key!="Backspace")
			   self.text_acc = self.text_acc + event.originalEvent.key;
		   
		   console.log("key pressed");
		   console.log(event.originalEvent.key);
		   if(event.originalEvent.key=="Enter"){
		       console.log("input node_name:");
		       console.log(self.text_acc);
		       succ(self.text_acc);
		       self.text_acc = undefined;
		       self.remove_input();
		   }
	       });
	   };

	   return({Input: Input});
       });
