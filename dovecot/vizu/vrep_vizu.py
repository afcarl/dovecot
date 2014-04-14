from ..vrepsim import vrepcom

class VizuVrep(VRepCom):

    def show_collide_data(self, datas):
    	for data in datas:
			col = data['datas']['collide_data']
			if len(col) == 3:
				col_sph = self.vrep.simCreatePureShape(1, True, True, True, True, True, True, [0.05,0.05,0.05], 1.0, [1,1]) # L O L
				if col_sph != -1:
					self.vrep.simSetObjectPosition(col_sph, -1, col)

class VizuVrepAr(VizuVrep):

    def load(self, script="marker", ar=True, calcheck=True):
        super(self.__class__, self).load(script, ar, calcheck)