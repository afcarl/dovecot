classdef MetaParametersLWPR

  properties
    init_D_
    w_gen_
    w_prune_
    update_D_
    init_alpha_
    penalty_
    diag_only_
    use_meta_
    meta_rate_
    kernel_name_
  end

  methods
    function obj = MetaParametersLWPR(...
        init_D, w_gen, w_prune,...
        update_D, init_alpha, penalty, diag_only,...
        use_meta, meta_rate, kernel_name)

      % Placing  kernels
      %   Tune these parameters first with update_D = 0
      if (nargin< 1), init_D=1; end
      if (nargin< 2), w_gen=0.2; end
      if (nargin< 3), w_prune=0.8; end;

      % Updating existing kernels
      %   Set diag_only=1 when it works well with the other parameters
      if (nargin< 4), update_D=true; end
      if (nargin< 5), init_alpha=1.0; end
      if (nargin< 6), penalty=1.0; end
      if (nargin< 7), diag_only=true; end

      % Updating the updating of kernels
      %   I usually keep my hands off of this ;-)
      if (nargin< 8), use_meta=false; end
      if (nargin< 9), meta_rate=1.0; end
      if (nargin<10), kernel_name='Gaussian'; end;

      obj.init_D_ = init_D; obj.w_gen_ = w_gen; obj.w_prune_ = w_prune;
      obj.update_D_ = update_D; obj.init_alpha_ = init_alpha; obj.penalty_ = penalty; obj.diag_only_ = diag_only;
      obj.use_meta_ = use_meta; obj.meta_rate_ = meta_rate; obj.kernel_name_ = kernel_name;

      assert(obj.w_gen_>0.0 && obj.w_gen_<1.0);
      assert(obj.w_prune_>0.0 && obj.w_prune_<1.0);
      assert(obj.w_gen_<obj.w_prune_);
    end


    function meta_parameters_clone = clone(obj)
      meta_parameters_clone = MetaParametersLWPR(...
        obj.init_D_, obj.w_gen_, obj.w_prune_,...
        obj.update_D_, obj.init_alpha_, obj.penalty_, obj.diag_only_,...
        obj.use_meta_, obj.meta_rate_, obj.kernel_name_);
    end
  end
end
