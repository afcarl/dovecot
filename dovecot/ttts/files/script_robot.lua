------------------------------------------------------------------------------
-- Following few lines automatically added by V-REP to guarantee compatibility
-- with V-REP 3.1.3 and later:
if (sim_call_type==sim_childscriptcall_initialization) then
	simSetScriptAttribute(sim_handle_self,sim_childscriptattribute_automaticcascadingcalls,false)
end
if (sim_call_type==sim_childscriptcall_cleanup) then

end
if (sim_call_type==sim_childscriptcall_sensing) then
	simHandleChildScripts(sim_call_type)
end
if (sim_call_type==sim_childscriptcall_actuation) then
	if not firstTimeHere93846738 then
		firstTimeHere93846738=0
	end
	simSetScriptAttribute(sim_handle_self,sim_scriptattribute_executioncount,firstTimeHere93846738)
	firstTimeHere93846738=firstTimeHere93846738+1

------------------------------------------------------------------------------


    if (simGetScriptExecutionCount() == 0) then

        -- handles
        joint_names = {"vx64_1",
                       "vx64_2",
                       "vx64_3",
                       "vx28_4",
                       "vx28_5",
                       "vx28_6",
                      }

        joint_handles = {}
        for i=1, #joint_names   do
            table.insert(joint_handles, simGetObjectHandle(joint_names[i]))
        end

        marker = simGetObjectHandle("marker")


        -- settings
        simAddStatusbarMessage("info: setting parameters")

        trajectory = simUnpackFloats(simGetStringSignal("trajectory"))

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
        contact_type   = {}
        contact_data   = {}

        simAddStatusbarMessage("info: starting simulation")
    end

    -- during the simulation
    if (simGetScriptExecutionCount() > 0) then

        sim_step = simGetScriptExecutionCount()

        if (simGetSimulationState() ~= sim_simulation_advancing_lastbeforepause) then
            -- simHandleChildScript(sim_handle_all_except_explicit) -- make sure children are executed !

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


            -- contacts
            contact_index = 0
            while(contact_index >= 0) do
                contact_handles, contact_point, contact_force = simGetContactInfo(sim_handle_all, marker, contact_index)
                if (contact_point == nil) then
                    -- if (contact_index > 0) then
                    --    simAddStatusbarMessage(contact_index)
                    -- end
                    contact_index = -1
                else
                    -- if (contact_handles[1] == obj_handles[1] or contact_handles[2] == obj_handles[1]) then
                    table.insert(contact_type, sim_step)
                    for i = 1, #contact_handles do
                        table.insert(contact_type, contact_handles[i])
                    end
                    for i = 1, #contact_point do
                        table.insert(contact_data, contact_point[i])
                    end
                    for i = 1, #contact_force do
                        table.insert(contact_data, contact_force[i])
                    end
                    -- end
                    contact_index = contact_index + 1
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

                    for i = 1, 3 do table.insert(collide_data, tc[i]) end
                    for i = 1, 3 do table.insert(collide_data, data_tmp[i] / col) end
                    collide = true
                end
            end
        end

        if(sim_step > sim_end) then
            if (ended == false) then
                ended = true
                simSetStringSignal("marker_sensors", simPackFloats(marker_sensors))
                simSetStringSignal("object_sensors", simPackFloats(obj_sensors))
                simSetStringSignal("joint_sensors",  simPackFloats(joint_sensors))
                if (#collide_data == 0) then
                    simSetStringSignal("collide_data", "")
                else
                    simSetStringSignal("collide_data",   simPackFloats(collide_data, 0, #collide_data))
                end
                if (#contact_data == 0) then
                    simSetStringSignal("contact_data",   "")
                    simSetStringSignal("contact_type",   "")
                else
                    simSetStringSignal("contact_data",   simPackFloats(contact_data, 0, #contact_data))
                    simSetStringSignal("contact_type",   simPackInts(contact_type))
                end
				simSetIntegerSignal("state", 0)
                simPauseSimulation()
            end
        end
    end

    -- end of simulation
    if (simGetSimulationState()==sim_simulation_advancing_lastbeforestop) then
        simAddStatusbarMessage("info: simulation ended")
    end

------------------------------------------------------------------------------
-- Following few lines automatically added by V-REP to guarantee compatibility
-- with V-REP 3.1.3 and later:
end
------------------------------------------------------------------------------
