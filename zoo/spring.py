import math

k   = 10000.0             # spring constant
dt  = 0.01              # in s  
m   = 400.0             # unit ?
dur = int(10.0/dt)      # 10 s
c   = -2*math.sqrt(m*k) # critical damping

def springForce(m, a, b):
    x_a, y_a, z_a = a
    x_b, y_b, z_b = b

    d_ab = dist(a,b)
    f = k * dist(a, b)
    f_x = f * dist(a_x, b_x)/d_ab
    f_y = f * dist(a_y, b_y)/d_ab
    f_z = f * dist(a_z, b_z)/d_ab

    return f_x, f_y, f_z

def dampenedSpringForce(a, b, a_old, b_old):
    a_x, a_y, a_z = a
    b_x, b_y, b_z = b

    a_x_old, a_y_old, a_z_old = a_old
    b_x_old, b_y_old, b_z_old = b_old

    d_x = (a_x - b_x)
    d_y = (a_y - b_y)
    d_z = (a_z - b_z)

    d_x_old = (a_x_old - b_x_old)
    d_y_old = (a_y_old - b_y_old)
    d_z_old = (a_z_old - b_z_old)

    f_x = k * d_x - (c * (d_x - d_x_old)/dt)
    f_y = k * d_y - (c * (d_y - d_y_old)/dt)
    f_z = k * d_z - (c * (d_z - d_z_old)/dt)

    return -f_x, -f_y, -f_z

def step(m, a, v_a, f):
    f_x, f_y, f_z = f
    acc_x = f_x/m
    acc_y = f_y/m
    acc_z = f_z/m

    v_x, v_y, v_z = v_a
    v_x += acc_x * dt
    v_y += acc_y * dt
    v_z += acc_z * dt

    a_x, a_y, a_z = a
    a_x += v_x * dt
    a_y += v_y * dt
    a_z += v_z * dt

    return (a_x, a_y, a_z), (v_x, v_y, v_z)

if __name__ == "__main__":

    a = 0.0, 0.0, 0.0
    b = 1.0, -1.0, 5.0
    a_old = 0.0, 0.0, 0.0
    b_old = 1.0, -1.0, 5.0

    v_a = 0.0, 0.0, 0.0

    traj_a = []
    for t in range(dur):
        f_a = dampenedSpringForce(a, b, a_old, b_old)
        traj_a.append(a)
        a_old = a
        b_old = b
        a, v_a = step(m, a, v_a, f_a)
        #print("{:5.2f} {:5.2f} {:5.2f}".format(*a))

    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    def plot_traj(traj):
        
        fig = matplotlib.figure.Figure()
        fig.canvas = FigureCanvas(fig)

        subplot = fig.add_subplot(1, 1, 1, axisbg=(1.0, 1.0, 1.0))
        subplot.plot(range(dur), [traj_i[0] for traj_i in traj], color = (1.0, 0.0, 0.0))
        subplot.plot(range(dur), [traj_i[1] for traj_i in traj], color = (0.0, 1.0, 0.0))
        subplot.plot(range(dur), [traj_i[2] for traj_i in traj], color = (0.0, 0.0, 1.0))
        filename = './traj.png'
        fig.savefig(filename, dpi=300, format='png', 
                              facecolor=(1.0, 1.0, 1.0))
        print('graph saved in {}'.format(filename))

    plot_traj(traj_a)