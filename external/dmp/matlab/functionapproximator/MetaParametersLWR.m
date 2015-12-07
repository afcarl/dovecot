classdef MetaParametersLWR

  properties(SetAccess='private')
    num_rfs_per_dim_
    intersection_
    centers_
    widths_
  end

  methods
    function obj = MetaParametersLWR(num_rfs_per_dim,intersection)
      if (nargin<2), intersection=0.7; end;
      
      obj.num_rfs_per_dim_ = num_rfs_per_dim;
      obj.intersection_    = intersection;
    end
    function obj = MetaParametersLWROld(varargin)
      % Usage:
      %   MetaParametersLWR()                       
      %   MetaParametersLWR(num_rfs)            
      %   MetaParametersLWR(num_rfs, intersection)
      %      defaults for num_rfs and intersection are set if not passed
      %   MetaParametersLWR(centers)
      %   MetaParametersLWR(centers, intersection)
      %   MetaParametersLWR(centers, widths)
      %      defaults for intersection is set if intersection or widths not passed
      optargin = size(varargin,2);

      % Defaults
      obj.num_rfs_ = 10;
      obj.intersection_ = 0.7;
      obj.centers_ = [];
      obj.widths_ = [];
      
      if (optargin>0)
        if (numel(varargin{1})==1)
          obj.num_rfs_ = varargin{1};
          if (optargin==2)
            obj.intersection_ = varargin{2};
            assert(numel(obj.intersection_)==1)
          end
        else
          obj.centers_ = varargin{1};
          obj.num_rfs_ = length(obj.centers_);
          if (optargin==2)
            if (numel(varargin{2})==1)
              obj.intersection_ = varargin{2};
            else
              obj.widths_ = varargin{2};
              assert(length(obj.centers_)==length(obj.widths_))
            end
          end
        end
      end
      
      assert(obj.num_rfs_>0);
      assert(obj.intersection_>0.0);
      assert(obj.intersection_<1.0);
    end

    %function obj = MetaParametersLWR(centers, widths)
    %  obj.intersection_ = -1;
    %  obj.centers_ = centers;
    %  obj.widths_ = widths;
    %
    %  assert(length(obj.centers_)==length(obj.widths_));
    %  obj.num_rfs_ = length(centers);
    %end

    function meta_parameters_clone = clone(obj)
      meta_parameters_clone = MetaParametersLWR(obj.num_rfs_,obj.intersection_);
      meta_parameters_clone.centers_ = obj.centers_;
      meta_parameters_clone.widths_  = obj.widths_;
    end
    
    function str = toString(obj)
      str = sprintf('%s[num_rfs=%d, intersection=%1.3f, centers=(',class(obj),obj.num_rfs_,obj.intersection_);
      str = [str sprintf('%1.6f ',obj.centers_)];
      str = [str sprintf('), widths=(')];
      str = [str sprintf('%1.6f ',obj.widths_)];
      str = [str sprintf(')]')];
    end


    function centers = getCenters(obj, min_val, max_val)
      if (~isempty(obj.centers_))
        % Centers were initialized: simply return them (and ignore min/max arguments)
        centers = obj.centers_;
      else
        % Centers were not initialized: generate them here given num_rfs_ and min/max values
        if (isscalar(min_val))
          
          % 1-D case: easy
          assert(isscalar(max_val))
          assert(isscalar(obj.num_rfs_per_dim_))
          centers = linspace(min_val, max_val, obj.num_rfs_per_dim_)';
          
        else
          
          % N-D case: more complicated...
          n_dims = length(min_val);
          if (isscalar(obj.num_rfs_per_dim_))
            num_rfs_per_dim = obj.num_rfs_per_dim_*ones(1,n_dims);
          else
            num_rfs_per_dim = obj.num_rfs_per_dim_;
          end
          assert(isequal(size(num_rfs_per_dim),size(min_val)));
          assert(isequal(size(num_rfs_per_dim),size(max_val)));
          
          
          for i_dim=1:n_dims
            centers_per_dim{i_dim} = linspace(min_val(i_dim),max_val(i_dim),num_rfs_per_dim(i_dim));
          end
          
          n_centers = prod(num_rfs_per_dim);
          centers = zeros(n_centers,n_dims);

          % nnn Document algorithm
          counter = ones(1,n_dims);
          cc = 1;
          while (counter(1)<=num_rfs_per_dim(1))
            for i_dim=1:n_dims
              centers(cc,i_dim) = centers_per_dim{i_dim}(counter(i_dim));
            end
            cc = cc+1;
  
            counter(end) = counter(end)+1;
            for i_dim=(n_dims:-1:2)
              if (counter(i_dim)>num_rfs_per_dim(i_dim))
                counter(i_dim) = 1;
                counter(i_dim-1) = counter(i_dim-1)+1;
              end
            end
          end
          
        end
      end
    end

    function widths = getWidths(obj, centers)
      widths = 0.2*ones(size(centers)); %nnn
      return

      
      if (~isempty(obj.widths_))
        % Widths were initialized: simply return them (and ignore centers argument)
        widths = obj.widths_;
      else
        % Centers were not initialized: generate them here given centers
        width = 1;
        n_centers = length(centers);
        if (n_centers>1)
          width = 0.5*(centers(2)-centers(1)); % zzz Use intersection instead
          widths = width*ones(size(centers));
        end
      end
    end
    
    function testme(obj) %#ok<INUSD>
      % Following should work
      mps(1) = MetaParametersLWR();
      mps(2) = MetaParametersLWR(5);
      mps(3) = MetaParametersLWR(5,0.5);
      mps(4) = MetaParametersLWR(linspace(0,1,5));
      mps(5) = MetaParametersLWR(linspace(0,1,5),0.5);
      mps(6) = MetaParametersLWR(linspace(0,1,5),0.2*ones(1,5));
      for ii=1:length(mps)
        mp = mps(ii);
        centers = mp.getCenters(3,4);
        widths = mp.getWidths(centers);
        disp(mp)
        disp(centers)
        disp(widths)
        pause
        
        meta_parameters_clone = mp.clone();
        disp(mp)
        disp(meta_parameters_clone)
        pause
      end
    end
    
  end
end


%       n = size(varargin,2);
%       if (n < 1), error('Available interfaces are: fa_lwr(n_basis_functions) | fa_lwr(ratio,centers) | fa_lwr(widths,centers)'); end
% 
%       if (n == 1) % fa_lwr(n_basis_functions)
%         n_basis_functions = varargin{1,1};
%         centers_in = linspace(1,0.001,n_basis_functions);
%         ratio = 0.5;
%         obj.ratio_intersection = ratio;
%         width = intersection2width(centers_in(1),centers_in(2),ratio);
%         widths_in = repmat(width,1,n_basis_functions);
%         %widths = ones(size(centers))/n_basis_functions;
%       end
% 
%       if (n == 2)
%         centers_in = varargin{1,2};
%         n_basis_functions = length(centers_in);
%         if isscalar(varargin{1,1}) % fa_lwr(ratio,centers)
%           ratio = varargin{1,1};
%           obj.ratio_intersection = ratio;
%           if (n_basis_functions > 1)
%             for ii = 1:length(centers_in)-1 % For each center
%               widths_in(ii) = obj.intersection2width(centers_in(ii),centers_in(ii+1),ratio); %#ok<PROP,PROP> Note: the centers need to be linspaced!
%             end
%             widths_in(end+1) = widths_in(end);
%           else
%             error('ERROR: n_basis_functions = 1')
%             %width = 1;
%           end
%           %widths = repmat(width,1,n_basis_functions);
%         else % fa_lwr(widths,centers)
%           widths_in = varargin{1,1};
%         end
%       end
% 

%     function width = intersection2width(obj,center1,center2,ratio)
%       %Calculate the width of two basis functions so that they intersect in a point
%       %defined using the fwhm formula.
%       % Half height: fwhm = 2*sqrt(2*log(2))*width
%       % Generic height defined by ratio: generic_fw = 2*sqrt(2*log(1/ratio))*width
% 
%       if (nargin < 1)
%         testintersection2width;
%         return
%       end
%       if (nargin < 2), error('Too few arguments'); end
%       if (nargin < 3), ratio = 1/2; end
% 
%       width = abs(center2-center1)./(2*sqrt(2*log(1/ratio)));
% 
% 
%     end

%       obj.centers = centers_in;
%       obj.widths = widths_in;
%       obj.weights = [];
%       obj.nbf = length(centers_in);
