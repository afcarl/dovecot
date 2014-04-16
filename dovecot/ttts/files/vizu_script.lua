if (simGetScriptExecutionCount()==0) then

	-- somes funtions
	function error(message)
		simAddStatusbarMessage(message)
		simPauseSimulation()
	end

	-- structures or something like that
	points  = {}
	points_coordinates = {}
	points_count = {}
	points_transparency = {}

	lines = {}
	lines_coordinates = {}
	lines_count = {}
	lines_transparency = {}

	spheres = {}
	spheres_coordinates = {}
	spheres_count = {}
	spheres_transparency = {}

	max_count = 0

	-- parameters
	data = simUnpackFloats(simGetScriptSimulationParameter(sim_handle_self, "Data"))
	keep_toy = simUnpackFloats(simGetScriptSimulationParameter(sim_handle_self, "Keep_Toy"))
	if (keep_toy[1] == 0) then
		handle_toy = simGetObjectHandle("toy")
		simRemoveObject(handle_toy)
	end
	-- unpacking data
	offset = 1 -- table index start at 1, first value is number of messages
	for i = 1, data[1] do
		-- object parameters
		message_size = data[offset + 1]
		type = data[offset + 2]
		color = {data[offset + 3], data[offset + 4], data[offset + 5]}
		transparency = data[offset + 6]
		size = data[offset + 7]
		num_coordinates = data[offset + 8]
		offset = offset + 9
		if (type == 0) then -- points
			obj_p = simAddDrawingObject(sim_drawing_points, size + sim_drawing_itemtransparency, 0, -1, num_coordinates / 3, color, nil, nil, nil)
			if not(obj_p == -1) then
				table.insert(points, obj_p)
				obj_p_c = {}
				for j = offset, offset + num_coordinates do
					table.insert(obj_p_c, data[j])
				end
				table.insert(points_coordinates, obj_p_c)
				table.insert(points_count, num_coordinates / 3)
				table.insert(points_transparency, transparency)
				max_count = math.max(max_count, num_coordinates / 3)
			else
				error("ERROR while creating points set...")
			end
		elseif (type == 1) then -- lines
			obj_l = simAddDrawingObject(sim_drawing_lines + sim_drawing_itemtransparency, size, 0, -1, num_coordinates / 6, color, nil, nil, nil)
			if not(obj_l == -1) then
				table.insert(lines, obj_l)
				obj_p_l = {}
				for j = offset, offset + num_coordinates do
					table.insert(obj_p_l, data[j])
				end
				table.insert(lines_coordinates, obj_p_l)
				table.insert(lines_count, num_coordinates / 6)
				table.insert(lines_transparency, transparency)
				max_count = math.max(max_count, num_coordinates / 6)
			else
				error("ERROR while creating points set...")
			end
		elseif (type == 2) then -- spheres
			obj_s = simAddDrawingObject(sim_drawing_spherepoints + sim_drawing_itemtransparency, size, 0, -1, num_coordinates / 3, color, nil, nil, nil)
			if not(obj_s == -1) then
				table.insert(spheres, obj_s)
				obj_p_s = {}
				for j = offset, offset + num_coordinates do
					table.insert(obj_p_s, data[j])
				end
				table.insert(spheres_coordinates, obj_p_s)
				table.insert(spheres_count, num_coordinates / 3)
				table.insert(spheres_transparency, transparency)
				max_count = math.max(max_count, num_coordinates / 3)
			else
				error("ERROR while creating spheres set...")
			end
		else
			error("ERROR : type is enknow...")
		end
		offset = offset + num_coordinates - 1
	end
	total_points = 0
	total_lines = 0
	total_spheres = 0
	drawn_points = 0
	drawn_lines = 0
	drawn_spheres = 0
	for i = 1, #points do
		total_points = total_points + points_count[i]
	end
	for i = 1, #lines do
		total_lines = total_lines + lines_count[i]
	end
	for i = 1, #spheres do
		total_spheres = total_spheres + spheres_count[i]
	end
end

-- main code
simHandleChildScript(sim_handle_all_except_explicit)
count = simGetScriptExecutionCount()
if (count > 0) then
	if (count > max_count + 1) then
		simAddStatusbarMessage("Drawn lines : "..drawn_lines)
		simAddStatusbarMessage("Total lines to draw : "..total_lines)
		simAddStatusbarMessage("Drawn points : "..drawn_points)
		simAddStatusbarMessage("Total points to draw : "..total_points)
		simAddStatusbarMessage("Drawn spheres : "..drawn_spheres)
		simAddStatusbarMessage("Total spheres to draw : "..total_spheres)
		simPauseSimulation()
	else
		-- points
		for i = 1 , #points do
			if (count <= points_count[i]) then
				coord = {}
				table.insert(coord, points_coordinates[i][3 * (count - 1) + 1])
				table.insert(coord, points_coordinates[i][3 * (count - 1) + 2])
				table.insert(coord, points_coordinates[i][3 * (count - 1) + 3])
				table.insert(coord, points_transparency[i])
				simAddDrawingObjectItem(points[i], coord)
				drawn_points = drawn_points + 1
			end
		end
		-- lines
		for i = 1 , #lines do
			if (count <= lines_count[i]) then
				coord = {}
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 1])
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 2])
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 3])
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 4])
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 5])
				table.insert(coord, lines_coordinates[i][6 * (count - 1) + 6])
				table.insert(coord, lines_transparency[i])
				simAddDrawingObjectItem(lines[i], coord)
				drawn_lines = drawn_lines + 1
			end
		end
		-- spheres
		for i = 1 , #spheres do
			if (count <= spheres_count[i]) then
				coord = {}
				table.insert(coord, spheres_coordinates[i][3 * (count - 1) + 1])
				table.insert(coord, spheres_coordinates[i][3 * (count - 1) + 2])
				table.insert(coord, spheres_coordinates[i][3 * (count - 1) + 3])
				table.insert(coord, spheres_transparency[i])
				simAddDrawingObjectItem(spheres[i], coord)
				drawn_spheres = drawn_spheres + 1
			end
		end
	end
end

if (simGetSimulationState()==sim_simulation_advancing_lastbeforestop) then
	-- Put some restoration code here
end