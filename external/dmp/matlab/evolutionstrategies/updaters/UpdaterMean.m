classdef UpdaterMean < handle

  properties
    eliteness
    weighting_method
  end

  methods
    function obj = UpdaterMean(eliteness,weighting_method)
      if (nargin<1), eliteness           =      10; end
      if (nargin<2), weighting_method    = 'PI-BB';  end % {'PI-BB','CMA-ES'}

      obj.eliteness           = eliteness          ;
      obj.weighting_method    = weighting_method   ;
    end

    function [mean_new weights]  = updateDistributionMean(obj,mean,samples,costs)
      % Input:
      %   distribution - distribution from which "samples" were sampled
      %                   mean, covar, sigma, evolution paths (last two only for CMA-ES)
      %   samples       - samples from above distribution. Size:  n_dofs x n_samples x n_dims
      %   costs         - costs for each sample: 1 x n_samples
      %
      % Output:
      %   distribution_new - updated distribution
      %   summary           - structure with summary of this update
      n_dims  = length(mean);
      n_samples = size(samples,1);


      if (isvector(costs))
        total_costs = costs(:);
      else
        % First column contains total costs
        total_costs = costs(:,1);
      end

      [weights] = obj.costsToWeights(total_costs,obj.weighting_method,obj.eliteness);

      %-------------------------------------------------------------------------------
      % Compute new mean with reward-weighed averaging
      mean_new = sum(repmat(weights,1,n_dims).*samples,1);

    end

    function [distribution_new summary]  = updateDistribution(obj,distribution,samples,costs)
      % Input:
      %   distribution - distribution from which "samples" were sampled
      %                   mean, covar, sigma, evolution paths (last two only for CMA-ES)
      %   samples       - samples from above distribution. Size:  n_dofs x n_samples x n_dims
      %   costs         - costs for each sample: 1 x n_samples
      %
      % Output:
      %   distribution_new - updated distribution
      %   summary           - structure with summary of this update

      distribution_new = distribution;
      [distribution_new.mean weights] = obj.updateDistributionMean(distribution.mean,samples,costs);

      %-------------------------------------------------------------------------------
      % Bookkeeping: put relevant information in a summary
      summary.distribution = distribution;
      summary.samples = samples;
      summary.costs = costs;
      summary.weights = weights;
      summary.distribution_new = distribution_new;

    end

    function [weights] = costsToWeights(obj,costs,weighting_method,eliteness) %#ok<INUSL>
      % Convert costs to weights for reward-weighted averaging
      %  weighting_method - For reward-weighted averaging
      %  eliteness         - eliteness parameter (trust the defaults ;-)

      %-------------------------------------------------------------------------------
      % First, map the costs to the weights
      if (strcmp(weighting_method,'PI-BB'))
        % PI^2 style weighting: continuous, cost exponention
        h = eliteness; % In PI^2, eliteness parameter is known as "h"
        weights = exp(-h*((costs-min(costs))/(max(costs)-min(costs))));

      elseif (strcmp(weighting_method,'CEM') || strcmp(weighting_method,'CMA-ES'))
        % CEM/CMA-ES style weights: rank-based, uses defaults
        mu = eliteness; % In CMA-ES, eliteness parameter is known as "mu"
        [Ssorted indices] = sort(costs,'ascend');
        weights = zeros(size(costs));
        if (strcmp(weighting_method,'CEM'))
          weights(indices(1:mu)) = 1/mu;
        else
          for ii=1:mu
            weights(indices(ii)) = log(mu+1/2)-log(ii);
          end
        end

      else
        warning('Unknown weighting method %s. Setting to "PI-BB".\n',weighting_method); %#ok<WNTAG>
        % Call recursively with fixed parameter
        weighting_method = 'PI-BB';
        [weights] = obj.costsToWeights(costs,weighting_method,eliteness); %#ok<INUSL>
        return;
      end

      % Relative standard deviation of total costs
      rel_std = std(costs)/mean(costs);
      if (rel_std<1e-10)
        % Special case: all costs are the same
        % Set same weights for all.
        weights = ones(size(weights));
      end

      % Normalize weights
      weights = weights/sum(weights);
    end

    function line_handle = plotCostsToWeights(obj,costs,weighting_method,eliteness) %#ok<INUSL>
      if (nargin<3), weighting_method = obj.weighting_method; end
      if (nargin<4), eliteness = obj.eliteness; end
      if (nargin<2), costs = 1:(2*eliteness); end
      weights  = obj.costsToWeights(costs,weighting_method,eliteness);
      line_handle = plot(costs,weights,'o-b');
      set(line_handle,'MarkerFaceColor','b','MarkerEdgeColor','none');
      xlabel('Cost')
      ylabel('Weight')
    end
      
    function testcoststoweights(obj) % zzz Move to separate function
      costs = 0:20;
      weighting_method_labels = {'CEM','CMA-ES','PI-BB'};
      elitenesses = [5 10];
      legend_labels = {};
      clf
      colors = get(gcf,'DefaultAxesColorOrder');
      n_colors = size(colors,1);
      i_color = 1;
      for i_weighting_method=1:length(weighting_method_labels)
        for i_eliteness=1:length(elitenesses)
          line_handle = obj.plotCostsToWeights(costs,weighting_method_labels{i_weighting_method},elitenesses(i_eliteness));
          cur_color = colors(mod(i_color-1,n_colors)+1,:); i_color = i_color+1;
          set(line_handle,'Color',cur_color,'MarkerFaceColor',cur_color);
          hold on
          legend_labels{end+1} = sprintf('%s (%d)',weighting_method_labels{i_weighting_method},elitenesses(i_eliteness));
        end
      end
      hold off
      legend(legend_labels,'Location','NorthEast');
      set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
    end
    
    function visualizeUpdate(obj,update_summary,highlight,plot_samples,main_color) %#ok<INUSL>
      if (nargin<2), highlight=0; end
      if (nargin<3), plot_samples=0; end
      if (nargin<4), main_color=0.8*ones(1,3); end

      n_dims  = length(update_summary.distribution.mean);
      plot_n_dim = min(n_dims,2); % Plot only first D dimensions

      weights = update_summary.weights;
      n_samples = length(weights);

      %if (nargin<4), i_dofs=1:n_dofs; end

      marker_scale = 40;

      theta = update_summary.distribution.mean;
      covar = update_summary.distribution.covar;
      theta_new = update_summary.distribution_new.mean;
      covar_new = update_summary.distribution_new.covar;
      samples = squeeze(update_summary.samples);
      weights_normalized = weights/max(weights);

      axis equal
      if (plot_samples)
        for k=1:n_samples
          theta_k = samples(k,:);
          marker_size = round(marker_scale*weights_normalized(k))+3;
          if (plot_n_dim==2)
            % Green circle representing weight
            %patch(theta_k(1)+weights_normalized(k,1)*circle(:,1),theta_k(2)+weights_normalized(k,2)*circle(:,2),[0.7 1 0.7],'EdgeColor','none')
            % zzz plot(theta_k(1),theta_k(2),'o','MarkerFaceColor',[0.7 1 0.7],'MarkerEdgeColor','none','MarkerSize',marker_size);
            hold on
            % Line from current mean to theta_k
            plot([theta(1) theta_k(1)],[theta(2) theta_k(2)],'-','Color',[0.5 0.5 1.0])
            % theta_k
            plot(theta_k(1),theta_k(2),'o','MarkerFaceColor',[0.5 0.5 1.0],'MarkerEdgeColor','k')
          elseif (plot_n_dim==3)
            %warning('Cannot plot green circle representing weight in 3 dimensions') %#ok<WNTAG>
            % Line from current mean to theta_k
            plot3([theta(1) theta_k(1)],[theta(2) theta_k(2)],[theta(3) theta_k(3)],'-','Color',[0.5 0.5 1.0])
            hold on
            % theta_k
            plot3(theta_k(1),theta_k(2),theta_k(3),'o','MarkerFaceColor',[0.5 0.5 1.0],'MarkerEdgeColor','k')
          end

        end
        % Line from current to new theta
        %plot([theta(1) theta_new(1)],[theta(2) theta_new(2)],'-','Color',0*[0.5 0 1],'LineWidth',3)
      end

      xlabel('\theta_1')
      ylabel('\theta_2')
      if (plot_n_dim==2)
        h_before_theta = plot(theta(1),    theta(2)    ,'o','MarkerSize',8,'MarkerEdgeColor','none');
        hold on
        h_after_theta  = plot(theta_new(1),theta_new(2),'o','MarkerSize',8,'MarkerEdgeColor','none');
      elseif (plot_n_dim==3)
        h_before_theta = plot3(theta(1),    theta(2)    ,    theta(3),'o','MarkerSize',8,'MarkerEdgeColor','none');
        hold on
        h_after_theta  = plot3(theta_new(1),theta_new(2),theta_new(3),'o','MarkerSize',8,'MarkerEdgeColor','none');
        zlabel('\theta_3')
      end

      % Note that plotting this might lead to numerical issues because we are
      % taking a submatrix of the covariance matrix
      h_before_covar = error_ellipse(real(squeeze(covar(1:plot_n_dim,1:plot_n_dim))),theta(1:plot_n_dim),'conf',0.99);
      h_after_covar  = error_ellipse(real(squeeze(covar_new(1:plot_n_dim,1:plot_n_dim))),theta_new(1:plot_n_dim),'conf',0.99);

      if (highlight)
        set([h_before_covar h_after_covar],'LineWidth',2)
        set(h_before_theta ,'MarkerFaceColor',[0.2 0.2 0.7],'MarkerEdgeColor','k')
        set(h_after_theta ,'MarkerFaceColor',[0.9 0.2 0.2],'MarkerEdgeColor','k')
        if (plot_n_dim<4)
          set(h_before_covar,'Color',[0.2 0.2 0.7]);
          set(h_after_covar,'Color',[0.9 0.2 0.2]);
        end
      else
        if (plot_n_dim<4)
          set([h_before_covar h_after_covar],'Color',main_color,'LineWidth',1);
          set(h_before_theta ,'MarkerFaceColor',main_color,'MarkerEdgeColor','none');
        end
      end
      axis equal
      set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
    end

  end
end

