# Tools that help animate, and their terms (as of November 2026)

Licences change; check the vendor's own page before relying on a row. "Fit" is for stylised, stepped or puppet characters; realistic characters weigh differently.

| Tool | What it does for you | Cost and terms | Fit |
|---|---|---|---|
| Keying in your own clip data | Poses written as data (code, JSON) from a pose sheet, sampled into keys, checked headless | Free | Best for stepped and rigid characters: deterministic, testable, one source of truth |
| Blender (motion paths) | Import the rig with its clips, turn on motion paths for a hand or foot: shows an arc, a corner or missing lag in minutes | Free | A quick check for any pipeline |
| Blender (hand-keying) | A plain FK control rig on your own bones, Graph Editor, actions exported as glTF animations through NLA tracks ([manual](https://docs.blender.org/manual/uk/4.3/addons/import_export/scene_gltf2.html)) | Free | Good for a hand-keyed style; two sources of truth if the rest of the clips are data |
| Godot `SpringBoneSimulator3D` | Hinge-like spring per joint with stiffness, drag and gravity ([docs](https://docs.godotengine.org/en/stable/classes/class_springbonesimulator3d.html)) | Free | To find a lag's feel; bake it for stepped clips |
| Godot `LimitAngularVelocityModifier3D` (4.6) | Caps a bone's turning speed, which lags reversals ([docs](https://docs.godotengine.org/en/stable/classes/class_limitangularvelocitymodifier3d.html)) | Free | As above |
| Godot `BoneConstraint3D`, `TwoBoneIK3D` (4.6+) | Drive one bone from another (a chest turn from the hips), reach a target | Free | Runtime layers; deterministic |
| Cascadeur | Physics-assisted keying: AutoPhysics, AutoPosing; 2026.2 added additive layers and easing ([blog](https://cascadeur.com/blog/view/cascadeur-2026-2-animation-layers-easing-new-languages)) | Free: non-commercial, saves .casc only, 300 frames, 120 joints. Indie: about €8 a month billed yearly under $100k revenue, exports glTF, FBX, USD. Retargeting is Pro ([plans](https://cascadeur.com/plans)) | Pushes toward realistic weight; Quick Rigging wants a humanoid template |
| NVIDIA Kimodo SOMA-RP v1.2 | Text to motion; NPZ or BVH on a 77-joint skeleton, no retargeting tool ([card](https://huggingface.co/nvidia/Kimodo-SOMA-RP-v1.2)) | NVIDIA Open Model License, commercial use allowed | Adult realism; reference at most |
| MDM, T2M-GPT, MoMask, MotionGPT | Text to motion | Trained on AMASS or HumanML3D, whose licence forbids commercial artefacts | Ruled out for products |
| DeepMotion | Video to motion | Free tier personal and non-commercial ([FAQ](https://www.deepmotion.com/pricing-animate3d)) | Adult realism |
| Rokoko Vision | Video to motion, retargeting on paid plans | About $10 a month; commercial terms not on the page ([pricing](https://www.rokoko.com/pricing)) | Adult realism; get terms in writing |
| Your own reference video | Film the motion, step through it, key by eye | Free | Often the best reference for stylised work |

## Picking

- Stylised, stepped or puppet characters: key from a pose sheet in your own data, check arcs with motion paths or this skill's probe, and use simulation only to find lag, then bake it.
- Realistic humans with a mocap budget: capture or generate, then clean arcs and add overlap by hand.
- Whatever the tool, judge the result on the reel at the gameplay camera, not in the tool's viewport.
- Third-party scripts and add-ons (bone jigglers, auto-rigs) carry their licences; prefer taking the idea and writing your own where a project's policy asks for that.
