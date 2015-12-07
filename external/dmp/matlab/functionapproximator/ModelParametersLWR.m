classdef ModelParametersLWR < Parameterizable
  
  properties
    centers_
    widths_
    slopes_
    offsets_
    
    centers_selected_;
    widths_selected_;
    slopes_selected_;
    offsets_selected_;
    
    selected_values_vector_size_;
  end

  methods
    function obj = ModelParametersLWR(centers, widths, slopes, offsets)
      obj.centers_ = centers;
      obj.widths_ = widths;
      obj.slopes_ = slopes;
      obj.offsets_ = offsets;
      
      assert(isequal(size(obj.centers_),size(obj.widths_)));
      assert(isequal(size(obj.centers_),size(obj.slopes_)));
      assert(isequal([size(obj.centers_,1) 1],size(obj.offsets_)));
   
      obj = obj.setSelectedModelParameters({'slopes'});
    end

    function selectable_labels = getSelectableModelParameters(obj) %#ok<INUSD>
      selectable_labels = {'centers','widths','slopes','offsets'};
    end
    
    function obj = setSelectedModelParameters(obj,selected_values_labels)
      obj.centers_selected_ = false;
      obj.widths_selected_ = false;
      obj.slopes_selected_ = false;
      obj.offsets_selected_ = false;

      sum_sizes = 0;
      if (~isempty(strmatch('centers',selected_values_labels)))
        obj.centers_selected_ = true;
        sum_sizes = sum_sizes + length(obj.centers_);
      elseif (~isempty(strmatch('widths',selected_values_labels)))
        obj.widths_selected_ = true;
        sum_sizes = sum_sizes + length(obj.widths_);
      elseif (~isempty(strmatch('slopes',selected_values_labels)))
        obj.slopes_selected_ = true;
        sum_sizes = sum_sizes + length(obj.slopes_);
      elseif (~isempty(strmatch('offsets',selected_values_labels)))
        obj.offsets_selected_ = true;
        sum_sizes = sum_sizes + length(obj.offsets_);
      end

      obj.selected_values_vector_size_ = sum_sizes;
    end

    function size = getModelParameterValuesSize(obj)
      size = obj.selected_values_vector_size_;
    end

    function values = getModelParameterValues(obj)
      values = [];
      if (obj.centers_selected_)
        values =  [values obj.centers_];
      end
      if (obj.widths_selected_)
        values =  [values obj.widths_];
      end
      if (obj.slopes_selected_)
        values =  [values obj.slopes_];
      end
    end

    function obj = setModelParameterValues(obj,values)
      if(~isequal(size(values),[1 obj.selected_values_vector_size_]))
        warning('Number of model parameter values must have size 1x%d. Not setting them.',len3*n_selected) %#ok<WNTAG>
      end
      
      offset = 0;
      if (obj.centers_selected_)
        obj.centers_ = values( offset + (1:length(obj.centers_)));
        offset = offset + length(obj.centers_);
      end
      if (obj.widths_selected_)
        obj.widths_ = values( offset+ (1:length(obj.widths_)));
        offset = offset + length(obj.widths_);
      end
      if (obj.slopes_selected_)
        obj.slopes_ = values( offset + (1:length(obj.slopes_)));
        offset = offset + length(obj.slopes_);
      end

    end
    
    function model_parameters_clone = clone(obj)
      model_parameters_clone = ModelParametersLWR(obj.centers_,obj.widths_,obj.slopes_);
    end
    
    function str = toString(obj)
      str = sprintf('%s[centers=(',class(obj));
      str = [str sprintf('%1.6f ',obj.centers_)];
      str = [str sprintf('), widths=(')];
      str = [str sprintf('%1.6f ',obj.widths_)];
      str = [str sprintf('), slopes=(')];
      str = [str sprintf('%1.6f ',obj.slopes_)];
      str = [str sprintf(')]')];
    end
  end
end
