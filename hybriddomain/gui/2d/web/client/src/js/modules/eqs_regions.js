console.log("log eqs_regions.js");
define(['jquery', 'fabric'],
       
       function($, fabric){
	   
	   var create_regions_cls = function(net){

	       /*Function used for region's inheritance.
		
		For Rect and Circle obj(options) is used for initialization,
		for Text obj(text, options).

		Overrided options will be: ``equation_number``
		and ``observable``. They will be extracted to
		json (with ``toObject`` method) for server.

		*/

	       
	       // FOR equations regions:
	       var EquationRegionRect = fabric.util.createClass(fabric.Rect, {
		   type: "ERegionRect",
	       
		   // this function is same for Rect and Circle,
		   // but will be differed for Text.
		   initialize: function(options) {
		       options || (options = { });
		       
		       this.callSuper('initialize', options);
		       // console.log("options:");
		       // console.log(options);
		       
		       this.set('equation_number', options.equation_number || '');
		       this.set('observable', options.observable || false);
		   },
		   
		   toObject: function() {
		       return fabric.util.object.extend(this.callSuper('toObject'), {
			   equation_number: this.get('equation_number'),
			   observable: this.get('observable')
		       });
		      
		   },
		   /*
		   fromObject: function(options) {
		       return new fabric.ERegion(options);
		   }
		    */
	       });
	       fabric.ERegionRect = EquationRegionRect;
	
	       /*
	       fabric.ERegionRect.fromObject = function(object, callback) {
		   // console.log("object = ", object);
		   // console.log("object.objects = ", object.objects);
		   var _enlivenedObjects;
		   
		   
		   fabric.util.enlivenObjects(object.objects, function (enlivenedObjects) {
		       console.log("fromObject.enlivenObject:object");
		       console.log(object);
		       console.log("fromObject.enlivenObject:enlivenedObjects");
		       console.log(enlivenedObjects);
		       delete object.objects;
		       _enlivenedObjects = enlivenedObjects;
		   });
		   console.log("fromObject:_enlivenedObjects");
		   console.log(_enlivenedObjects);
		   return new fabric.ERegionRect(_enlivenedObjects, object);
	       };
	       */
	       
	       
	       fabric.ERegionRect.fromObject = function(object, callback) {
		   // console.log("fromObject.object");
		   // console.log(object);
		   return new fabric.Object._fromObject('ERegionRect', object, callback);
		   // return new fabric.ERegionRect(object);
	       };
	       
	       /*
	       // test0:
	       var test0 = '{"objects":[{"type":"path","version":"3.1.0","originX":"left","originY":"top","left":56.81,"top":23.82,"width":170.4,"height":70.54,"fill":null,"stroke":"rgba(255,255,255,1.0)","strokeWidth":10,"strokeDashArray":null,"strokeLineCap":"round","strokeDashOffset":0,"strokeLineJoin":"round","strokeMiterLimit":10,"scaleX":1,"scaleY":1,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"path":[["M",26.892173913043475,91.4007284768212],["Q",26.902173913043477,91.3907284768212,26.902173913043477,90.89403973509934],["Q",26.902173913043477,90.39735099337749,27.40036231884058,89.40397350993378],["Q",27.89855072463768,88.41059602649007,27.89855072463768,87.41721854304636],["Q",27.89855072463768,86.42384105960265,27.89855072463768,83.94039735099338],["Q",27.89855072463768,81.45695364238411,28.894927536231883,77.98013245033113],["Q",29.891304347826086,74.50331125827815,30.88768115942029,70.03311258278146],["Q",31.884057971014492,65.56291390728477,35.869565217391305,56.62251655629139],["Q",39.85507246376812,47.68211920529801,43.84057971014492,42.715231788079464],["Q",47.826086956521735,37.74834437086093,54.302536231884055,32.78145695364238],["Q",60.778985507246375,27.81456953642384,67.25543478260869,24.834437086092713],["Q",73.73188405797102,21.85430463576159,78.71376811594203,21.357615894039736],["Q",83.69565217391305,20.86092715231788,86.68478260869566,20.86092715231788],["Q",89.67391304347827,20.86092715231788,90.17210144927537,20.86092715231788],["Q",90.67028985507247,20.86092715231788,90.67028985507247,21.357615894039736],["Q",90.67028985507247,21.85430463576159,91.66666666666667,23.34437086092715],["Q",92.66304347826087,24.834437086092713,95.65217391304347,29.304635761589402],["Q",98.64130434782608,33.77483443708609,102.12862318840578,38.24503311258278],["Q",105.6159420289855,42.71523178807947,111.09601449275362,48.67549668874172],["Q",116.57608695652173,54.63576158940397,126.04166666666666,62.58278145695364],["Q",135.5072463768116,70.52980132450331,140.9873188405797,75],["Q",146.4673913043478,79.47019867549669,151.44927536231882,82.45033112582782],["Q",156.43115942028984,85.43046357615894,159.91847826086956,86.42384105960265],["Q",163.40579710144928,87.41721854304636,172.37318840579712,89.40397350993378],["Q",181.34057971014494,91.3907284768212,189.31159420289856,90.39735099337749],["L",197.29260869565215,89.39397350993377]]}]}';
	       */
	       // test1:
	       /*
	       var test1 = '{"objects": [{"type":"ERegionRect","version":"3.1.0","originX":"left","originY":"top","left":0.48,"top":0.19,"width":60,"height":70,"fill":"rgba(255,255,255,1.0)","stroke":null,"strokeWidth":1,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":1,"scaleY":1,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"rx":0,"ry":0,"equation_number":"2","observable":true}]}';
	       var canvas = net.canvas;
		*/
	       /*
	       var canvas = new fabric.Canvas('canvas',
					      {isDrawingMode: false});
	       
	       console.log("test0 loadFromJSON");
	       canvas.loadFromJSON(test0);
	       console.log("fabric:");
	       console.log(fabric);
	       console.log("done");*/
	       /*
	       console.log("test1 loadFromJSON");
	       canvas.loadFromJSON(test1);
	       canvas.requestRenderAll();
	       console.log("done");
	       */
	       var EquationRegionCircle = fabric.util.createClass(fabric.Circle, {
		   type: "ERegionCircle",
		   
		   // this function is same for Rect and Circle,
		   // but will be differed for Text.
		   initialize: function(options) {
		       options || (options = { });
		       
		       this.callSuper('initialize', options);
		       // console.log("options:");
		       // console.log(options);
		       
		       this.set('equation_number', options.equation_number || '');
		       this.set('observable', options.observable || false);
		   },
		   
		   toObject: function() {
		       return fabric.util.object.extend(this.callSuper('toObject'), {
			   equation_number: this.get('equation_number'),
			   observable: this.get('observable')
		       });
		   }});
	       
	       fabric.ERegionCircle = EquationRegionCircle;
	
	       /*
	       fabric.ERegion.fromObject = function(object, callback) {
		   var _enlivenedObjects;
		   fabric.util.enlivenObjects(object.objects, function (enlivenedObjects) {
		       delete object.objects;
		       _enlivenedObjects = enlivenedObjects;
		   });
		   return new fabric.ERegion(_enlivenedObjects, object);
	       };
		*/
	       
	       fabric.ERegionCircle.fromObject = function(object, callback) {
		   return new fabric.Object._fromObject('ERegionCircle', object, callback);
		   
		   // return new fabric.ERegionCircle(options);
	       };

	       var EquationRegionTextbox = fabric.util.createClass(fabric.Textbox, {
		   type: "ERegionTextbox",
		   
		   // override init for text:
		   initialize: function(text, options){
		       options || (options = { });
		       
		       this.callSuper('initialize', text, options);
		       // console.log("options:");
		       // console.log(options);
		       
		       this.set('equation_number', options.equation_number || '');
		       this.set('observable', options.observable || false);
		   },
		   
		   toObject: function() {
		       return fabric.util.object.extend(this.callSuper('toObject'), {
			   equation_number: this.get('equation_number'),
			   observable: this.get('observable')
		       });
		   }});
	       
	       fabric.ERegionTextbox = EquationRegionTextbox;
	
	       /*
	       fabric.ERegion.fromObject = function(object, callback) {
		   var _enlivenedObjects;
		   fabric.util.enlivenObjects(object.objects, function (enlivenedObjects) {
		       delete object.objects;
		       _enlivenedObjects = enlivenedObjects;
		   });
		   return new fabric.ERegion(_enlivenedObjects, object);
	       };
		*/
	       
	       fabric.ERegionTextbox.fromObject = function(object, callback) {
		   return new fabric.Object._fromObject('ERegionTextbox', object, callback, "text");
		   // return new fabric.ERegionTextbox(options);
	       };
	       // END FOR

	       // FOR bounds regions:
	        
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
	       var BoundRegion = fabric.util.createClass(fabric.ERegionRect, {
		   type: "BRegion",
	       
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

	       fabric.BRegion = BoundRegion;
	       fabric.BRegion.fromObject = function(object, callback) {
		   return new fabric.Object._fromObject('BRegion', object, callback);
		   // return new fabric.BRegion(options);
	       };
	       // END FOR
	   };

	   var choice_region = function(stype, options){
	       // var cls = create_region_cls(stype);
	       var obj = undefined;
	       
	       if(stype=="Circle")
		   obj = new fabric.ERegionCircle({radius: 20, left: 100, top: 100,
						   observable: options.observable,
						   equation_number: options.equation_number,
						   fill: options.color});
	       if(stype=="Text"){
		   obj = new fabric.ERegionTextbox('editable text', {left: 100, top: 100,
								     observable: options.observable,
								     equation_number: options.equation_number,
								     fill: options.color});
		   console.log("text options:");
		   console.log(options);
		   obj.setColor(options.color);
	       }

	       if(stype=="Rect" || !obj)
		   obj = new fabric.ERegionRect({top : 100, left : 100, width : 60, height : 70,
						 observable: options.observable,
						 equation_number: options.equation_number,
						 fill: options.color});
	       return(obj);
	   };

	   // var EquationRegion = create_region_cls("Rect");
	   
	   return {
	       create_regions_cls: create_regions_cls,
	       choice_region: choice_region
	   };
       });
