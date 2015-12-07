classdef TaskViapoint < Task

  properties(Access='public')
    viapoint_
    viapoint_time_
  end

  methods

    function [obj] = TaskViapoint(viapoint,viapoint_time)
      if (nargin<1), viapoint  = [0.4 0.7]; end
      if (nargin<2), viapoint_time = 0.5; end
      
      obj.viapoint_ = viapoint;
      obj.viapoint_time_ = viapoint_time;
      
    end
  end
  
  methods(Static)
    function task = fromStringSubclass(str)
      % TaskViapoint[viapoint=2 3, viapoint_time=0.3]
      
      token = regexp(str,'viapoint=(.+),','tokens');
      % tokens{1} is for instance '2 3'
      viapoint = sscanf(char(token{1}),'%f');
      
      token = regexp(str,'viapoint_time=(.+)]','tokens');
      viapoint_time = str2double(char(token{1}));
      
      task = TaskViapoint(viapoint,viapoint_time);
    end
  end
    
  methods
    function cost_vars_per_time = reshapeCostVars(obj,cost_vars,n_dims_dmp)
      [n_rollouts n_time_steps_times_n_cost_vars ] = size(cost_vars); %#ok<NASGU>
      n_cost_vars = 3*n_dims_dmp + 1;
      n_time_steps = n_time_steps_times_n_cost_vars/n_cost_vars;
      
      cost_vars_per_time = zeros(n_rollouts, n_time_steps, n_cost_vars);
      for k=1:n_rollouts
        cost_vars_per_time(k,:,:) = reshape(cost_vars(k,:),n_cost_vars,n_time_steps)';
      end
    end
    
    function costs = costFunction(obj,cost_vars)
    
      n_dims_dmp = length(obj.viapoint_);
      cost_vars_per_time = obj.reshapeCostVars(cost_vars,n_dims_dmp);
      [n_rollouts n_time_steps n_cost_vars ] = size(cost_vars_per_time);
      
      ts = zeros(n_time_steps,1);
      ys = zeros(n_time_steps,n_dims_dmp);
      ydds = zeros(n_time_steps,n_dims_dmp);
      for k=1:n_rollouts
        
        ys(:,:)   = squeeze(cost_vars_per_time(k,:,((0*n_dims_dmp)+1):(1*n_dims_dmp)));
        ydds(:,:) = squeeze(cost_vars_per_time(k,:,((2*n_dims_dmp)+1):(3*n_dims_dmp)));
        ts(:,:) = squeeze(cost_vars_per_time(k,:,end));
        
        viapoint_time_step = find(ts>=obj.viapoint_time_,1);

        %ys(viapoint_time_step,:)
        %obj.viapoint_'
        dist_to_viapoint = sqrt(sum((ys(viapoint_time_step,:)'-obj.viapoint_).^2));
        costs(k,2) = dist_to_viapoint;
        
        % Cost due to acceleration
        sum_ydd = sum((sum(ydds.^2,2)));
        costs(k,3) = 0.0001*sum_ydd/n_time_steps;
        
        % Total cost is the sum of all the subcomponent costs
        costs(k,1) = sum(costs(k,2:end));
      end

    end

    function line_handles = plotRollouts(obj,cost_vars,axes_handle)

      n_dims_dmp = length(obj.viapoint_);
      cost_vars_per_time = obj.reshapeCostVars(cost_vars,n_dims_dmp);
      [n_rollouts n_time_steps n_cost_vars ] = size(cost_vars_per_time);
      

      ts = squeeze(cost_vars_per_time(:,:,end)); % Time
      
      if (n_dims_dmp==3)
        x = squeeze(cost_vars_per_time(:,:,1));
        y = squeeze(cost_vars_per_time(:,:,2));
        z = squeeze(cost_vars_per_time(:,:,3));
        cla
        plot3(x',y',z','-k')
        hold on
        plot3(x(:,1)',y(:,1)',z(:,1)','og')
        plot3(x(:,end)',y(:,end)',z(:,end)','or')
        
        k = 1;
        viapoint_time_step = find(ts(k,:)>=obj.viapoint_time_,1);
        my_ones = ones(size(x(:,viapoint_time_step)));
        linewidth = 1;
        via = obj.viapoint_;
        plot3([ x(:,viapoint_time_step) via(1)*my_ones]' ,[y(:,viapoint_time_step) via(2)*my_ones]' ,[z(:,viapoint_time_step) via(3)*my_ones]','Color',0.7*ones(1,3),'LineWidth',linewidth);
        
        hold off
        axis equal
        return
      end
      
      
      if (n_dims_dmp==1)
        x = ts; % Time;
        y = squeeze(cost_vars_per_time(:,:,1));   
        x_via = obj.viapoint_time_;
        y_via = obj.viapoint_(1);

      elseif (n_dims_dmp==2)
        x = squeeze(cost_vars_per_time(:,:,1));
        y = squeeze(cost_vars_per_time(:,:,2));
        x_via = obj.viapoint_(1);
        y_via = obj.viapoint_(2);

      else
        warning('Only know how to plot rollouts for viapoint task when n_dim<4, but n_dim==%d',n_dims_dmp); %#ok<WNTAG>
        return;
      end
      
      color = 0.8*ones(1,3);
      linewidth = 1;

      % Draw trajectory
      line_handles(1,:) =  plot(x',y','-','Color',color,'LineWidth',linewidth);
      hold on
      % Draw line from trajectory to viapoint
      if (n_dims_dmp==2)
        % Get viapoint time step; assumes that it is the same for all rollouts
        k = 1;
        viapoint_time_step = find(ts(k,:)>=obj.viapoint_time_,1);
        my_ones = ones(size(x(:,viapoint_time_step)));
        linewidth = 1;
        line_handles(2,:) = plot([ x(:,viapoint_time_step) x_via*my_ones]' ,[y(:,viapoint_time_step) y_via*my_ones]','Color',0.7*color,'LineWidth',linewidth);
      end
      % Highlight position along trajectory at viapoint_time_step
      %line_handles(3,:) =  plot(x(:,viapoint_time_step),y(:,viapoint_time_step),'o','Color',color,'LineWidth',linewidth);

      % Plot viapoint
      plot(x_via,y_via,'o','MarkerFaceColor',[0.6 0.9 0.6],'MarkerSize',8,'MarkerEdgeColor',0.5*[1 1 1]);
      hold off

      if (n_dims_dmp==1)
        xlabel('t (s)')
        ylabel('y_1')
      else
        xlabel('y_1')
        ylabel('y_2')
      end
      

      axis square
      axis tight
    end

  end
end
