#ifndef EIGENSAVEMATRIX_HPP
#define EIGENSAVEMATRIX_HPP

#include <string>

#include <eigen3/Eigen/Core>

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
bool loadMatrix(std::string filename, Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime>& m);

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
bool saveMatrix(std::string filename, Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime> matrix, bool overwrite=false);

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
bool saveMatrix(std::string directory, std::string filename, Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime> matrix, bool overwrite=false);

#include "EigenFileIO.tpp"


#endif        //  #ifndef EIGENSAVEMATRIX_HPP

