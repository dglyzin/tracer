# must be outside hybriddomain
import os
import sys
# sys.path.insert(0, "/home/valdecar/Downloads/programs/py_packages/setuptools-master")

from setuptools import setup, find_packages, find_namespace_packages
from pkg_resources import get_distribution, DistributionNotFound

import setuptools_scm
from setuptools_scm import get_version
from setuptools_scm.integration import find_files

# hybriddomain
this_dir = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
    print("\nthis_dir:")
    print(this_dir)
    print("\nfind_packages:")
    print(find_packages('.'))
    print("\nget_version:")
    print(get_version(root='.', relative_to=__file__))

    # for description:
    with open("readme.txt") as f:
        long_description = f.read()
    
    # for requirements:
    with open("requirements.ini") as f:
        s_reguirements = f.read()
    requirements = s_reguirements.split("\n")
    print("\nrequirements:")
    print(requirements)

    setup(
        name="hybriddomain",

        # use version (only) from setuptools_scm:
        use_scm_version=True,
        # version=get_version(root='.', relative_to=__file__),

        author="lab",
        author_email="lab@lab.com",
        description="Model creator for solvers",
        long_description=long_description,
        long_description_content_type="text",
        url="",
        packages=find_packages('.'),
        include_package_data=True,

        exclude_package_data={"hybriddomain.tests":
                              ["*.json", "*.ipynb",
                               "problems/*", "settings/*"]},
        # for ``include_package_data`` to work accordingly to git:
        # setuptools_scm will register itself as setuptools plug in,
        # with use of ``entry_points``, so it's git/hg ``file_finders``
        # will be implicitly used for finding only git/hg managable files
        # (that not in .{git/hg}ignore) when ``include_package_data``
        # or ``package_data`` attributes of setuptools.setup() was used.
        # (see https://github.com/pypa/setuptools_scm/blob/master/setup.py)

        # this will automatically used due to setup_requires setuptools_scm
        # (it will add it's entry_points to the setuptools during install):
        # entry_points="""
        # [setuptools.file_finders]
        # setuptools_scm = setuptools_scm.integration:find_files
        # """,
       
        setup_requires=['setuptools_scm'],
        # setup_requires=[ "setuptools_git >= 0.3", ],
        install_requires=requirements
    )
