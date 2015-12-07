/**
 * @file mainpage.h
 * @brief File containing only documentation (for the Doxygen mainpage)
 * @author Freek Stulp
 */

/** \mainpage 

This library contains several modules for training dynamical movement primitives (DMPs), and optimizing their parameters through black-box optimization. Each module has its own dedicated page.

\li \ref page_dyn_sys This module provides implementations of several basic dynamical systems. DMPs are combinations of such systems. This module is completely independent of all other modules.

\li \ref page_func_approx This module provides implementations (but mostly wrappers around external libraries) of several function approximators. DMPs use function approximators to learn and reproduce arbitrary smooth movements. This module is completely independent of all other modules.

\li \ref page_dmp This module provides an implementation of several types of DMPs. It depends on both the DynamicalSystems and FunctionApproximators modules, but no other.

\li \ref page_bbo This module provides implementations of several stochastic optimization algorithms for the optimization of black-box cost functions. This module is completely independent of all other modules.  

\li \ref page_dmp_bbo This module applies black-box optimization to the parameters of a DMP. It depends on all the other modules.

Each of the pages linked to above contains two sections: 

\li A tutorial that treats the concepts that are implemented 
\li A description of how these concepts have been implemented, and why it has been done so in this fashion.

If you want a deeper understanding of the entire library, I recommend you to go through the pages in the order above. If you want to start coding immediately, I suggest to look at the \ref Demos to see how the functionality of the library may be used. The demos for each module are found in  cpp/MODULENAME/demos.

Some general considerations on the design of the library are here \ref page_design

*/

/** \page page_design Design Rationale

\todo Design Rationale

Here's a brief discussion of why I designed things the way they are:

\li Why Matlab and C++?

\li Input: const ref, Output, ref.

\li Why do you use Eigen in the wrong way? I used this project to learn Eigen by learning-by-doing. So I might not be proficient in it yet. If you find convoluted solutions, please let me know if there are ways to make the code more legible or efficient.

\li Why not PIMPL? Keep code simple, relatively small code base.

\li Why state as one big vector. Easier to store. 

\verbatim
CODE ORGANIZATION
http://stackoverflow.com/questions/13521618/c-project-organisation-with-gtest-cmake-and-doxygen/13522826#13522826
________________________________________________________________________________
DESIGN DECISIONS TO SIMPLIFY CODE
  Do not change dimensionality of a DynamicalSystem. Determined during construction
  Not use factory design pattern, but rather clone

________________________________________________________________________________
DESIGN DECISIONS TO OPTIMIZE CODE
  ModelParameters
    rather dynamic_cast of ModelParameters
    XOR different members in different classes 
    XOR copy in different classes

________________________________________________________________________________
DESIGN DECISIONS TO KEEP CODE GENERAL    

For standard optimization, n_parallel = 1 and n_time_steps = 1 so that
                    vector<Matrix>            Matrix
  samples         =                   n_samples x n_dim
  task_parameters =                   n_samples x n_task_pars
  cost_vars       =                   n_samples x n_cost_vars


Generic case: n_dofs-D Dmp, n_parallel=n_dofs
                    vector<Matrix>            Matrix
  samples         = n_parallel     x  n_samples x sum(n_model_parameters)
  task_parameters =                   n_samples x n_task_pars
  cost_vars       =                   n_samples x (n_time_steps*n_cost_vars)

  
Standard optimization is special case of the above with, n_parallel = 1 and n_time_steps = 1
\endverbatim

\section Style

\verbatim

http://google-styleguide.googlecode.com/svn/trunk/cppguide.xml#Naming

Exception: 
  functions start with low caps (as in Java, to distinguish them from classes) 
  filenames for classes follow the classname (i.e. CamelCased)
  
  
  

http://google-styleguide.googlecode.com/svn/trunk/cppguide.xml#Names_and_Order_of_Includes
    dir2/foo2.h (preferred location — see details below).
    C system files.
    C++ system files.
    Other libraries' .h files.
    Your project's .h files.
\endverbatim

*/

/** \defgroup Demos Demos
 */
 

