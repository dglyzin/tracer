Overview 2d
===========

Blocks space (global grid):
---------------------------

Each `2d` block is rectangle area in which pde is solved with use of
finite difference method. Each block can contain equation regions,
it sides (edges) must have bounds or interconnect regions.

For blocks space two parameters is imported: ``offset`` and ``size``:

::

    "Offset": {
       "x": 0.0, 
       "y": 0.0
     }, 
    "Size": {
       "x": 1.0, 
       "y": 0.5
    }

- ``Offset`` -- represent coordinate shift in some sort of abstract
global grid.

- ``Size`` -- is size of rectangle which will be created in
``(offset x, offset y)`` point of global grid.

For example:

   +-------------------------------------------------------+
   | .. image:: _static/overview_2d_pic_1_two_blocks_ex.jpg|
   +=======================================================+
   | Pic. 1 Space with two blocks                          |
   +-------------------------------------------------------+

It worth to say this blocks (i.e. without interconnects) will represent some
solutions (process, spreaded in time; simulation) as in this pict's (so they all
same):


   +-----------------------------------------------------------------------+
   | .. image:: _static/overview_2d_pic_2.jpg                              |
   +=======================================================================+
   | Pic. 2 All this spaces with two blocks are equal (interpeted as equal)|
   +-----------------------------------------------------------------------+

Interconnects:
^^^^^^^^^^^^^^

To connect two block together interconnect used:

::

   "Block1": 0, 
   "Block2": 1, 
   "Block1Side": 3, 
   "Block2Side": 2

Also block ``offset`` param will be used for generators (ics) and
array fillers (ics) to extract exact area in which intectonnect will
be used.

For example:

   +-----------------------------------------------+
   | .. image:: _static/overview_2d_pic_3_ic_ex.jpg|
   +===============================================+
   | Pic. 3 Space with two connected blocks        |
   +-----------------------------------------------+


It worth to say this blocks  will represent some solutions (process,
 spreaded in time; simulation) as in this pict's (so they all same):

   +-----------------------------------------------------------------------+
   | .. image:: _static/overview_2d_pic_4.jpg                              |
   +=======================================================================+
   | Pic. 4 All this spaces with two blocks are equal (interpeted as equal)|
   +-----------------------------------------------------------------------+


So model can represent not only euclidian infinity flat space but also
finit flat space (as torus):

   +-----------------------------------------------+
   | .. image:: _static/overview_2d_pic_5_torus.jpg|
   +===============================================+
   | Pic. 5 Space for torus                        |
   +-----------------------------------------------+
 
