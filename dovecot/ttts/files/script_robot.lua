if (simGetScriptExecutionCount() == 0) then

    -- handles
    joint_names = {'vx64_1',
                   'vx64_2',
                   'vx64_3',
                   'vx28_4',
                   'vx28_5',
                   'vx28_6',
                  }

    joint_handles = {}
    for i=1, #joint_names   do
        table.insert(joint_handles, simGetObjectHandle(joint_names[i]))
    end

    marker = simGetObjectHandle("marker")


    -- settings
    simAddStatusbarMessage("info: setting parameters")

    trajectory = simUnpackFloats(simGetScriptSimulationParameter(sim_handle_self, "trajectory"))
    simSetScriptSimulationParameter(sim_handle_self, "trajectory", "")

    n_args    = math.floor(trajectory[1])
    traj_end  = math.floor(trajectory[2])
    sim_end   = math.floor(trajectory[3])
    max_speed =            trajectory[4]
    n_obj     = math.floor(trajectory[5])

    obj_handles = {}
    for i=1, n_obj do
        table.insert(obj_handles, math.floor(trajectory[5+i]))
    end

    simSetFloatingParameter(sim_floatparam_simulation_time_step, 0.02)
    for i = 1, #joint_handles do
        simSetObjectFloatParameter(joint_handles[i], 2017, max_speed)
    end

    sim_step = simGetScriptExecutionCount()
    ended = false
    collide = false

    -- return structure
    marker_sensors = {}
    joint_sensors  = {}
    obj_sensors    = {}
    collide_data   = {}

    simAddStatusbarMessage("info: starting simulation")
end

-- during the simulation
if (simGetScriptExecutionCount() > 0) then

    sim_step = simGetScriptExecutionCount()

    if (simGetSimulationState() ~= sim_simulation_advancing_lastbeforepause) then
        simHandleChildScript(sim_handle_all_except_explicit) -- make sure children are executed !

        -- marker
        tc = simGetObjectPosition(marker, -1)
        for j = 1, 3 do table.insert(marker_sensors, tc[j]) end

        -- objects
        for i = 1, #obj_handles do
            pc = simGetObjectPosition(obj_handles[i], -1)
            for j = 1, 3 do table.insert(obj_sensors, pc[j]) end

            qc = simGetObjectQuaternion(obj_handles[i], -1)
            for j = 1, 4 do table.insert(obj_sensors, qc[j]) end

            lvc, avc = simGetObjectVelocity(obj_handles[i])
            for j = 1, 3 do table.insert(obj_sensors, lvc[j]) end
            for j = 1, 3 do table.insert(obj_sensors, avc[j]) end
        end

        -- joints
        for i = 1, #joint_handles do
            table.insert(joint_sensors, simGetJointTargetPosition(joint_handles[i]))
            table.insert(joint_sensors, simGetObjectFloatParameter(joint_handles[i], 2012))

            if(sim_step < traj_end) then
                simSetJointTargetPosition(joint_handles[i], trajectory[n_args + #joint_handles*(sim_step-1) + i])
            end
        end


        -- collisions
        if(collide == false) then
            col, data = simCheckCollisionEx(obj_handles[1], marker)
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

                for i = 1, 3 do table.insert(collide_data, pt[i]) end
                for i = 1, 3 do table.insert(collide_data, data_tmp[i] / col) end
                collide = true
            end
        end
    end

    if(sim_step > sim_end) then
        if (ended == false) then
            ended = true
            simSetScriptSimulationParameter(sim_handle_self, "marker_sensors", simPackFloats(marker_sensors))
            simSetScriptSimulationParameter(sim_handle_self, "object_sensors", simPackFloats(obj_sensors))
            simSetScriptSimulationParameter(sim_handle_self, "joint_sensors",  simPackFloats(joint_sensors))
            simSetScriptSimulationParameter(sim_handle_self, "collide_data",   simPackFloats(collide_data))
            simPauseSimulation()
        end
    end
end

-- end of simulation
if (simGetSimulationState()==sim_simulation_advancing_lastbeforestop) then
    simAddStatusbarMessage("info: simulation ended")
end
