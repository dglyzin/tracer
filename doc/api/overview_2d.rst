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

In order to explain how ``ics`` is interpretatid in ``hs``
looks at examples:

Say One have two blocks with ics:

    "Interconnects": [
	{
            "Name": "connection 1", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 2, 
            "Block2Side": 3
        },


   +---------------------------------------------------------------------+
   | .. image:: _static/overview_2d_pic_3.1.jpg                              |
   +=======================================================================+
   | Pic. 3.1 Two connected blocks              |
   +-----------------------------------------------------------------------+

in dom file they will be converted in

   icDim  icLen  source block  dist_block  source side  dist side  \
0      1     64             0           1            2          3   
1      1     64             1           0            3          2   


   source offset  dist offset  
0             37            0  
1              0           37  


Then ic array list (that whose entrys .cpp ic funcions will be used in)
will be created:

in block 1: ic = [2,] sides of block 0
in block 0: ic = [3,] sides of block 1

For example

in Block0Interconnect__Side2_Eqn2 from .cpp file
ic[0] will be used.

in Block1Interconnect__Side2_Eqn2 from .cpp file
ic[0] will be used.


If there is more ics with other block (it is important)
then arrays will be increasing accordingly:

for example

	{
            "Name": "connection 1", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 2, 
            "Block2Side": 3
        },
	{
            "Name": "connection 1", 
            "Block1": 1, 
            "Block2": 0, 
            "Block1Side": 2, 
            "Block2Side": 3
        }

   icDim  icLen  source block  dist_block  source side  dist side  \
0      1     64             0           1            2          3   
1      1     64             1           0            3          2   
2      1     64             1           0            2          3   
3      1     64             0           1            3          2   

   source offset  dist offset  
0             37            0  
1              0           37  
2              0           37  
3             37            0  

Then ic array list (that whose entrys .cpp ic funcions will be used in)
will be created:

in block 1: ic = [2, 3] sides of block 0
in block 0: ic = [3, 2] sides of block 1

For example

in Block0Interconnect__Side2_Eqn2 from .cpp file
ic[0] will be used.

in Block0Interconnect__Side3_Eqn2 from .cpp file
ic[1] will be used.

in Block1Interconnect__Side2_Eqn2 from .cpp file
ic[0] will be used.

in Block1Interconnect__Side3_Eqn2 from .cpp file
ic[1] will be used.
(see problems/2dTests/heat_block_0_ics_other)

When there is only one block and ic looks like:

	{
            "Name": "connection 1", 
            "Block1": 0, 
            "Block2": 0, 
            "Block1Side": 2, 
            "Block2Side": 3
        }

   icDim  icLen  source block  dist_block  source side  dist side  \
0      1    101             0           0            2          3   
1      1    101             0           0            3          2   

   source offset  dist offset  
0              0            0  
1              0            0  

in block 0: ic = [2, 3] sides of block 0

For example

in Block0Interconnect__Side2_Eqn0 from .cpp file
ic[1] will be used.

in Block0Interconnect__Side3_Eqn0 from .cpp file
ic[0] will be used.
(see problems/2dTests/heat_block_0_ics_self)

For that unreflectness of ic array (compare with ics for differ blocks)
is due dist_block now is equal to src_block
an he copy sides direcly to same block (according ics table above)
i.e.  externalBorder in hs for single block ics is
interpreted as sourceBorder for same block.
For this reason situation with many ics (both with self and other block)
is complicated. For example:

	{
            "Name": "connection other", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 0, 
            "Block2Side": 1
        },
	{
            "Name": "connection self", 
            "Block1": 0, 
            "Block2": 0, 
            "Block1Side": 2, 
            "Block2Side": 3
        },
	{
            "Name": "connection 1", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 1, 
            "Block2Side": 0
        }

   icDim  icLen  source block  dist_block  source side  dist side  \
0      1     51             0           1            0          1   
1      1     51             1           0            1          0   
2      1    101             0           0            2          3   
3      1    101             0           0            3          2   
4      1     51             0           1            1          0   
5      1     51             1           0            0          1   

   source offset  dist offset  
0             15            0  
1              0           15  
2              0            0  
3              0            0  
4             15            0  
5              0           15  

in block 1: ic = [0, 1] sides of block 0
in block 0: ic = [1, 2, 3, 0] sides of [block 1, block 0, block 0, block 1]


For example:

Block0Interconnect__Side0_Eqn0 from .cpp file
ic[0] will be used.
Block0Interconnect__Side1_Eqn0 from .cpp file
ic[3] will be used.
Block0Interconnect__Side2_Eqn0 from .cpp file
ic[2] will be used.
Block0Interconnect__Side3_Eqn0 from .cpp file
ic[1] will be used.

Block1Interconnect__Side0_Eqn0 from .cpp file
ic[1] will be used.
Block1Interconnect__Side1_Eqn0 from .cpp file
ic[0] will be used.

see problems/2dTests/heat_block_0_ics_self_other


If order of ics was chenged in .json
then order of ic in entrys table will be changed to:
For example for order:

 	{
            "Name": "connection other", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 0, 
            "Block2Side": 1
        },
	{
            "Name": "connection 1", 
            "Block1": 0, 
            "Block2": 1, 
            "Block1Side": 1, 
            "Block2Side": 0
        },
	{
            "Name": "connection self", 
            "Block1": 0, 
            "Block2": 0, 
            "Block1Side": 2, 
            "Block2Side": 3
        }

entry table will looks like:
   icDim  icLen  source block  dist_block  source side  dist side  \
0      1     51             0           1            0          1   
1      1     51             1           0            1          0   
2      1     51             0           1            1          0   
3      1     51             1           0            0          1   
4      1    101             0           0            2          3   
5      1    101             0           0            3          2   

   source offset  dist offset  
0             15            0  
1              0           15  
2             15            0  
3              0           15  
4              0            0  
5              0            0  

and ics array in .cpp will looks like:
in block 1: ic = [0, 1] sides of block 0
in block 0: ic = [1, 0, 2, 3] sides of [block 1, block 1, block 0, block 0]


what will cause ic function in .cpp change they icIdx too: 

Block0Interconnect__Side0_Eqn0 from .cpp file
ic[0] will be used.
Block0Interconnect__Side1_Eqn0 from .cpp file
ic[1] will be used.
Block0Interconnect__Side2_Eqn0 from .cpp file
ic[3] will be used.
Block0Interconnect__Side3_Eqn0 from .cpp file
ic[2] will be used.

Block1Interconnect__Side0_Eqn0 from .cpp file
ic[1] will be used.
Block1Interconnect__Side1_Eqn0 from .cpp file
ic[0] will be used.

see problems/2dTests/heat_block_0_ics_self_other_order


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
 
