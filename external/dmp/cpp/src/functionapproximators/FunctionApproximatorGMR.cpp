/**
 * @file   FunctionApproximatorGMR.cpp
 * @brief  FunctionApproximator class source file.
 * @author Thibaut Munzer, Freek Stulp
 */
 
/*
 * Copyright (C) 2013 MACSi Project
 * author:  Thibaut Munzer, Freek Stulp
 * website: www.macsi.isir.upmc.fr
 *
 * Permission is granted to copy, distribute, and/or modify this program
 * under the terms of the GNU General Public License, version 2 or any
 * later version published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
 * Public License for more details
 */

#include "functionapproximators/FunctionApproximatorGMR.h"

#include "functionapproximators/ModelParametersGMR.h"
#include "functionapproximators/MetaParametersGMR.h"

#include <iostream> 
#include <eigen3/Eigen/LU>
#include <eigen3/Eigen/Cholesky>

using namespace std;
using namespace Eigen;

FunctionApproximatorGMR::FunctionApproximatorGMR(MetaParametersGMR* meta_parameters, ModelParametersGMR* model_parameters)
:
  FunctionApproximator(meta_parameters,model_parameters)
{
}

FunctionApproximatorGMR::FunctionApproximatorGMR(ModelParametersGMR* model_parameters)
:
  FunctionApproximator(model_parameters)
{
}

FunctionApproximator* FunctionApproximatorGMR::clone(void) const {
  MetaParametersGMR* meta_params  = NULL;
  if (getMetaParameters()!=NULL)
    meta_params = dynamic_cast<MetaParametersGMR*>(getMetaParameters()->clone());

  ModelParametersGMR* model_params = NULL;
  if (getModelParameters()!=NULL)
    model_params = dynamic_cast<ModelParametersGMR*>(getModelParameters()->clone());

  if (meta_params==NULL)
    return new FunctionApproximatorGMR(model_params);
  else
    return new FunctionApproximatorGMR(meta_params,model_params);
};

void FunctionApproximatorGMR::train(const MatrixXd& inputs, const MatrixXd& targets)
{
  if (isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorGMR::train more than once. Doing nothing." << endl;
    cerr << "   (if you really want to retrain, call reTrain function instead)" << endl;
    return;
  }
  
  assert(inputs.rows() == targets.rows()); // Must have same number of examples
  assert(inputs.cols()==getExpectedInputDim());

  const MetaParametersGMR* meta_parameters_GMR = 
    static_cast<const MetaParametersGMR*>(getMetaParameters());

  int nbGaussian = meta_parameters_GMR->number_of_gaussians_;
  int gmmDim = inputs.cols() + targets.cols();

  std::vector<VectorXd*> gmmCenters;
  std::vector<double*> gmmPriors;
  std::vector<MatrixXd*> gmmCovars;

  for (int i = 0; i < nbGaussian; i++)
  {
    gmmCenters.push_back(new VectorXd(gmmDim));
    gmmPriors.push_back(new double(0));
    gmmCovars.push_back(new MatrixXd(gmmDim, gmmDim));
  }

  MatrixXd gmmData = MatrixXd(inputs.rows(), gmmDim);
  gmmData << inputs, targets;

  _kMeansInit(gmmData, gmmCenters, gmmPriors, gmmCovars);
  _EM(gmmData, gmmCenters, gmmPriors, gmmCovars);

  std::vector<VectorXd*> centers;
  std::vector<MatrixXd*> slopes;
  std::vector<VectorXd*> biases;
  std::vector<MatrixXd*> inverseCovarsL;

  int nbInDim = inputs.cols();
  int nbOutDim = targets.cols();

  for (int iCenter = 0; iCenter < nbGaussian; iCenter++)
  {
    centers.push_back(new VectorXd(gmmCenters[iCenter]->segment(0, nbInDim)));

    slopes.push_back(new MatrixXd(gmmCovars[iCenter]->block(nbInDim, 0, nbOutDim, nbInDim) * gmmCovars[iCenter]->block(0, 0, nbInDim, nbInDim).inverse()));
    
    biases.push_back(new VectorXd(gmmCenters[iCenter]->segment(nbInDim, nbOutDim) -
      *(slopes[iCenter]) * gmmCenters[iCenter]->segment(0, nbInDim)));

    MatrixXd L = gmmCovars[iCenter]->block(0, 0, nbInDim, nbInDim).inverse().llt().matrixL();
    inverseCovarsL.push_back(new MatrixXd(L));
  }

  setModelParameters(new ModelParametersGMR(centers, gmmPriors, slopes, biases, inverseCovarsL));

  for (size_t i = 0; i < gmmCenters.size(); i++)
    delete gmmCenters[i];
  for (size_t i = 0; i < gmmCovars.size(); i++)
    delete gmmCovars[i];
}

void FunctionApproximatorGMR::predict(const MatrixXd& input, MatrixXd& output)
{
  if (!isTrained())  
  {
    cerr << "WARNING: You may not call FunctionApproximatorGMR::predict if you have not trained yet. Doing nothing." << endl;
    return;
  }
  
  const ModelParametersGMR* model_parameters_GMR = static_cast<const ModelParametersGMR*>(getModelParameters());
  const MetaParametersGMR* meta_parameters_GMR = static_cast<const MetaParametersGMR*>(getMetaParameters());
  int nbGaussian = meta_parameters_GMR->number_of_gaussians_;

  int nbOutDim = model_parameters_GMR->biases_[0]->size();

  output = MatrixXd(input.rows(), nbOutDim);

  for (int i = 0; i < input.rows(); i++)
  {
    VectorXd inputPoint = input.row(i);
    VectorXd h(nbGaussian);
    VectorXd partialH(nbGaussian);
  
    for (int iCenter = 0; iCenter < nbGaussian; iCenter++)
    {
      VectorXd center = *(model_parameters_GMR->centers_[iCenter]);
      partialH[iCenter] = -1. / 2 * ((inputPoint - center).transpose() * *(model_parameters_GMR->inverseCovarsL_[iCenter]) *
        model_parameters_GMR->inverseCovarsL_[iCenter]->transpose() * (inputPoint - center))(0, 0);
    }
    double max = partialH.maxCoeff();
    for (int iCenter = 0; iCenter < nbGaussian; iCenter++)
      partialH[iCenter] -= max;

    for (int iCenter = 0; iCenter < nbGaussian; iCenter++)
    {
      VectorXd center = *(model_parameters_GMR->centers_[iCenter]);
      double det = 1. / pow((*(model_parameters_GMR->inverseCovarsL_[iCenter]) * model_parameters_GMR->inverseCovarsL_[iCenter]->transpose()).determinant(), 2);
      h[iCenter] = *(model_parameters_GMR->priors_[iCenter]) * 1. / sqrt(pow(2 * M_PI, center.rows()) * det) * exp(partialH[iCenter]);
    }
    h /= h.sum();

    VectorXd prediction(nbOutDim);
    prediction.setZero();
    for (int iCenter = 0; iCenter < nbGaussian; iCenter++)
    {
      VectorXd tmp = *(model_parameters_GMR->slopes_[iCenter]) * inputPoint;
      prediction += h[iCenter] * (*(model_parameters_GMR->biases_[iCenter]) + tmp);
    }
    output.row(i) = prediction;
  }
}

void FunctionApproximatorGMR::_kMeansInit(const MatrixXd& data, std::vector<VectorXd*>& centers, std::vector<double*>& priors,
  std::vector<MatrixXd*>& covars, int nbMaxIter)
{

  MatrixXd dataCentered = data.rowwise() - data.colwise().mean();
  MatrixXd dataCov = dataCentered.transpose() * dataCentered / data.rows();
  MatrixXd dataCovInverse = dataCov.inverse();

  std::vector<int> dataIndex;
  for (int i = 0; i < data.rows(); i++)
    dataIndex.push_back(i); 
  std::random_shuffle (dataIndex.begin(), dataIndex.end());

  for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    *(centers[iCenter]) = data.row(dataIndex[iCenter]);

  VectorXi assign(data.rows());
  assign.setZero();

  bool converged = false;
  for (int iIter = 0; iIter < nbMaxIter && !converged; iIter++)
  {
    // E step
    converged = true;
    for (int iData = 0; iData < data.rows(); iData++)
    {
      VectorXd v = (*(centers[assign[iData]]) - data.row(iData).transpose());

      double minDist = v.transpose() * dataCovInverse * v;

      for (int iCenter = 0; iCenter < (int)centers.size(); iCenter++)
      {
        if (iCenter == assign[iData])
          continue;

        v = (*(centers[iCenter]) - data.row(iData).transpose());
        double dist = v.transpose() * dataCovInverse * v;
        if (dist < minDist)
        {
          converged = false;
          minDist = dist;
          assign[iData] = iCenter;
        }
      }
    }

    // M step
    VectorXi nbPoints = VectorXi::Zero(centers.size());
    for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
      centers[iCenter]->setZero();
    for (int iData = 0; iData < data.rows(); iData++)
    {
      *(centers[assign[iData]]) += data.row(iData).transpose();
      nbPoints[assign[iData]]++;
    }
    for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
      *(centers[iCenter]) /= nbPoints[iCenter];
  }

  // Init covars
  VectorXi nbPoints = VectorXi::Zero(centers.size());
  for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    covars[iCenter]->setZero();
  for (int iData = 0; iData < data.rows(); iData++)
  {
    *(covars[assign[iData]]) += (data.row(iData).transpose() - *(centers[assign[iData]])) * (data.row(iData).transpose() - *(centers[assign[iData]])).transpose();
    nbPoints[assign[iData]]++;
  }
  for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    *(covars[iCenter]) /= nbPoints[iCenter];

  // Init priors
  for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    *(priors[iCenter]) = 1. / centers.size();
}

void FunctionApproximatorGMR::_EM(const MatrixXd& data, std::vector<VectorXd*>& centers, std::vector<double*>& priors,
    std::vector<MatrixXd*>& covars, int nbMaxIter)
{
  MatrixXd assign(centers.size(), data.rows());
  assign.setZero();

  for (int iIter = 0; iIter < nbMaxIter; iIter++)
  {
    // E step
    for (int iData = 0; iData < data.rows(); iData++)
      for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
        assign(iCenter, iData) = *(priors[iCenter]) * _normal(data.row(iData).transpose(), *(centers[iCenter]), *(covars[iCenter]));

    for (int iData = 0; iData < data.rows(); iData++)
      assign.col(iData) /= assign.col(iData).sum();

    // M step
    for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    {
      centers[iCenter]->setZero();
      covars[iCenter]->setZero();
      *(priors[iCenter]) = 0;
    }

    for (int iData = 0; iData < data.rows(); iData++)
    {
      for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
      {
        *(centers[iCenter]) += assign(iCenter, iData) * data.row(iData).transpose();
        *(priors[iCenter]) += assign(iCenter, iData);
      }
    }

    for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
    {
      *(centers[iCenter]) /= assign.row(iCenter).sum();
      *(priors[iCenter]) /= assign.cols();
    }

    for (int iData = 0; iData < data.rows(); iData++)
      for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
        *(covars[iCenter]) += assign(iCenter, iData) * (data.row(iData).transpose() - *(centers[iCenter])) * (data.row(iData).transpose() - *(centers[iCenter])).transpose();

    for (size_t iCenter = 0; iCenter < centers.size(); iCenter++)
      *(covars[iCenter]) /= assign.row(iCenter).sum();
  }
}

double FunctionApproximatorGMR::_normal(const VectorXd& data, const VectorXd& center, const MatrixXd& cov)
{
  double tmp = -1. / 2 * ((data - center).transpose() * cov.inverse() * (data - center))(0, 0);
  return 1. / sqrt(pow(2 * M_PI, center.cols()) * cov.determinant()) * exp(tmp);
}