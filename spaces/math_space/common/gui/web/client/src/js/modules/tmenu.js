console.log("log tmenu.js");

define(['jquery', 'jquery-ui-custom/jquery-ui', 'modules/tooltip'],
       
       function($, ui, tooltip){

	   return {
	       Menu: function Menu(items, tooltips){
		   
		   /* Manipulation with menu.
		      
		      -- items - list of items for menu
		      TODO: make subitems sublis

		      -- tooltips - list of tooltips for each
		      menu items. It's length must be equal length
		      of items.
		    */

		   // FOR global variables:
		   var self = this;
		   
		   // FOR menu
		   self.menu_items = items;
		   self.menu_tooltips = tooltips;

		   // self.menu_items = ["add term to db", ""];
		   
		   tooltip.init();
		   
		   self.menu_hide = function(){
		       $("#menu").hide();
		   };

		   self.menu_show = function(event_position){
		       
		       // not used, depricated

		       //$("#menu").menu("option", "position",
		       //		{my: "left top", at: "left top",
		       //		 of: event_position});
		       var x = event_position.position["x"];
		       var y = event_position.position["y"];
		       console.log("position:");
		       console.log([x, y]);
		       
		       $("#menu").offset({top: y,
					  left: x})
		       console.log("menu offset:");
		       console.log($("#menu").offset());
		       
		       // $("#menu").offset({top: clientY, left: clientX})
		       
		       $("#menu").show();
		       console.log("menu offset:");
		       console.log($("#menu").offset());
		       
		   };

		   self.menu_remove = function(){
		       $("#menu").remove();
		   };
	       
		   self.menu_create = function(x, y){
		       
		       // FOR create menu region:
		       var str = ('<ul id="menu" class="ui-menu ui-widget ui-widget-content">'
				  +'</ul>');
		       $("#menu_div").html(str);
		       
		       // var x = event_position.position["x"];
		       // var y = event_position.position["y"];
		       console.log("event position:");
		       console.log([x, y]);
		 		       
		       $("#menu").menu();
		       $("#menu").offset({top: y+10, left: x+30});
		       //$("#menu").offset({top: y, left: x});
		       //$("#menu").menu("option", "position",
		       //		{x: x, y: y});

		       //$("#menu").menu({position: {of: event_position}});
		       // $("#menu").menu({position: {my: "left top", at: "left top", of: event_position}});
		       console.log("offset:");
		       console.log($("#menu").offset());
		       // END FOR
		       
		       // FOR add new items:
		       list_to_add = self.menu_items;
		       list_to_add_tooltips = self.menu_tooltips;
		       var html_list_to_add = $.map(list_to_add, function(elm, id){
			   return('<li class="ui-menu-item ui-widget ui-widget-content"'
				  + ' title="' + list_to_add_tooltips[id] + '">'+elm+'</li>');
		       });
		       $("#menu").append(html_list_to_add.join(""));
		       // END FOR
		       
		       // FOR define menu events handlers:
		       $("#menu").on("menufocus", function(event, ui){
			   $.each(ui, function(id, elm){
			       console.log("elm[0]");
			       console.log($(elm).style);
			       console.log(elm[0].style);
			       $(elm).addClass("ui-state-focus ui-state-active");
			       //$(elm).css("background-color", "blue");
			       // $(elm[0]).css("color", "blue");
			       //elm[0].setAttribute("style", "color: blue");
			       //elm[0].style.color = "blue";
			   });
			   console.log(ui);
		       });
		       $("#menu").on( "menublur", function( event, ui ) {
			   $.each(ui, function(id, elm){
			       console.log("elm[0]");
			       console.log($(elm).style);
			       console.log(elm[0].style);
			       $(elm).removeClass("ui-state-focus ui-state-active");
			       //$(elm).css("background-color", "blue");
			       // $(elm[0]).css("color", "blue");
			       //elm[0].setAttribute("style", "color: blue");
			       //elm[0].style.color = "blue";
			   });
		       });
		       $("#menu").on("menuselect", function(event, ui){
			   console.log("select");
		       });
		       // END FOR
		       // $("#menu").offset({top: 300, left: 300});
		   };
		   
		   /*
		     $("#create_menu").on("click", function(event){
		     $("#menu").menu();
		     });
		   */
		   // END FOR
	       }
	   }
       });
