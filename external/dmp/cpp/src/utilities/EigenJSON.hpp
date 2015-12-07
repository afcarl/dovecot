#ifndef EIGENJSON_HPP
#define EIGENJSON_HPP


#include <string>
#include <vector>
#include <iostream>
#include <eigen3/Eigen/Core>

// zzz Move implementations to tpp file

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline std::string serializeJSON(const Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime>& m)
{
  std::stringstream stream;
  stream << "[";
  for (int ii=0; ii<m.rows(); ii++)
  {
    if (ii>0) stream << ", ";
    stream << "[";
    for (int jj=0; jj<m.cols(); jj++)
    {
      if (jj>0) stream << ", ";
      stream << m(ii,jj);
    }
    stream << "]"; 
  }
  stream << "]"; 
  
  return stream.str();
}


template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline std::string serializeJSON(const std::vector<Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime>* >& v_m)
{
  std::stringstream stream;
  stream << "[";
  for (unsigned int ii=0; ii<v_m.size(); ii++)
  {
    if (ii>0) stream << ", ";
    stream << serializeJSON(*(v_m[ii]));
  }
  stream << "]"; 
  
  return stream.str();
}

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline std::string serializeJSON(const std::vector<Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime> >& v_m)
{
  std::stringstream stream;
  stream << "[";
  for (unsigned int ii=0; ii<v_m.size(); ii++)
  {
    if (ii>0) stream << ", ";
    stream << serializeJSON(v_m[ii]);
  }
  stream << "]"; 
  
  return stream.str();
}

template<typename Scalar, int ColsAtCompileTime>
inline std::string serializeJSON(const std::vector<Eigen::Matrix<Scalar,1,ColsAtCompileTime> >& v_v)
{
  std::stringstream stream;
  stream << "[";
  for (unsigned int ii=0; ii<v_v.size(); ii++)
  {
    if (ii>0) stream << ", ";
    stream << "[";
    for (int jj=0; jj<v_v[ii].size(); jj++)
    {
      if (jj>0) stream << ", ";
      stream << v_v[ii][jj];
    }
    stream << "]"; 
  }
  stream << "]"; 
  
  return stream.str();
}


template<typename Scalar, int ColsAtCompileTime>
inline bool deserializeRowVectorJSON(const std::string& str, Eigen::Matrix<Scalar,1,ColsAtCompileTime>& v)
{
  std::stringstream strstream(str);
  if (strstream.peek() == '[')
  {
    strstream.ignore();
  }
  else 
  {
    std::cerr << __FILE__ << ":" << __LINE__ << ":ERROR: Expected '['" << std::endl;
    return false;
  }
  
  std::vector<double> vect;
  double value;
  while (strstream >> value)
  {
    vect.push_back(value);
    if (strstream.peek() == ',')
      strstream.ignore();
  }
  
  // nnn Fix this
  Eigen::RowVectorXd v_d = Eigen::RowVectorXd::Map(&vect[0],vect.size());
  v = v_d.cast<Scalar>();
  return true;
  
}

template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline bool deserializeMatrixJSON(const std::string& str, Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime>& m)
{
  m.resize(0,0);
  
  std::stringstream strstream(str);
  if (strstream.peek() == '[')
  {
    strstream.ignore();
  }
  else 
  {
    std::cerr << __FILE__ << ":" << __LINE__ << ":ERROR: Expected '['" << std::endl;
    return false;
  }

  std::string cur_str="";
  char c;
  while (strstream >> c)
  {
    cur_str += c;
    if (c==']')
    {
      if (cur_str.size()==1)
      {
        // You have read a ']', and it is the last one (because there are no preceding numbers
        // because (cur_str.size()==1). Therefore, reading is done. 
        return true;
      }
      
      Eigen::Matrix<Scalar,1,ColsAtCompileTime> v;
      if (!deserializeRowVectorJSON(cur_str,v))
        return false;
      
      if (m.rows()==0)
      {
        m = v;  
      }
      else
      {
        if (v.size()!=m.cols())
        {
          std::cerr << __FILE__ << ":" << __LINE__ << ":";
          std::cerr << "ERROR: number of columns in matrix must be the same." << std::endl;
        }
        m.conservativeResize(m.rows()+1,m.cols());
        m.bottomRows(1) = v; 
      }
      
      cur_str = "";

      if (strstream.peek() == ',')
        strstream.ignore();
    }
  }
  
  return true;
  
}


template<typename Scalar, int RowsAtCompileTime>
inline bool deserializeStdVectorEigenVectorJSON(const std::string& str, std::vector<Eigen::Matrix<Scalar,RowsAtCompileTime,1> >& v_v)
{
  v_v.clear();
  
  std::stringstream strstream(str);
  if (strstream.peek() == '[')
  {
    strstream.ignore();
  }
  else 
  {
    std::cerr << __FILE__ << ":" << __LINE__ << ":ERROR: Expected '['" << std::endl;
    return false;
  }

  std::string cur_str="";
  char c;
  while (strstream >> c)
  {
    cur_str += c;
    if (c==']')
    {
      if (cur_str.size()==1)
      {
        // You have read a ']', and it is the last one (because there are no preceding numbers
        // because (cur_str.size()==1). Therefore, reading is done. 
        return true;
      }
      
      Eigen::Matrix<Scalar,1,RowsAtCompileTime> v;
      if (!deserializeRowVectorJSON(cur_str,v))
        return false;
      
      Eigen::Matrix<Scalar,RowsAtCompileTime,1> v_trans = v.transpose();
      v_v.push_back(v_trans);
      
      cur_str = "";

      if (strstream.peek() == ',')
        strstream.ignore();
    }
  }
  
  return true;
  
}


template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline bool deserializeStdVectorEigenMatrixJSON(const std::string& str, std::vector<Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime> >& v_m)
{
  v_m.clear();
  
  std::stringstream strstream(str);
  if (strstream.peek() == '[')
  {
    strstream.ignore();
  }
  else 
  {
    std::cerr << __FILE__ << ":" << __LINE__ << ":ERROR: Expected '['" << std::endl;
    return false;
  }

  std::string cur_str="";
  char c;
  while (strstream >> c)
  {
    cur_str += c;
    if (c==']')
    {
      if (cur_str.size()==1)
      {
        // You have read a ']', and it is the last one (because there are no preceding numbers
        // because (cur_str.size()==1). Therefore, reading is done. 
        return true;
      }
      
      Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime> m;
      if (!deserializeMatrixJSON(cur_str,m))
        return false;
      v_m.push_back(m);
      
      cur_str = "";

      if (strstream.peek() == ',')
        strstream.ignore();
    }
  }
  
  return true;
  
}



template<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>
inline bool deserializeJSON(std::istream& strstream, Eigen::Matrix<Scalar,RowsAtCompileTime,ColsAtCompileTime>& m)
{
  m.resize(0,0);
  
  strstream >> std::ws;
  if (strstream.peek() == '[')
  {
    strstream.ignore();
  }
  else 
  {
    std::cerr << __FILE__ << ":" << __LINE__ << ":ERROR: Expected '['" << std::endl;
    return false;
  }

  std::string cur_str="";
  char c;
  while (strstream >> c)
  {
    cur_str += c;
    if (c==']')
    {
      if (cur_str.size()==1)
      {
        // You have read a ']', and it is the last one (because there are no preceding numbers
        // because (cur_str.size()==1). Therefore, reading is done. 
        return false;
      }
      
      Eigen::Matrix<Scalar,1,ColsAtCompileTime> v;
      if (!deserializeRowVectorJSON(cur_str,v))
        return false;
      
      if (m.rows()==0)
      {
        m = v;  
      }
      else
      {
        if (v.size()!=m.cols())
        {
          std::cerr << __FILE__ << ":" << __LINE__ << ":";
          std::cerr << "ERROR: number of columns in matrix must be the same." << std::endl;
        }
        m.conservativeResize(m.rows()+1,m.cols());
        m.bottomRows(1) = v; 
      }
      
      cur_str = "";

      if (strstream.peek() == ',')
        strstream.ignore();
    }
  }
  
  return true;
  
}

inline std::istream& operator>>(std::istream& input, Eigen::MatrixXd& m)
{
  deserializeJSON(input,m);
  return input;
}

#endif        //  #ifndef EIGENJSON_HPP

