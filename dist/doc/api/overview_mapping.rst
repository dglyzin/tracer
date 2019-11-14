Overview json Hardware and Mapping settings, device_conf settings
=================================================================

Mapping settings
-------------

Represented in ``.json`` files in ``Mappings`` directive::

  "Mapping": {
        "IsMapped": true, 
        "BlockMapping": [
            {
                "NodeIdx": 0, 
                "DeviceType": "cpu", 
                "DeviceIdx": 0
            }, 
            {
                "NodeIdx": 1, 
                "DeviceType": "cpu", 
                "DeviceIdx": 0
            }
        ]

Each node in ``BlockMapping`` list corespond to each block.
``NodeIdx`` must be differ for each block.
So if interconnects used with differ blocks, they all mast differ nodes.
This parameters add N to solver ``salloc`` command (in that case 2)::

  salloc -N 2 -n 2 -w cnode7 -p exp  mpirun  ~/projects/lab/hybridsolver/bin/HS

For this configuration to work (with two blocks) correctly, maximum task per node must be equal to count of blocks
(count of nodes). This can be achived with ``taskCountPerNode`` attribute of ``device_conf`` file
(in ``settings/device_conf`` folder)::

     "taskCountPerNode": "2"

This parameters add n to  solver ``salloc`` command (in that case 2)::

  salloc -N 2 -n 2 -w cnode7 -p exp  mpirun  ~/projects/lab/hybridsolver/bin/HS

Also there is a ``Hardware`` parameter in json file::

   "Hardware": [
        {
            "Name": "cnode7", 
            "CpuCount": 2, 
            "CpuMemory": [
                56
            ], 
            "GpuCount": 3, 
            "GpuMemory": [
                5, 
                5, 
                5
            ]
        },
	{
            "Name": "cnode7", 
            "CpuCount": 2, 
            "CpuMemory": [
                56
            ], 
            "GpuCount": 3, 
            "GpuMemory": [
                5, 
                5, 
                5
            ]
        }

This parameters add -w to solver ``salloc`` command (in that case cnode7, cnode7)::

  salloc -N 2 -n 2 -w cnode7, cnode7 -p exp  mpirun  ~/projects/lab/hybridsolver/bin/HS
