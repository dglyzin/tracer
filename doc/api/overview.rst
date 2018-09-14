Overview
========

Can currently solve pde equations like:

.. math::  U' = \sum_{i} a_{i} U(t-\delta_{i}) + \sum_{j} b_{j} \frac{d U(t-\delta_{j})}{d x} \
	+ \sum_{k} c_{k} \frac{d^{2} U(t-\delta_{k})}{d x^{2}}


where 

.. math:: \delta_{s} \geqslant 0  


Flow:
-----

1. User create model (using oop or from json).
2. Model transformed for appropriate solver
   (i.e. source files generated in ``problems/problem_name/out`` folder) \
   Equation converted to cpp 
   Environment converted to arrays in .dom file

3. Run solver
4. Postproc transform result to ``.mp3/arrays`` (also in out folder).

`Step 1` in ``envs``, `Step 2` in ``gens``, `Step 3,4` in ``solver`` folders.



See schemes below.

   +---------------------------------------+
   | .. image:: _static/overview_struct.jpg|
   +=======================================+
   | Pic. 1 Structure                      |
   +---------------------------------------+

   +-------------------------------------+
   | .. image:: _static/overview_func.jpg|
   +=====================================+
   | Pic. 2 Function                     |
   +-------------------------------------+

::

Run:
----

To run problem remotely::

`python3 -m solvers.hs.remoterun.remoterun conn_base default problems/1dTests/logistic_delays`

where
   - ``conn_base`` - is default name for connection file in `settings/conn/`
   - ``default`` - is default name for device settings file in `settings/device_conf`
   - ``problems/1dTests/logistic_delays`` - name of problems

To just generate src files run (from hd)::

`python3 -m gens.hs.tests.tests_gen_1d -t test_name -d device_name`

where 
   - ``test_name`` - is name of folder with json in `problems/1dTests`\
   without extention. Default is `Brusselator1d`

   - ``device_name`` - is name of device conf json file in `settings/device_conf`\
   without extention. Default is `default`
   
