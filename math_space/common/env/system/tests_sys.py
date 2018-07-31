import os
import sys
import inspect

# add import's path:
current_dir = (os.path
               .dirname(os.path
                        .abspath(inspect.getfile(inspect.currentframe()))))
parent_dir = os.path.dirname(current_dir)
eq_dir = os.path.join(parent_dir, 'equation')
sys_dir = os.path.join(parent_dir, 'system')
print("current_dir:")
print(current_dir)
sys.path.insert(0, sys_dir)


from env.system.sys_main import sysNet as System


def test_sys():
    '''
    s = ts.test_sys()
    s[0].show_cpp()
    or
    out = s[0].make_cpp()
    '''
    eq_1 = "U' = U(t-1.1) + U(t-0.9) + U(t-1.2) + V + V(t-1.1)"
    eq_2 = "U' = U(t-1.1) + U(t-0.7) + U(t-1.2) + V(t-0.3)"
    eq_3 = "U' = U(t-1.2) + U(t-0.7) + U(t-1.3)"

    # create system and parse equations:
    system = System(system=[eq_1, eq_2, eq_3])

    # generate cpp:
    system.cpp.set_default()
    system.cpp.gen_cpp()

    # collect all nodes in one place
    # (system.postproc.nodes):
    system.postproc.collect_nodes()

    # convert delays:
    system.postproc.postproc_nodes()
    return(system)


def test_sinch_sys():

    eq_1 = "U' = U(t-1.1) + U(t-0.9) + U(t-1.2) + V + V(t-1.1)"
    eq_2 = "U' = U(t-1.1) + U(t-0.7) + U(t-1.2) + V(t-0.3)"
    eq_3 = "U' = U(t-1.2) + U(t-0.5) + U(t-1.3)"

    # create system and parse equations:
    sys_1 = System(system=[eq_1, eq_2])
    sys_2 = System(system=[eq_2, eq_3])

    # generate cpp:
    sys_1.cpp.set_default()
    sys_1.cpp.gen_cpp()
    sys_2.cpp.set_default()
    sys_2.cpp.gen_cpp()

    # collect all nodes in one place
    # (system.postproc.nodes):
    sys_1.postproc.collect_nodes()
    sys_2.postproc.collect_nodes()

    # sinch systems:
    sys_1.postproc.postproc_delay_sys([sys_2])

    print("sys_1.original")
    sys_1.plotter.show_original()

    print("sys_2.original")
    sys_2.plotter.show_original()

    print("sys_1.cpp")
    sys_1.plotter.show_cpp()

    print("sys_2.cpp")
    sys_2.plotter.show_cpp()

    print('sys_1.global_data:')
    sys_1.postproc.show_nodes_global_data()
    print('sys_2.global_data:')
    sys_2.postproc.show_nodes_global_data()
    return(sys_1)


if __name__ == '__main__':
    # test_sys()
    test_sinch_sys()
