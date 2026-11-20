extends Node
## Records where named bones and nodes are, every frame, and writes them as the JSON that
## motion_path.py reads (motion-kit's motion-craft skill). Godot 4.3 or later.
##
## Add it to a scene (or create it from a test script), point it at a Skeleton3D and name
## the bones, and/or give it Node3D paths. With a camera, it records where each point is on
## screen, in pixels (what the player sees); without, in the world, in metres. It starts
## after `skip` frames, records `frames` frames, writes `path`, and quits the game if
## `quit_when_done` is set, so a headless or Movie Maker run can record and stop:
##   godot --path . --fixed-fps 60 res://my_view.tscn -- --paths=/abs/paths.json
## (`--paths=` on the command line overrides `path`.)
##
## Recording the extremities that matter (hands, feet, head, the tip of anything that
## trails) and their parents (upper arm, thigh) lets the probe measure arcs and lag.
## It runs late in the frame (process_priority 1000), after animation and IK have posed
## the skeleton; on a figure stepped on twos, consecutive samples repeat, which the probe
## counts as one pose.

@export var skeleton: Skeleton3D
## Bone names in `skeleton`, recorded at each bone's joint (its global pose origin).
@export var bones: PackedStringArray = []
## Other nodes to record, at their global origin.
@export var nodes: Array[NodePath] = []
## Record on screen through this camera, in pixels; leave empty for world space.
@export var camera: Camera3D
@export var skip := 30
@export var frames := 240
@export var path := "user://paths.json"
@export var quit_when_done := false

var _seen := 0
var _points := {}
var _done := false


func _ready() -> void:
	process_priority = 1000
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--paths="):
			path = arg.trim_prefix("--paths=")
	for bone in bones:
		_points[bone] = []
	for node_path in nodes:
		_points[String(node_path.get_name(node_path.get_name_count() - 1))] = []


func _process(_delta: float) -> void:
	if _done:
		return
	_seen += 1
	if _seen <= skip:
		return
	if skeleton != null:
		for bone in bones:
			var index := skeleton.find_bone(bone)
			if index < 0:
				continue
			var at := skeleton.global_transform * skeleton.get_bone_global_pose(index).origin
			(_points[bone] as Array).append(_sample(at))
	for node_path in nodes:
		var node := get_node_or_null(node_path) as Node3D
		if node != null:
			(_points[String(node_path.get_name(node_path.get_name_count() - 1))] as Array).append(_sample(node.global_position))
	if _seen - skip >= frames:
		_write()


func _sample(at: Vector3) -> Array:
	if camera != null:
		var on_screen := camera.unproject_position(at)
		return [on_screen.x, on_screen.y]
	return [at.x, at.y, at.z]


func _write() -> void:
	_done = true
	# Under --fixed-fps every frame's delta is exact; otherwise take the measured rate.
	var step := get_process_delta_time()
	var data := {
		"fps": roundf(1.0 / step) if step > 0.0 else Engine.get_frames_per_second(),
		"space": "screen" if camera != null else "world",
		"plane": "xy",
		"points": _points,
	}
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("bone_path_recorder: can't write %s" % path)
		return
	file.store_string(JSON.stringify(data))
	file.close()
	print("bone_path_recorder: %d frames of %d points to %s" % [frames, _points.size(), path])
	if quit_when_done:
		get_tree().quit()
