if (simGetScriptExecutionCount() == 0) then
	simAddStatusbarMessage("Getting handles...")
	handles = {}
	handles[1] = simGetObjectHandle("vx64_1")
	handles[2] = simGetObjectHandle("vx64_2")
	handles[3] = simGetObjectHandle("vx64_3")
	handles[4] = simGetObjectHandle("vx28_4")
	handles[5] = simGetObjectHandle("vx28_5")
	handles[6] = simGetObjectHandle("vx28_6")
	cube = simGetObjectHandle("cube")
	simAddStatusbarMessage("Getting handles... done.")

	simAddStatusbarMessage("Getting scripts parameters...")
	
	Trajectory = simUnpackFloats(simGetScriptSimulationParameter(sim_handle_self, "Trajectory"))

	motors_sim_steps = math.floor((#Trajectory-1)/12)
	-- simAddStatusbarMessage("-- motors_sim_steps set to " .. motors_sim_steps)
	-- for i = 1, #Trajectory do  simAddStatusbarMessage("-- Trajectory[" .. i .. "] = " .. Trajectory[i]) end

	if(Trajectory == nil) then
		simAddStatusbarMessage("-- motors_sim_steps set to 0")
		motors_sim_steps = 0
	end

	max_sim_steps = math.floor(Trajectory[12*motors_sim_steps+1]) 
	if(max_sim_steps == nil) then
		simAddStatusbarMessage("-- max_sim_steps set to motors_sim_steps * 2")
		max_sim_steps = motors_sim_steps * 2
	end

	simAddStatusbarMessage("Getting scripts parameters... done.")

	sim_step = simGetScriptExecutionCount()

	-- will be return
	object_positions_step_by_step = {}
	object_quaternions_step_by_step = {}
	object_velocities_step_by_step = {}
	joint_positions_step_by_step = {}
	joint_velocities_step_by_step = {}
	for i = 1, #handles do
		table.insert(joint_positions_step_by_step, {})
		table.insert(joint_velocities_step_by_step, {})
	end
end

-- during the simulation
if (simGetScriptExecutionCount() > 0) then
	simHandleChildScript(sim_handle_all_except_explicit) -- make sure children are executed !
	
	pc = simGetObjectPosition(cube, -1)
	for i = 1, 3 do table.insert(object_positions_step_by_step, pc[i]) end

	qc = simGetObjectQuaternion(cube, -1)
	for i = 1, 4 do table.insert(object_quaternions_step_by_step, qc[i]) end
	
	lvc, avc = simGetObjectVelocity(cube)
	for i = 1, 3 do table.insert(object_velocities_step_by_step, lvc[i]) end
	for i = 1, 3 do table.insert(object_velocities_step_by_step, avc[i]) end

	sim_step = simGetScriptExecutionCount()

	function ReadMotorsPosVel(_index)
		table.insert(joint_positions_step_by_step[_index], simGetJointTargetPosition(handles[_index]))
		table.insert(joint_velocities_step_by_step[_index], simGetObjectFloatParameter(handles[_index], 2012))
	end
	for i = 1, #handles do
		ReadMotorsPosVel(i)
	end

	if(sim_step <= motors_sim_steps) then
		function WriteMotorsPosVel(_index)
			simSetJointTargetPosition(handles[_index], Trajectory[2 * (_index-1) * motors_sim_steps + sim_step])
			simSetObjectFloatParameter(handles[_index], 2017, Trajectory[(2 * (_index-1) + 1) * motors_sim_steps + sim_step])
		end
		for i = 1, #handles do
			WriteMotorsPosVel(i)
		end
	end

	if(sim_step > max_sim_steps) then
		simSetScriptSimulationParameter(sim_handle_self,"Object_Positions",simPackFloats(object_positions_step_by_step))
		simSetScriptSimulationParameter(sim_handle_self,"Object_Quaternions",simPackFloats(object_quaternions_step_by_step))
		simSetScriptSimulationParameter(sim_handle_self,"Object_Velocities",simPackFloats(object_velocities_step_by_step))
		
		function WriteMotorsResults(_index)
			simSetScriptSimulationParameter(sim_handle_self,"Joint_" .. tostring(_index) .. "_final_pos",simPackFloats(joint_positions_step_by_step[_index]))
			simSetScriptSimulationParameter(sim_handle_self,"Joint_" .. tostring(_index) .. "_final_vel",simPackFloats(joint_positions_step_by_step[_index]))
		end
		for i = 1, #handles do
			WriteMotorsResults(i)
		end
		simPauseSimulation()
	end
	
end

-- Recommended in documentation : see doc
if (simGetSimulationState()==sim_simulation_advancing_lastbeforestop) then
    -- Put some restoration code here
end
