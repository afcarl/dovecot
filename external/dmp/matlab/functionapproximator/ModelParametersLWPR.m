classdef ModelParametersLWPR < Parameterizable
  properties(SetAccess='private')
    ID_
    model_
  end

  methods
    function obj = ModelParametersLWPR(ID, model)
      obj.ID_    = ID;
      obj.model_ = model;
    end

    function selectable_labels = getSelectableModelParameters(obj)
      selectable_labels = {};
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function size = getModelParameterValuesSize(obj)
      size = 0;
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function obj = setSelectedModelParameters(obj,selected_values_labels)
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function values = getModelParameterValues(obj)
      values = [];
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function obj = setModelParameterValues(obj,values)
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function model_parameters_clone = clone(obj)
      model_parameters_clone = 0;
      error('Not implemented yet...') %#ok<WNTAG>
    end
  end  
end


% ModelParametersLWPR(LWPR_Object* lwpr_object)
% :
%   obj.lwpr_object_ = lwpr_object;
% {
%   
%   % Initialize the value_types_ vector
%   n_centers = 0;
%   n_slopes = 0;
%   n_offsets = 0;
% 	for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
% 	{
% 		for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
% 		{
%       n_centers += lwpr_object_->nIn(); 
%       n_slopes  += lwpr_object_->model.sub[iDim].rf[iRF]->nReg;
%       n_offsets += 1;
% end
% end
%   n_widths = n_centers;
%   
%   n_values = n_centers + n_widths + n_slopes + n_offsets;
%   value_types_ = VectorXi(n_values);
%   value_types_ << Constant(n_centers, LWPR_CENTERS),
%                   Constant( n_widths, LWPR_WIDTHS ),
%                   Constant( n_slopes, LWPR_SLOPES ),
%                   Constant(n_offsets, LWPR_OFFSETS );   
% end
%   
% ModelParametersLWPR* clone()  {
%   LWPR_Object* lwpr_object_clone =  LWPR_Object(*lwpr_object_);
%   return  ModelParametersLWPR(lwpr_object_clone);
% end
% 
% ostream& toStream(ostream& output)  {
%   output << "ModelParametersLWPR[todo]";
%   return output;
% end
% 
% istream& fromStream(istream& input) {
%   cerr << _FILE___ << ":" << _LINE___ << ":Not implemented yet!" << endl;
%   return input;
% end
% 
%  getValues(VectorXd& values)  {
%   % First determine the size of the values vector to be returned and resize it.
%   values.resize(length(value_types_));
% 
%   ii=0;
%   
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->nIn(); j++)
%        values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->c[j];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->nIn(); j++)
%         values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->D[j*lwpr_object_->model.nInStore+j];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->model.sub[iDim].rf[iRF]->nReg; j++)
%         values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->beta[j];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       values[ii++] = lwpr_object_->model.sub[iDim].rf[iRF]->beta0;
% end
% 
% 
%  setValues( VectorXd& values) {
%   if (length(value_types_) != length(values))
%   {
%     cerr << _FILE___ << ":" << _LINE___ << ": values is of wrong size." << endl;
%     return;
% end
% 
%   ii=0;
%   
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->nIn(); j++)
%        lwpr_object_->model.sub[iDim].rf[iRF]->c[j] = values[ii++];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->nIn(); j++)
%         lwpr_object_->model.sub[iDim].rf[iRF]->D[j*lwpr_object_->model.nInStore+j] = values[ii++];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       for (j = 0; j < lwpr_object_->model.sub[iDim].rf[iRF]->nReg; j++)
%         lwpr_object_->model.sub[iDim].rf[iRF]->beta[j] = values[ii++];
%       
%   for (iDim = 0; iDim < lwpr_object_->model.nOut; iDim++)
%     for (iRF = 0; iRF < lwpr_object_->model.sub[iDim].numRFS; iRF++)
%       lwpr_object_->model.sub[iDim].rf[iRF]->beta0 = values[ii++];
% end
% 
%  getValueTypes(VectorXi& value_types) 
% { 
%   value_types =  value_types_;
% end
% 
% /*
% %  save( char* file)
% % {
% % 	lwpr_object_->writeBinary(file);
% % }
% */
