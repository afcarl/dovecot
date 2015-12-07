function testdynamicalsystem(test_names,dyn_sys,dt)
addpath ../matlab/dynamicalsystems/
if (nargin<1), test_names = {'rungekutta','tau','attractor','perturb','euler'}; end
if (nargin<2), dyn_sys = ExponentialSystem(0.6,[1 0.2],[0.5 0.8],6); end
if (nargin<3), dt = 0.004; end

disp(dyn_sys.toString())

figure_handle = gcf;

n_colors = dyn_sys.dim;
colormap(ones(n_colors,3));
colors = colormap(jet);
colors_hsv = rgb2hsv(colors);
colors_hsv(:,2) = 0.3;
colors_faded = hsv2rgb(colors_hsv); %#ok<NASGU>
colors_hsv(:,3) = 0.8;
colors = 0.7*hsv2rgb(colors_hsv); %#ok<NASGU>
%colors = get(gcf,'DefaultAxesColorOrder')

initial_state   = [0.5 1.0]'; % zzz pass as arg
attractor_state = [0.8 0.1]'; 

n_tests = length(test_names);
for i_test = 1:n_tests;
  if (strcmp('TimeSystem',class(dyn_sys)))
    % Cannot set states for time system. Do not set to avoid warnings.
  else
    dyn_sys.setInitialState(initial_state);
    dyn_sys.setAttractorState(attractor_state);
  end
  
  cur_test = test_names{i_test};

  tau = dyn_sys.tau;
  ts = 0:dt:2*tau;
  if (strcmp('tau',cur_test))
    dyn_sys.setTau(tau*1.5);
  end
  
  if (strcmp('euler',cur_test))
    dyn_sys.use_runge_kutta = 0;
  end
  
  % Analytical solution
  [xs_ana xds_ana] = dyn_sys.analyticalSolution(ts);
  
  
  % Reset the dynamical system, and get the first state
  [x xd] = dyn_sys.integrateStart();

  xs_step  = zeros(length(ts),length(x));
  xds_step = zeros(length(ts),length(xd));
  xs_step(1,:) = x;
  xds_step(1,:) = xd;

  % Integration
  for tt=2:length(ts)

    if (strcmp('attractor',cur_test) && (tt==ceil(length(ts)/3)))
      % Change the attractor state at t = T/3
      attractor_state = attractor_state+0.1;
    end

    if (strcmp('TimeSystem',class(dyn_sys)) || strcmp('SigmoidSystem',class(dyn_sys)))
      % Attractor state of Time/SigmoidSystem may not be set.
    else
      dyn_sys = dyn_sys.setAttractorState(attractor_state);      
    end
    [x xd] = dyn_sys.integrateStep(dt,xs_step(tt-1,:)');
    xs_step(tt,:) = x;
    if (strcmp('perturb',cur_test) && (tt==ceil(length(ts)/3)))
      % Perturb the state at t = T/3
      xs_step(tt,:) = xs_step(tt,:) - 0.25;
    end
    xds_step(tt,:) = xd;
  end

  do_cpp = 0;
  delete_tmp_files = 0;
  ts_ana_cpp  = [];
  ts_step_cpp = [];
  if (do_cpp && (strcmp(cur_test,'rungekutta') || strcmp(cur_test,'tau')))
    %input_filename = '/tmp/tmp_testsettings.txt';
    output_analytical_filename = '/tmp/tmp_analytical.txt';
    output_step_filename = '/tmp/tmp_step.txt';

    %fid = fopen(input_filename,'w');
    %fprintf(fid,dyn_sys.toString());
    %fprintf(fid,'\ndt=%1.5f, T=%d\n',dt,length(ts));
    %fclose(fid);

    system_command = sprintf('../cpp/tests/dynamicalsystems/testDynamicalSystem --name %s %s %s',class(dyn_sys),output_analytical_filename,output_step_filename);
    fprintf('Matlab:\n');
    fprintf('  dyn_sys: %s\n',dyn_sys.toString());
    fprintf('  dt: %f\n',dt);
    fprintf('  T: %d\n',length(ts));
    fprintf('\nC++:\n');
    system(system_command);
    if (delete_tmp_files)
      delete(input_filename);
    end
    

    if (exist(output_analytical_filename,'file'))
      data_ana = load(output_analytical_filename);
      dim_cpp = (size(data_ana,2)-1)/2;
      ts_ana_cpp = data_ana(:,end);
      xs_ana_cpp = data_ana(:,1:dim_cpp);
      xds_ana_cpp = data_ana(:,(dim_cpp+1):(2*dim_cpp));
      if (delete_tmp_files)
        delete(output_analytical_filename);
      end
    else
      warning('Something went wrong when calling C++ executable. File "%s" not written.',output_analytical_filename) %#ok<WNTAG>
    end

    if (exist(output_step_filename,'file'))
      data_step = load(output_step_filename);
      dim_cpp = (size(data_step,2)-1)/2;
      ts_step_cpp = data_step(:,end);
      xs_step_cpp = data_step(:,1:dim_cpp);
      xds_step_cpp = data_step(:,(dim_cpp+1):(2*dim_cpp));
      if (delete_tmp_files)
        delete(output_step_filename);
      end
    else
      warning('Something went wrong when calling C++ executable. File "%s" not written.',output_step_filename) %#ok<WNTAG>
    end

  end

  % Plotting
  figure(figure_handle)
  figure_handle = figure_handle+1;
  clf
  set(gcf,'Name',sprintf('%s (%s)',class(dyn_sys),cur_test))

  for do_diff = 0:1
    n_rows = 2;
    if (~isempty(ts_ana_cpp))
      n_rows = 3;
    end
     
    axis_handles(1) = subplot(n_rows,3,1+do_diff*3);
    axis_handles(2) = subplot(n_rows,3,2+do_diff*3);    
    if (dyn_sys.order_orig==2)
      axis_handles(3) = subplot(n_rows,3,3+do_diff*3);
    end

    line_handles_analytical = dyn_sys.plotStates(axis_handles,ts,xs_ana,xds_ana);
    line_handles_step       = dyn_sys.plotStates(axis_handles,ts,xs_step,xds_step);
    
    if (~isempty(ts_ana_cpp))
      axis_handles(1) = subplot(n_rows,3,1+do_diff*6);
      axis_handles(2) = subplot(n_rows,3,2+do_diff*6);
      if (dyn_sys.order_orig==2)
        axis_handles(3) = subplot(n_rows,3,3+do_diff*6);
      end
      line_handles_analytical_cpp = dyn_sys.plotStates(axis_handles,ts_ana_cpp,xs_ana_cpp,xds_ana_cpp);
      line_handles_step_cpp       = dyn_sys.plotStates(axis_handles,ts_step_cpp,xs_step_cpp,xds_step_cpp);
    end
    

    for i_dim=1:size(line_handles_analytical,2)
      set(line_handles_analytical(:,i_dim),'LineWidth',6,'Color',colors_faded(i_dim,:))
      set(line_handles_step(:,i_dim),'LineStyle','--','LineWidth',4,'Color',colors(i_dim,:))
      if (~isempty(ts_ana_cpp))
        set(line_handles_analytical_cpp,'LineWidth',1,'Color',0.5*colors_faded(i_dim,:))
      end
      if (~isempty(ts_step_cpp))
        set(line_handles_step_cpp,'LineWidth',1,'Color',0.1*colors_faded(i_dim,:),'LineStyle','--')
      end
    end


    % Compute difference on the second round
    xs_diff_cpp = [];
    if (~isempty(ts_ana_cpp))
      if (~isempty(ts_step_cpp))
        xs_diff_cpp = xs_ana_cpp - xs_step_cpp;
        xds_diff_cpp = xds_ana_cpp - xds_step_cpp;
      end
      xs_ana_cpp = xs_ana_cpp - xs_ana;
      xds_ana_cpp = xds_ana_cpp - xds_ana;
    end
    if (~isempty(ts_step_cpp))
      xs_step_cpp = xs_step_cpp - xs_step;
      xds_step_cpp = xds_step_cpp - xds_step;
    end
    xs_step  = xs_step - xs_ana;
    xds_step = xds_step - xds_ana;
    xs_ana  = xs_ana  - xs_ana;  % 0! yipee!
    xds_ana = xds_ana - xds_ana; % 0! yipee!
    
    if (do_diff==0 &&  ( strcmp('rungekutta',cur_test) || strcmp('euler',cur_test) ) )
      [y yd ydd] = dyn_sys.getOutput(xs_step,xds_step);
      disp(['  => diffs between analytical solution and numerical integration (Matlab) : '...
      num2str(max(max(y)))...
      ' and '...
      num2str(max(max(yd)))...
      ' (' cur_test ')']);
      if (~isempty(ts_ana_cpp))
        [y yd ydd] = dyn_sys.getOutput(xs_ana_cpp,xds_ana_cpp);
        disp(['  => diffs between analytical solution in Matlab and C++                  : '...
          num2str(max(max(y)))...
          ' and '...
          num2str(max(max(yd)))...
          ' (' cur_test ')']);
      end
      if (~isempty(ts_step_cpp))
        [y yd ydd] = dyn_sys.getOutput(xs_step_cpp,xds_step_cpp);
        disp(['  => diffs between numerical integration in Matlab and C++                : '...
          num2str(max(max(y)))...
          ' and '...
          num2str(max(max(yd)))...
          ' (' cur_test ')']);
      end
      if (~isempty(xs_diff_cpp))
        [y yd ydd] = dyn_sys.getOutput(xs_diff_cpp,xds_diff_cpp);
        disp(['  => diffs between analytical solution and numerical integration (C++)    : '...
          num2str(max(max(y)))...
          ' and '...
          num2str(max(max(yd)))...
          ' (' cur_test ') 0 values mostly due to saving both to file with limited precision']);
      end
    end
    

    for axis_handle=axis_handles
      subplot(axis_handle)

      axis tight
      ylimits = ylim;
      ylimits = [ylimits(1)-0.1*range(ylimits) ylimits(2)+0.1*range(ylimits)];
      ylim(ylimits)
      plot([tau tau],ylimits,'-','LineWidth',1,'Color',[0 0 0])
      text(tau,mean(ylimits),'$\tau$','Interpreter','latex')
      hold off

      % The golden ratio is very accomodating to the eye
      set(gca,'PlotBoxAspectRatio',[1.618 1 1] )

      %cur_title = cur_test;
      %if (do_diff)
      %  cur_title = [cur_title ' (diff)'];
      %end
      %title(cur_title)
    end
  end
  legend_lines = [ line_handles_analytical(1) line_handles_step(1)];
  legend_labels = {'ana (Mat)','int (Mat)'};
  if (~isempty(ts_ana_cpp))
    legend_labels{end+1} = 'ana (C++)';
    legend_lines(end+1) = line_handles_analytical_cpp(1);
  end
  if (~isempty(ts_step_cpp))
    legend_labels{end+1} = 'int (C++)';
    legend_lines(end+1) = line_handles_step_cpp(1);
  end
  legend(legend_lines,legend_labels,'Location','East')
end

end
