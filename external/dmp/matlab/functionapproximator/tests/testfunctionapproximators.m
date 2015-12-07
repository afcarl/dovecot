n_samples=100;

for input_dim=1:2

  % Generate some input and target data
  % Do "doc meshgrid" to see the function
  if (input_dim==1)
    inputs = -2 + 4*rand(n_samples,1);
    inputs = sort(inputs);
    targets = inputs.* exp(-inputs.^2);
  else
    inputs = -2 + 4*rand(2*n_samples,2);
    targets = inputs(:,1).* exp(-inputs(:,1).^2 - inputs(:,2).^2);
  end
  
  % Make some function approximators

  % LWR
  function_approximators = {};
  n_centers = 9;
  meta_parameters = MetaParametersLWR(n_centers);
  function_approximators{end+1} = FunctionApproximatorLWR(meta_parameters);
  
  % LWPR
  init_D = 200*eye(input_dim); 
  w_gen = 0.2;
  w_prune = 0.8;
  update_D = 1;
  init_alpha = 0.1;
  penalty = 0.0001;
  diag_only = 1;
  meta_parameters_lwpr = MetaParametersLWPR(init_D, w_gen, w_prune,...
        update_D, init_alpha, penalty, diag_only);      
  function_approximators{end+1} = FunctionApproximatorLWPR(meta_parameters_lwpr);
  
  % GPR
  covar = 1;
  meta_parameters_gpr = MetaParametersGPR(covar);
  function_approximators{end+1} = FunctionApproximatorGPR(meta_parameters_gpr);
  

  % Train and visualize all function approximators
  for ff=1:length(function_approximators)

    fprintf('Training function approximator "%s".\n',class(function_approximators{ff}))
    function_approximators{ff} = function_approximators{ff}.train(inputs,targets);
    
    figure(10*input_dim + ff)
    set(gcf,'Name',class(function_approximators{ff}))
    subplot(1,2,1)
    function_approximators{ff}.visualizegridpredictions(gca,[1 0 1],100/input_dim.^2);
    subplot(1,2,2)
    function_approximators{ff}.visualizegridpredictions(gca,[0 1 0],100/input_dim.^2);
    drawnow
  end
  
end