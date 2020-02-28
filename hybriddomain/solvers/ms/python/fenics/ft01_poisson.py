"""
FEniCS tutorial demo program: Poisson equation with Dirichlet conditions.
Test problem is chosen to give an exact solution at all nodes of the mesh.

  -Laplace(u) = f    in the unit square
            u = u_D  on the boundary

  u_D = 1 + x^2 + 2y^2
    f = -6
"""

from __future__ import print_function
from fenics import *
import matplotlib.pyplot as plt
from mshr import *
import numpy as np


def run():

    # Create mesh
    channel = Rectangle(Point(0, 0), Point(2, 1))
    cylinder = Circle(Point(0.2, 0.2), 0.05)
    domain = channel - cylinder
    mesh = generate_mesh(domain, 32)

    '''
    # Create mesh and define function space
    mesh = UnitSquareMesh(8, 8)
    '''
    V = FunctionSpace(mesh, 'P', 1)
    # Define boundary condition
    u_D = Expression('1 + x[0]*x[0] + 2*x[1]*x[1]', degree=2)

    def boundary(x, on_boundary):
        return on_boundary

    bc = DirichletBC(V, u_D, boundary)

    # Define variational problem
    u = TrialFunction(V)
    v = TestFunction(V)
    f = Constant(-6.0)
    a = dot(grad(u), grad(v))*dx
    L = f*v*dx

    # Compute solution
    u = Function(V)
    solve(a == L, u, bc)

    v2d = vertex_to_dof_map(V)
    # nodal_values = u.compute_vertex_values()
    # nodal_values[v2d[i]] or nodal_values[v2d]
    # for same order as coordinats.

    # get func array:
    x = np.linspace(0, 2, 512)
    y = np.linspace(0, 1, 256)
    yv, xu = np.meshgrid(y, x)
    u.set_allow_extrapolation(True)
    f = np.vectorize(lambda xl, yl: u((xl, yl)))
    print("xu.max:")
    print(xu.max())
    print("yu.max:")
    print(yv.max())
    print(u((xu.max(), yv.max())))
    result = f(xu, yv)
    return((u, mesh, a, L, v2d, result))


if __name__ == '__main__':

    u, mesh, a, L, v2d, result = run()

    x = np.linspace(0,2, 512)
    y = np.linspace(0,1, 256)

    plt.imshow(result)
    plt.show()
    # Plot solution and mesh
    plot(u)
    # plot(mesh)

    # Save solution to file in VTK format
    # vtkfile = File('poisson/solution.pvd')
    # vtkfile << u

    '''
    # Compute error in L2 norm
    error_L2 = errornorm(u_D, u, 'L2')

    # Compute maximum error at vertices
    vertex_values_u_D = u_D.compute_vertex_values(mesh)
    vertex_values_u = u.compute_vertex_values(mesh)
    import numpy as np
    error_max = np.max(np.abs(vertex_values_u_D - vertex_values_u))

    # Print errors
    print('error_L2  =', error_L2)
    print('error_max =', error_max)
    '''
    # Hold plot
    # interactive()
    plt.show()
