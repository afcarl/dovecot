import numpy as np
import libpydmp as pydmp


class DMP(object):

    def __init__(self):
        self.dmp = pydmp.PyDMP(1)
        duration = 2.0

        self.dmp.set_timesteps(int(120*duration), 0.0, duration)
        self.dmp.set_initial_state([0.0])
        self.dmp.set_attractor_state([1.0])

        self.centers = None
        self.widths  = None
        self.slopes  = None
        self.offsets = None

        self.lwr_meta_params(1, 0.1)

    def trajectory(self):
        traj = self.dmp.generate_trajectory()
        return traj[::3], traj[1::3], traj[2::3] 

    def lwr_meta_params(self, n_bases, overlap=0.1):
        self.n_bases = n_bases
        self.dmp.set_lwr_meta_parameters(1, n_bases, overlap)

        self.centers = list(np.linspace(0.0, 1.0, num=n_bases+2))[1:-1]
        self.widths  = [1.0/n_bases + 2*overlap]*n_bases
        self.slopes  = [0.0]*n_bases
        self.offsets = [0.0]*n_bases

        self.dmp.set_lwr_model_parameters(self.centers, self.widths, self.slopes, self.offsets)

    def lwr_model_params(self, centers = None, widths = None,
                               slopes = None, offsets = None):
        assert self.centers is not None, "you must set lwr_meta_parameters before set_lwr_model_parameters."
        self.centers = centers or self.centers
        self.widths  = widths  or self.widths
        self.slopes  = slopes  or self.slopes
        self.offsets = offsets or self.offsets

        assert self.n_bases == len(self.centers) == len(self.widths) == len(self.slopes) == len(self.offsets)
        self.dmp.set_lwr_model_parameters(list(self.centers), list(self.widths), 
                                          list(self.slopes), list(self.offsets))




if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    def plot_dmp(dmp):
        ts, xs, xds = dmp.trajectory()
        
        fig = matplotlib.figure.Figure()
        fig.canvas = FigureCanvas(fig)

        xs_color  = (250/255.0,105/255.0,  0/255.0)
        xds_color = (105/255.0,210/255.0,231/255.0)

        subplot = fig.add_subplot(1, 1, 1, axisbg=(1.0, 1.0, 1.0))
        subplot.set_title('slopes:{} offsets:{}'.format(dmp.slopes, dmp.offsets))
        subplot.plot(ts, xs,  color=xs_color)
        for tl in subplot.get_yticklabels():
            tl.set_color(xs_color)
        subplot.set_ylabel('position', color=xs_color)
        
        subplot2 = subplot.twinx()
        subplot2.plot(ts, xds, color=xds_color)
        for tl in subplot2.get_yticklabels():
            tl.set_color(xds_color)

        subplot2.set_ylabel('speed', color=xds_color)

        filename = './dmp{}{}{}{}.png'.format(dmp.slopes, dmp.offsets, dmp.centers, dmp.widths)
        fig.savefig(filename, dpi=300, format='png', 
                              facecolor=(1.0, 1.0, 1.0))
        print('graph saved in {}'.format(filename))


    # for slope1 in range(-5, 6):
    #     for slope2 in range(-5, 6):

    #         dmp = DMP()
    #         dmp.lwr_meta_params(2)
    #         dmp.lwr_model_params(slopes = [slope1*20.0, slope2*20.0], offsets = [0.0, 0.0], centers = [0.0, 0.5])        
    #         plot_dmp(dmp)

    # for slope in range(21):

    #     dmp = DMP()
    #     dmp.lwr_model_params(slopes = [slope*-10.0], offsets = [0.0], centers =[0.0])        
    #     plot_dmp(dmp)

    dmp = DMP()
    dmp.dmp.set_attractor_state([0.0])
    #dmp.lwr_meta_params(2)
    #dmp.lwr_model_params(slopes = [0.0, -500.0], offsets = [-500.0, 0.0], centers = [0.0, 0.5], widths = [1.0, 1.0])        
    dmp.lwr_meta_params(1)
    dmp.lwr_model_params(slopes = [0.0], offsets = [-500.0], centers = [0.5], widths = [1.0])        
    plot_dmp(dmp)
