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

::
 (Important note: Check ``hs_python``, ``hd_python`` prefixes in devices conf file, they must point at env, where hybriddomain module was instaled (and not forget about ``home`` -> ``clusterhome`` migration))

::
 (Important note: Count of ``Results`` and ``Plots`` in ``model.json`` file must be equal or less then count of blocks, Count of values in ``Value`` list in ``Plots/Results`` entries must be equal or less then count of equations in system)(see :doc:`json plot and result settings   <overview_plot>` for more)

To run problem remotely (from ``hybriddomain`` repository folder (where ``hybriddomain`` folder exist))
::

 hybriddomain$ ~/anaconda3/bin/./python3 -m hybriddomain.solvers.hs.remoterun.remoterun conn/conn_base.json device_conf/default.json paths/paths_hs_base.json hybriddomain/problems/1dTests/logistic_delays

where

   - ``conn/conn_base.json`` - is default name for connection file in `hybriddomain/settings` folder
   - ``device_conf/default.json`` - is default name for device settings file in `hybriddomain/settings`
   - ``paths/paths_hs_base.json`` -- is default name for paths settings file in `hybriddomain/settings`
   - ``hybriddomain/problems/1dTests/logistic_delays`` - name of problems

Test src gen for 1d:
--------------------

To just generate src files use  ``hybriddomain.gens.hs.tests.tests_gen_1d``::

 ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_1d -t problem_folder -d device_conf_rpath -p paths_rpath -w workspace_folder_location -u username

where

   - ``problem_folder`` -- project path to folder, where .json file stored
         and it can be:

      either relative to hd:

      (ex: ``hybriddomain/problems/1dTests/test_folder``)::

       python3 -m hybriddomain.gens.hs.tests.tests_gen_1d -t hybriddomain/problems/1dTests/logistic_delays

      or absolute::
      
       python3 -m hybriddomain.gens.hs.tests.tests_gen_1d -t ~/projects/lab/hybriddomain/hybriddomain/problems/1dTests/logistic_delays

      or test_folder name
          where test_folder in ``hd/problems/1dTests``::

           python3 -m gens.hs.tests.tests_gen_1d -t logistic_delays

   - ``workspace_folder_location`` -- (optional) is path to folder
      where "problems" and "settings" folder lie.
      If no given, "problems" will be used from hd/hd/problems,
      "settings" from hd/hd/settings.
      This parameter used only at server (remotely).

   - ``username`` -- used for interpetation of tilde (~) in pathes if
      connection file not used or not exist.

   - ``paths_rpath`` -- (optional) is relative to settings if running from project_folder
      (or hd/hd/settings if running from hd) path of paths file
      default is ``paths/paths_hs_base.json``

   - ``device_conf_rpath`` -- (optional) is relative to settings if running from project_folder
      (or hd/hd/settings if running from hd) path of device config file
      default is ``device_conf/default.json``

# Examples:

# for tests at client side from hd repository folder (where hd folder located) use::

   ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_1d -t logistic_delays -u username

# or with undefault settings::

   ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_1d -t logistic_delays -p paths/paths_hs_base.json -u username

# for run from remoterun.py use::

   ~/anaconda3/bin/./python3 -c "import hybriddomain.gens.hs.tests.tests_gen_1d as ts; ts.run_from_remoterun()" -t logistic_delays -u username

# from project_folder::

 ~/anaconda3/bin/./python3 -c "import hybriddomain.gens.hs.tests.tests_gen_1d as ts; ts.run_from_remoterun()" -t ~/Documents/projects/projectsNew/lab/project_folder/problems/logistic_delays -p connection.json -d devices.json -w ~/Documents/projects/projectsNew/lab/project_folder -u username


Test src gen for 2d:
--------------------

::
 (Important note: if there is two blocks in model, ``ics_other.json`` file must be used (where "taskCountPerNode": "2")(see :doc:`json Hardware and Mapping settings, device_conf settings <overview_mapping>` for more))

To just generate src files use  ``hybriddomain.gens.hs.tests.tests_gen_2d``::

 ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t project_folder -d device_conf_rpath -p paths_rpath -w workspace_folder_location -u username

where

   - ``problem_folder`` -- project path to folder, where .json file stored
         and it can be:

      either relative to hd:

      (ex: ``hybriddomain/problems/2dTests/heat_block_1``)::

	python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t hybriddomain/problems/2dTests/heat_block_2_ics_other -d ics_other

      or absolute::
      
	python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t ~/projects/lab/hybriddomain/hybriddomain/problems/2dTests/heat_block_2_ics_other -d device_conf/ics_other.json

      or test_folder name
          where test_folder in ``hd/problems/2dTests``::

           python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other -d device_conf/ics_other.json

   - ``workspace_folder_location`` -- (optional) is path to folder
      where "problems" and "settings" folder lie.
      If no given, "problems" will be used from hd/hd/problems,
      "settings" from hd/hd/settings.
      This parameter used only at server (remotely).

   - ``username`` -- used for interpetation of tilde (~) in pathes if
      connection file not used or not exist.

   - ``paths_rpath`` -- (optional) is relative to settings if running from project_folder
      (or hd/hd/settings if running from hd) path of paths file
      default is ``paths/paths_hs_base.json``

   - ``device_conf_rpath`` -- (optional) is relative to settings if running from project_folder
      (or hd/hd/settings if running from hd) path of device config file
      default is ``device_conf/default.json``

# Examples:

# for tests at client side from hd repository folder (where hd folder located) use::


   ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other -d device_conf/ics_other.json -u username

# or with undefault settings::

   ~/anaconda3/bin/./python3 -m hybriddomain.gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other -d device_conf/ics_other.json -p paths/paths_hs_base.json -u username

# for run from remoterun.py use::

  ~/anaconda3/bin/./python3 -c "import hybriddomain.gens.hs.tests.tests_gen_2d as ts; ts.run()" -t heat_block_2_ics_other -d device_conf/ics_other.json -u username

# from project_folder::

  ~/anaconda3/bin/./python3 -c "import hybriddomain.gens.hs.tests.tests_gen_2d as ts; ts.run()" -t ~/Documents/projects/projectsNew/lab/project_folder/problems/2dTests/heat_block_1 -p connection.json -d devices.json -w ~/Documents/projects/projectsNew/lab/project_folder -u username

