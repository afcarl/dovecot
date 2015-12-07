function dmp = testdmptrain


%-------------------------------------------------------------------------------
% MAIN SETTINGS

% Time constant
tau = 0.6;

% Time signal, e.g. 0.01, 0.02, 0.03 ... 2*tau
dt = 0.004;
ts_train = 0:dt:tau;
ts_exec  = 0:dt:1.5*tau;

dim = 3;

%-------------------------------------------------------------------------------
% GENERATE SOME DATA

x   = zeros(length(ts_train),dim);
xd  = zeros(length(ts_train),dim);
xdd = zeros(length(ts_train),dim);


sigma = 0.10;
tbump = 0.5*tau;
bump = exp((-0.5/(sigma.^2)) * (ts_train - tbump).^2);
bump_small = exp((-0.5/((sigma/1.5).^2)) * (ts_train - tbump).^2);

for dd=1:dim
  x(1,dd) = 0.05*dd;
  v = 0.2*dd*(bump'-1.2*(dd-1)*bump_small');
  for tt=2:length(ts_train)
    x(tt,dd) = x(tt-1,dd) + dt*v(tt);
  end
  xd(:,dd)  = diffnc(x(:,dd),dt);
  xdd(:,dd) = diffnc(xd(:,dd),dt);
end

output_dir = '/tmp/';
save([output_dir 'demo_ts.txt'],'ts_train','-ascii');
save([output_dir 'demo_xs.txt'],'x','-ascii');
save([output_dir 'demo_xds.txt'],'xd','-ascii');
save([output_dir 'demo_xdds.txt'],'xdd','-ascii');

if (0)
  subplot(1,3,1)
  plot(ts_train,x)
  subplot(1,3,2)
  plot(ts_train,xd)
  subplot(1,3,3)
  plot(ts_train,xdd)
end


%-----------------------------------------------------------------------------
% CONSTRUCT SOME UNTRAINED FUNCTION APPROXIMATORS FOR THE DMP
all_function_approximators = {};

% LWR
n_basis_functions = 15;
meta_parameters_lwr = MetaParametersLWR(n_basis_functions);

% LWPR
init_D = 1000;
w_gen = 0.1;
w_prune = 0.8;
update_D = 1;
init_alpha = 0.00001;
penalty = 0.001;
meta_parameters_lwpr = MetaParametersLWPR(init_D, w_gen, w_prune, update_D, init_alpha, penalty);

% GPR
covar = 1;
meta_parameters_gpr = MetaParametersGPR(covar);


for dd=1:dim
  function_approximators_lwr(dd) = FunctionApproximatorLWR(meta_parameters_lwr);
  function_approximators_lwpr(dd) = FunctionApproximatorLWPR(meta_parameters_lwpr);
  function_approximators_gpr(dd) = FunctionApproximatorGPR(meta_parameters_gpr);
end

all_function_approximators{end+1} = function_approximators_lwr;
all_function_approximators{end+1} = function_approximators_lwpr;
%all_function_approximators{end+1} = function_approximators_gpr; % zzz Fix this


n_function_approximators = length(all_function_approximators);
i_figure = 1;
for ff=1:n_function_approximators

  % Get current fa from the list
  function_approximators = all_function_approximators{ff};

  %-------------------------------------------------------------------------------
  % INITIALIZE AND TRAIN THE DMP
  x_init = zeros(dim,1);
  x_attr = ones(dim,1);
  dmp_type = 'KULVICIUS_2012_JOINING';
  dmp = constructDmp(tau, x_init, x_attr, dmp_type, function_approximators);
  dmp = dmp.train(ts_train,x,xd,xdd,i_figure);

  figure(i_figure+1)
  set(gcf,'Name',sprintf('fa=%s',class(dmp.function_approximators(1))))
  drawnow
  figure(i_figure)
  set(gcf,'Name',sprintf('DMP trained with fa=%s',class(dmp.function_approximators(1))))

  if (ff==1)
    filename_cpp_step = '/tmp/testDmpTrain/cpp_repro_step.txt';
    filename_cpp_ana  = '/tmp/testDmpTrain/cpp_repro_ana.txt';
    command = ['cd ../cpp/tests/dmp; testDmpTrain ' filename_cpp_ana ' ' filename_cpp_step];
    system(command);

    if (~exist(filename_cpp_step,'file'))
      warning(['Something went wrong when calling "' command '" because file "' filename_cpp_step '" is not there.']) %#ok<WNTAG>
    else
      data_step_cpp = load(filename_cpp_step);
      dim_cpp = (size(data_step_cpp,2)-1)/2;
      ts_step_cpp = data_step_cpp(:,end);
      xs_step_cpp = data_step_cpp(:,1:dim_cpp);
      xds_step_cpp = data_step_cpp(:,(dim_cpp+1):end);

      data_ana_cpp = load(filename_cpp_ana);
      ts_ana_cpp = data_ana_cpp(:,end);
      xs_ana_cpp = data_ana_cpp(:,1:dim_cpp);
      xds_ana_cpp = data_ana_cpp(:,(dim_cpp+1):end);

      [ axis_handles_step_cpp line_handles_step_cpp ] = dmp.plotStates(ts_step_cpp,xs_step_cpp,xds_step_cpp);
      [ axis_handles_ana_cpp line_handles_ana_cpp ] = dmp.plotStates(ts_ana_cpp,xs_ana_cpp,xds_ana_cpp);

      set(line_handles_step_cpp,'LineStyle','-')
      set(line_handles_step_cpp,'LineWidth',1)
      set(line_handles_step_cpp,'Color',0*[0.6 0.3 0.3])

      set(line_handles_ana_cpp,'LineStyle','--')
      set(line_handles_ana_cpp,'LineWidth',1)
      set(line_handles_ana_cpp,'Color',[0.8 0.3 0.3])
    end
  end

  drawnow



  i_figure = i_figure + 2;

end

end
