Overview json plot and result settings
======================================

Plot settings
-------------
::
 (Important note: Count of ``Results`` and ``Plots`` in ``model.json`` file must be equal or less then count of blocks, Count of values in ``Value`` list in ``Plots/Results`` entries must be equal or less then count of equations in system)

Represented in ``.json`` files in ``Plots`` directive::

  "Plots": 
  [{
   "Name": "plot0",
   "Title": "block0 u(t,x)", 
   "Period": 0.001,
   "Value": ["U"]
   },
   {
    "Name": "plot1",
    "Title": "block1 u(t,x)", 
    "Period": 0.001,
    "Value": ["U"]
   }]

each entry in ``Plots`` list correspond to block in model.
``Value`` is list of variable's, each represented with equation in ``System`` directive. 
For each block video file will be generated ("Name" + with according index to it's name),
that contain, for each variable from ``Value`` list, variable results evolution at separate layers.
(See Pic. 1):

   +----------------------------------------------------------+
   | .. image:: _static/overview_plot_pic_1_plots_block_ex.png|
   +==========================================================+
   | Pic. 1 Plots file for block 0 of Brusselator1d.json test |
   +----------------------------------------------------------+

Results settings
----------------

Represented in ``.json`` files in ``Results`` directive::

  "Results":
  [{
    "Name": "block0", 
    "Period": 0.001,
    "Value": ["U", "V"]
   },
   {
    "Name": "block1", 
    "Period": 0.001,
    "Value": ["U", "V"]
   },
   {
    "Name": "block2", 
    "Period": 0.001,
    "Value": ["U", "V"]
   },
   {
    "Name": "block3", 
    "Period": 0.001,
    "Value": ["U", "V"]
   }]

Like in ``Plots``, each entry in ``Results`` list correspond to block in model.
``Value`` is list of variable's, each represented with equation in ``System`` directive. 
For each block and each variable (from ``Value`` list) result file will be generated
(ex(#TODO: file name updated description needed!): like "Brusselator1d-res0-U.out" for ``block0`` var ``U``),
that is array with [time, data] like::

  0.00000000: [0.     0.01   0.02 ...,   9.98   9.99  10.]
  0.00100000: [0.01643526 0.01849364  0.02411744 ...,  9.38551519  7.73367371 5.33818054]
  0.00200000: [0.02416995 0.02559824  0.02969959 ...,  8.78058045  7.22605051 5.48017457]

