This repository provides an implementation of dynamical systems and
dynamical movement primitives.

The C++ implementation is in the directory cpp/
    The following modules are nearing completion, and have relatively
    complete documentation 
        dmp  
        dynamicalsystems  
        functionapproximators
    These modules are still under development and not documented well
    yet
        evolutionstrategies
        dmp_bbo  

The Matlab implementation is still under construction, please ignore
the matlab/ directory for now.



________________________________________________________________________________
Where to start?

To learn how to use the code, the first thing to do is look at the
documentation here:
    docs/html/index.html
        (this documentation must first be generated with the doxygen
        program, see cpp/INSTALL.txt) 

Each module has a set of demos and tests, e.g.
    cpp/src/dynamicalsystems/demos/
        The demos do not show all the functionality, but are well
        documented and a good place to understand how the code can be 
        used.
    cpp/src/dynamicalsystems/tests/
        The tests are not documented as well, but perform more
        extensive tests on the code. They are only built in debug mode
        (see cpp/INSTALL.txt)
  
        

________________________________________________________________________________
Installation

Please see cpp/INSTALL.txt for details
