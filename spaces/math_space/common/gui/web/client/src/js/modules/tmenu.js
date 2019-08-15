console.log("log tmenu.js");

define(['jquery', 'jquery-ui-custom/jquery-ui', 'modules/tooltip'],
       
       function($, ui, tooltip){

	   function Menu(m_id, items, tooltips, callbacks){
	       /* Manipulation with menu.
		      
		-- ``m_id`` - actual div id of index.htm,
		where menu will be stored.

		-- ``items`` - list of items for menu
		TODO: make subitems sublis

		-- ``tooltips`` - list of tooltips for each
		menu items. It's length must be equal length
		of items.

		-- ``callbacks`` - dict whose keys is same
		as ``items``.
	       */
	       
	       // FOR global variables:
	       var self = this;

	       // FOR menu
	       // inter menu id:
	       self.menu_id = "#menu";

	       // actual menu div id in index.htm:
	       self.menu_div_id = m_id;

	       self.menu_items = items;
	       self.menu_tooltips = tooltips;
	       self.menu_callbacks = callbacks;

	       self.menu_status = 0;
	       // self.menu_items = ["add term to db", ""];
	       
	       tooltip.init();
	       // END FOR
	   }
	   
	   Menu.prototype.update = function(x, y){
	       var self = this;

	       if(self.menu_status == 0){
		   console.log(self);
		   self.menu_create(x, y);
		   self.menu_status = 1;
	       }else if(self.menu_status == 1){
		   // menu_hide();
		   self.menu_remove();
		   self.menu_status = 2;
	       }else if(self.menu_status == 2){
		   // menu_show(event);
		   self.menu_create(x, y);
		   self.menu_status = 1;
	       };
	   };

	   Menu.prototype.update_remove = function(x, y){
	       var self = this;

	       if(self.menu_status == 1){
		   // menu_hide();
		   self.menu_remove();
		   self.menu_status = 2;
	       };
	   };

	   Menu.prototype.menu_hide = function(){
	       $(this.menu_id).hide();
	   };
	
	   Menu.prototype.menu_show = function(event_position){
		       
	       // not used, depricated

	       //$("#menu").menu("option", "position",
	       //		{my: "left top", at: "left top",
	       //		 of: event_position});
	       var x = event_position.position["x"];
	       var y = event_position.position["y"];
	       console.log("position:");
	       console.log([x, y]);
	       
	       $(this.menu_id).offset({top: y,
				  left: x})
	       console.log("menu offset:");
	       console.log($(this.menu_id).offset());
	       
	       // $("#menu").offset({top: clientY, left: clientX})
	       
	       $(this.menu_id).show();
	       console.log("menu offset:");
	       console.log($(this.menu_id).offset());
	       
	   };

	   Menu.prototype.menu_remove = function(){
	       $(this.menu_id).remove();
	   };
	
	   Menu.prototype.menu_create = function(x, y){
	       
	       var self = this;

	       // FOR create menu region:
	       var str = ('<ul id="'+self.menu_id.slice(1)+'" class="ui-menu ui-widget ui-widget-content">'
			  +'</ul>');
	       $(self.menu_div_id).html(str);
	       
	       // var x = event_position.position["x"];
	       // var y = event_position.position["y"];
	       console.log("event position:");
	       console.log([x, y]);
	       
	       $(this.menu_id).menu();
	       $(this.menu_id).offset({top: y+10, left: x+30});
	       //$("#menu").offset({top: y, left: x});
	       //$("#menu").menu("option", "position",
	       //		{x: x, y: y});

	       //$("#menu").menu({position: {of: event_position}});
	       // $("#menu").menu({position: {my: "left top", at: "left top", of: event_position}});
	       console.log("offset:");
	       console.log($(this.menu_id).offset());
	       // END FOR
	       
	       // FOR add new items:
	       var list_to_add = self.menu_items;
	       var list_to_add_tooltips = self.menu_tooltips;
	       var html_list_to_add = $.map(list_to_add, function(elm, id){
		   return('<li class="ui-menu-item ui-widget ui-widget-content"'
			  + ' title="' + list_to_add_tooltips[id] + '">'+elm+'</li>');
	       });
	       $(this.menu_id).append(html_list_to_add.join(""));
	       // END FOR
	       
	       // FOR define menu events handlers:
	       $(this.menu_id).on("menufocus", function(event, ui){
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
	       $(this.menu_id).on( "menublur", function( event, ui ) {
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
	       $(this.menu_id).on("menuselect", function(event, ui){
		   console.log("select");
		   // console.log(event);
		   console.log(ui);
		   if (self.callbacks){
		       var idx = ui.item[0].textContent;
		       console.log(ui.item[0].textContent);
		       self.callbacks[idx]();
		   }else{
		       console.log("callbacks not set");
		   };
	       });
	       // END FOR
	       // $("#menu").offset({top: 300, left: 300});
	   };

	   return {
	       Menu: Menu
	   }
       });
