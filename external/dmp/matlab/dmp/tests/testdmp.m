function dmp = testdmp

%-------------------------------------------------------------------------------
% SETTINGS RELATED TO TIME

% Time constant
tau = 0.6;

% Time signal, e.g. 0.01, 0.02, 0.03 ... 2*tau
dt = 0.004;
ts_train = 0:dt:tau;
ts_exec  = 0:dt:1.5*tau;

%-------------------------------------------------------------------------------
% CONSTRUCT SOME DYNAMICAL SYSTEMS NECESSARY FOR THE DMP

initial_state   = [0.5 1.0 1.0]';
attractor_state = [0.8 0.1 0.1]';
dim = length(initial_state);

spring_alpha = 20;

n_dmps = 2;
n_function_approximators = 2;

i_figure = 1;
for i_dmp=1:n_dmps

  if (i_dmp==1)
    dmp_name = 'new';

    % DMPs with delayed goals, simpler phase, and sigmoid gating
    % This is how I like them ;-)
    goal_alpha = 15;
    goal_system = ExponentialSystem(tau,initial_state,attractor_state,goal_alpha);

    phase_system = TimeSystem(tau);

    gating_alpha = -40;
    gating_system = SigmoidSystem(tau,1,gating_alpha,0.75*tau);

  else
    dmp_name = 'old';

    % Standard DMP with same system for phase and gating
    goal_system = [];

    phase_alpha = 6;
    phase_system = ExponentialSystem(tau,1,0,phase_alpha);

    gating_alpha = 6;
    gating_system = ExponentialSystem(tau,1,0,gating_alpha);

  end

  %-------------------------------------------------------------------------------
  % CONSTRUCT SOME FUNCTION APPROXIMATORS FOR THE DMP

  % Initialize one LWR for each dimension
  phase_min_max = sort([phase_system.x_init phase_system.x_attr]);
  n_basis_functions = 9;
  centers = linspace(phase_system.x_init,phase_system.x_attr,n_basis_functions)';
  widths  = centers(2)-centers(1)*ones(size(centers));
  intersection_ratio = 0.5;
  randn('state', 0);
  slopes = (i_dmp*i_dmp)*[0 0 0 0 0 0 0 0 0; 0 10 20 100 -30 -120 10 10 -20; 0 0 0 0 0 0 0 0 0];
  for dd=1:dim
    meta_parameters = MetaParametersLWR(n_basis_functions);
    model_parameters = ModelParametersLWR(centers,widths,slopes(dd,:)',0*slopes(dd,:)');
    function_approximators(dd) = FunctionApproximatorLWR(meta_parameters,model_parameters);
  end

  %-------------------------------------------------------------------------------
  % CONSTRUCT THE DMP
  dmp = Dmp(tau,initial_state,attractor_state,spring_alpha,goal_system,phase_system,gating_system,function_approximators);

  % Analytical solution
  [xs_ana xds_ana]= dmp.analyticalSolution(ts_exec);

  %-----------------------------------------------------------------------------
  % INTEGRATE STEP BY STEP

  % Now start and integrate system
  % This is where we will store the states over time
  xs_step = zeros(length(ts_exec),size(xs_ana,2));
  xds_step = zeros(length(ts_exec),size(xs_ana,2));
  
  [xs_step(1,:) xds_step(1,:)] = dmp.integrateStart(); % Start integrating
  for tt=2:length(ts_exec)
    [xs_step(tt,:) xds_step(tt,:)] = dmp.integrateStep(dt,xs_step(tt-1,:)'); % Integration
  end

  %-----------------------------------------------------------------------------
  % PLOTTING (USING Dmp::plotStateVectors)
  figure(i_figure);
  i_figure = i_figure + 1;
  clf

  [ axis_handles_analytical line_handles_analytical] = dmp.plotStates(ts_exec,xs_ana,xds_ana);
  set(line_handles_analytical,'LineWidth',3)
  set(line_handles_analytical,'Color',[0.8 0.8 1])

  for aa=1:length(axis_handles_analytical)
    set(axis_handles_analytical,'NextPlot','add');
  end

  [ axis_handles_step line_handles_step ] = dmp.plotStates(ts_exec,xs_step,xds_step);
  set(line_handles_step,'LineStyle','--')
  set(line_handles_step,'LineWidth',2)
  set(line_handles_step,'Color',[0.3 0.3 0.6])

  legend_lines = [ line_handles_analytical(1) line_handles_step(1)];
  legend_labels = {'ana (Mat)','int (Mat)'};

  do_cpp = 0;
  if (do_cpp &&  strcmp(dmp_name,'new'))

    filename_cpp_step = '/tmp/data_cpp_step.txt';
    filename_cpp_ana  = '/tmp/data_cpp_ana.txt';
    system(['cd ../cpp/tests/dmp; testDmp ' filename_cpp_ana ' ' filename_cpp_step]);

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

    legend_labels{end+1} = 'int (C++)';
    legend_labels{end+1} = 'ana (C++)';
    legend_lines(end+1) = line_handles_step_cpp(1);
    legend_lines(end+1) = line_handles_ana_cpp(1);
  end

  for aa=1:length(axis_handles_analytical)
    subplot(axis_handles_step(aa))
    y_limits_exec = ylim;
    hold on
    plot([tau tau],y_limits_exec,'-k')
    hold off
  end
  legend(legend_lines,legend_labels,'Location','East')

  set(gcf,'Name',sprintf('%s (compare analytical and integration)',dmp_name))


  drawnow
  
end

end
