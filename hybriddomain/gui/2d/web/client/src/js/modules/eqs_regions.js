console.log("log eqs_regions.js");
define(['jquery', 'fabric'],
       
       function($, fabric){

	   var create_region_cls = function(stype){

	       /*Function used for region's inheritance.
		
		For Rect and Circle obj(options) is used for initialization,
		for Text obj(text, options).

		Overrided options will be: ``equation_number``
		and ``observable``. They will be extracted to
		json (with ``toObject`` method) for server.

		- ``stype`` -- Name of parent (Rect, Circle or Text)
		default is Rect.*/

	       var ftype=undefined;

	       // this function is same for Rect and Circle,
	       // but will be differed for Text.
	       var init = function(options) {
		   options || (options = { });
		   
		   this.callSuper('initialize', options);
		   // console.log("options:");
		   // console.log(options);

		   this.set('equation_number', options.equation_number || '');
		   this.set('observable', options.observable || false);
	       };

	       if(stype=="Rect")
		   ftype = fabric.Rect;
	       if(stype=="Circle")
		   ftype = fabric.Circle;
	       if(stype=="Text"){
		   ftype = fabric.Textbox;

		   // override init for text:
		   init = function(text, options){
		       options || (options = { });
		   
		       this.callSuper('initialize', text, options);
		       // console.log("options:");
		       // console.log(options);

		       this.set('equation_number', options.equation_number || '');
		       this.set('observable', options.observable || false);
		   };
	       }
	       if(!ftype)
		   ftype = fabric.Rect;

	       
	       var EquationRegion = fabric.util.createClass(ftype, {
		   type: "eRegion",
	       
		   initialize: init,
		   
		   toObject: function() {
		       return fabric.util.object.extend(this.callSuper('toObject'), {
			   equation_number: this.get('equation_number'),
			   observable: this.get('observable')
		       });
		   }
	       });
	       return(EquationRegion);
	   };

	   var create_region = function(stype, options){
	       var cls = create_region_cls(stype);
	       var obj = undefined;
	       
	       if(stype=="Circle")
		   obj = new cls({radius: 20, left: 100, top: 100,
				  observable: options.observable,
				  equation_number: options.equation_number,
				  fill: options.color});
	       if(stype=="Text"){
		   obj = new cls('editable text', {left: 100, top: 100,
				  observable: options.observable,
				  equation_number: options.equation_number,
				  fill: options.color});
		   console.log("text options:");
		   console.log(options);
		   obj.setColor(options.color);
	       }

	       if(stype=="Rect" || !obj)
		   obj = new cls({top : 100, left : 100, width : 60, height : 70,
				  observable: options.observable,
				  equation_number: options.equation_number,
				  fill: options.color});
	       return(obj);
	   };

	   var EquationRegion = create_region_cls("Rect");
 
	   /*
	    Inherit Rect for bounn region object.
	    Overriden options is:

	    - ``convas_width/_height`` -- used for defining bottom
	    and right coordinate for side 0 and 1.

	    - ``side`` -- used for side:
	    ***x->
	    *  
	    |  ---side 2---
	    y  |          |
	       s          s
	       i          i
	       d          d
	       e          e
	       0          1
	       |          |
	       ---side 3---

	    Movement in according axes will be restricted.
	    This object will be shown in img as 1px width (for sides 0, 1)
	    or height(for sides 2, 3).
	    */
	   var BoundRegion = fabric.util.createClass(EquationRegion, {
	       type: "bRegion",
	       
	       initialize: function(options) {
		   options || (options = { });
		   
		   this.callSuper('initialize', options);
		   
		   //create new attrs:
		   this.set('convas_width', options.convas_width);
		   this.set('convas_height', options.convas_height);
		   this.set('side', options.side);
		   
		   // restrict rotation and scaling:
		   this.set("lockRotation", true);
		   this.set("lockScalingX", true);
		   this.set("lockScalingY", true);

		   // restrict movement:
		   if (options.side == 0 || options.side == 1){
		       this.set('width', 10);
		       this.set('height', 70);
		       this.set("lockMovementX", true);
		       this.set("top", 0);
		       if(options.side == 0){
			   this.set("left", 0);
		       }else{
			   this.set("left", options.convas_width - 10);
		       }
		   };
		   if (options.side == 2 || options.side == 3){
		       this.set('width', 70);
		       this.set('height', 10);
		       this.set("lockMovementY", true);
		       
		       if(options.side == 2){
			   this.set("top", 0);
		       }else{
			   this.set("top", options.convas_height - 10);
		       }
		   };
	       },

	       _render: function(ctx) {
		   this.callSuper('_render', ctx);
		   
		   // ctx.font = '20px Helvetica';
		   // ctx.fillStyle = '#333';
		   // ctx.fillText(this.label, -this.width/2, -this.height/2 + 20);
	       },

	       toObject: function() {
		   return fabric.util.object.extend(this.callSuper('toObject'), {
		       side: this.get('side')
		   });
	       }
	   });

	   return {
	       create_region: create_region,
	       EquationRegion: EquationRegion,
	       BoundRegion: BoundRegion
	   };
       });
