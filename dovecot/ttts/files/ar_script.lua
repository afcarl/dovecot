if (simGetScriptExecutionCount()==0) then


	--
	handle_marker = simGetObjectHandle("marker")
	handle_toy = simGetObjectHandle("toy")
	--
	marker_trajectory = simUnpackFloats(simGetScriptSimulationParameter(sim_handle_self, "Trajectory"))
	trajectory_sim_steps = #marker_trajectory / 3
	--
	r_pos_old = simGetObjectPosition(handle_marker, -1)
	t_pos_old = {marker_trajectory[1], marker_trajectory[1 + trajectory_sim_steps], marker_trajectory[1 + 2 * trajectory_sim_steps]}
	-- collide
	collide = false
	collide_data = {}
	-- will be return
	object_sensors = {}
	marker_real_trajectory = {}
	-- constants def
	k = 100.0 -- spring constant
	m = 0.100 -- grams ?
	dt = 0.010
	--dt = simGetSimulationTimeStep()
	simAddStatusbarMessage(dt)
	c = -2 * math.sqrt(m * k) -- critical damping
	-- function def
	function computeForceAndTorque(real_pos, target_pos, real_pos_old, target_pos_old)
		-- put some fucking code here
		a_x = real_pos[1]
		a_y = real_pos[2]
		a_z = real_pos[3]

		b_x = target_pos[1]
		b_y = target_pos[2]
		b_z = target_pos[3]

		a_x_old = real_pos_old[1]
		a_y_old = real_pos_old[2]
		a_z_old = real_pos_old[3]

		b_x_old = target_pos_old[1]
		b_y_old = target_pos_old[2]
		b_z_old = target_pos_old[3]

		d_x = (a_x - b_x)
		d_y = (a_y - b_y)
		d_z = (a_z - b_z)

		d_x_old = (a_x_old - b_x_old)
		d_y_old = (a_y_old - b_y_old)
		d_z_old = (a_z_old - b_z_old)

		f_x = k * d_x - (c * (d_x - d_x_old)/dt)
		f_y = k * d_y - (c * (d_y - d_y_old)/dt)
		f_z = k * d_z - (c * (d_z - d_z_old)/dt)

		return {-f_x, -f_y, -f_z}
	end
end

-- main code
simHandleChildScript(sim_handle_all_except_explicit)

current_step = simGetScriptExecutionCount()

pc = simGetObjectPosition(handle_toy, -1)
for i = 1, 3 do table.insert(object_sensors, pc[i]) end
qc = simGetObjectQuaternion(handle_toy, -1)
for i = 1, 4 do table.insert(object_sensors, qc[i]) end
lvc, avc = simGetObjectVelocity(handle_toy)
for i = 1, 3 do table.insert(object_sensors, lvc[i]) end
for i = 1, 3 do table.insert(object_sensors, avc[i]) end

if(current_step < trajectory_sim_steps) then
	r_pos = simGetObjectPosition(handle_marker, -1)
	for i = 1, 3 do table.insert(marker_real_trajectory, r_pos[i]) end
	t_pos = {marker_trajectory[current_step + 1], marker_trajectory[current_step + 1 + trajectory_sim_steps], marker_trajectory[current_step + 1 + 2 * trajectory_sim_steps]}
	force = computeForceAndTorque(r_pos, t_pos, r_pos_old, t_pos_old)
	simAddForceAndTorque(handle_marker, force, nil)
	r_pos_old = r_pos
	t_pos_old = t_pos

	if(collide == false) then
		col, data = simCheckCollisionEx(handle_toy, handle_marker)
		if (col > 0) then
			data_tmp = {0.0, 0.0, 0.0}
			for j = 1, col do
				x1 = data[(j - 1) * 6 + 1]
				y1 = data[(j - 1) * 6 + 2]
				z1 = data[(j - 1) * 6 + 3]
				x2 = data[(j - 1) * 6 + 4]
				y2 = data[(j - 1) * 6 + 5]
				z2 = data[(j - 1) * 6 + 6]
				data_tmp[1] = data_tmp[1] + ((x1 + x2) / 2)
				data_tmp[2] = data_tmp[2] + ((y1 + y2) / 2)
				data_tmp[3] = data_tmp[3] + ((z1 + z2) / 2)
			end

			table.insert(collide_data, data_tmp[1] / col)
			table.insert(collide_data, data_tmp[2] / col)
			table.insert(collide_data, data_tmp[3] / col)

			collide = true
		end
	end

else
	simSetScriptSimulationParameter(sim_handle_self, "Object_Sensors", simPackFloats(object_sensors))
	simSetScriptSimulationParameter(sim_handle_self, "Collide_Data", simPackFloats(collide_data))
	simSetScriptSimulationParameter(sim_handle_self, "Marker_Trajectory", simPackFloats(marker_real_trajectory))
	-- pause simulation
	simPauseSimulation()
end

if (simGetSimulationState()==sim_simulation_advancing_lastbeforestop) then
	-- Put some restoration code here
end