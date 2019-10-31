# must be outside hybriddomain
import os
from setuptools import setup, find_packages, find_namespace_packages
from pkg_resources import get_distribution, DistributionNotFound

import setuptools_scm
from setuptools_scm import get_version

# hybriddomain
this_dir = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
    print("this_dir:")
    print(this_dir)
    print("\nfind_packages:")
    print(find_packages('.'))
    
    with open("readme.txt") as f:
        long_description = f.read()
    
    setup(
        name="hybriddomain",
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
        exclude_package_data={"tests": ["*.json", "*.ipynb",
                                        "problems/*", "settings/*"]},
        # for ``include_package_data`` to work accordingly to git:
        # setuptools_scm will register itself as setuptools plug in,
        # with use of ``entry_points``, so it's git/hg ``file_finders``
        # will be implicitly used for finding only git/hg managable files
        # (that not in .{git/hg}ignore) when ``include_package_data``
        # or ``package_data`` attributes of setuptools.setup() was used.
        # (see https://github.com/pypa/setuptools_scm/blob/master/setup.py)
        setup_requires=['setuptools_scm'],
        # setup_requires=[ "setuptools_git >= 0.3", ],

    )
    
    '''
    entry_points={
    "setuptools.file_finders": [
        "foobar = setuptools_scm:files_command",
    ]
    }
    '''
    '''
    print("\nget_distribution version:")
    try:
        # __version__ = get_distribution(__name__).version
        # print(__version__)
        
        version = get_version(root='.', relative_to=__file__)
        print(version)
    except DistributionNotFound:
        # package is not installed
        print("not found")
    '''
