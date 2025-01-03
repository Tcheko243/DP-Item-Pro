bl_info = {
    "name": "DP Item Pro",
    "description": "Advanced tool for managing transformations and manipulating objects",
    "author": "Dimona Patrick",
    "version": (2, 3, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Object > DP Item Pro",
    "category": "Object",
}

import bpy
from bpy.utils import register_class, unregister_class
import math
import random
from mathutils import Vector, Matrix
import functools

class ITEMPRO_Properties(bpy.types.PropertyGroup):
    uniform_scale: bpy.props.FloatProperty(
        name="Uniform Scale",
        description="Set a uniform scale for the object",
        default=1.0,
        min=0.01,
        max=10.0,
    )
    duplication_count: bpy.props.IntProperty(
        name="Duplication Count",
        description="Number of duplicates for stacking",
        default=5,
        min=1,
        max=100,
    )
    duplication_offset: bpy.props.FloatVectorProperty(
        name="Duplication Offset",
        description="Offset for stacking duplicates (X, Y, Z)",
        default=(0.0, 0.0, 1.0),
    )
    align_axis: bpy.props.EnumProperty(
        name="Align Axis",
        description="Axis for alignment",
        items=[
            ('X', 'X', 'Align on X axis'),
            ('Y', 'Y', 'Align on Y axis'),
            ('Z', 'Z', 'Align on Z axis'),
        ],
        default='Z'
    )
    mirror_axis: bpy.props.EnumProperty(
        name="Mirror Axis",
        items=[
            ('X', 'X', 'Mirror on X axis'),
            ('Y', 'Y', 'Mirror on Y axis'),
            ('Z', 'Z', 'Mirror on Z axis'),
        ],
        default='X'
    )
    distribution_type: bpy.props.EnumProperty(
        name="Distribution",
        items=[
            ('LINEAR', 'Linear', 'Linear distribution'),
            ('CIRCULAR', 'Circular', 'Circular distribution'),
            ('GRID', 'Grid', 'Grid distribution'),
            ('RANDOM', 'Random', 'Random distribution')
        ],
        default='LINEAR'
    )
    grid_size: bpy.props.IntVectorProperty(
        name="Grid Size",
        description="Number of items in each direction (X, Y)",
        size=2,
        default=(3, 3),
        min=1,
        max=10,
    )
    circular_count: bpy.props.IntProperty(
        name="Count",
        description="Number of items in circle",
        default=8,
        min=2,
        max=36
    )
    radius: bpy.props.FloatProperty(
        name="Radius",
        description="Radius for circular distribution",
        default=1.0,
        min=0.01
    )
    spacing: bpy.props.FloatProperty(
        name="Spacing",
        description="Space between objects",
        default=1.0,
        min=0.0
    )
    random_range: bpy.props.FloatVectorProperty(
        name="Random Range",
        description="Range for random distribution",
        default=(5.0, 5.0, 5.0),
        min=0.0
    )
    rotation_angle: bpy.props.FloatProperty(
        name="Rotation Angle",
        description="Angle for smooth rotation",
        default=45.0,
        min=-360.0,
        max=360.0
    )

    # Dimensions
    dimensions: bpy.props.FloatVectorProperty(
        name="Dimensions",
        description="Object dimensions (X, Y, Z)",
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        unit='LENGTH'
    )

    # Transform Constraints
    constrain_proportional: bpy.props.BoolProperty(
        name="Constrain Proportional",
        description="Maintain proportional dimensions when scaling",
        default=False
    )

    lock_dimensions: bpy.props.BoolVectorProperty(
        name="Lock Dimensions",
        description="Lock individual dimensions",
        size=3,
        default=(False, False, False)
    )

    # Precision settings
    transform_precision: bpy.props.FloatProperty(
        name="Transform Precision",
        description="Precision for transformations",
        default=0.01,
        min=0.0001,
        max=1.0
    )

    # Pivot point settings
    pivot_point: bpy.props.EnumProperty(
        name="Pivot Point",
        items=[
            ('CENTER', 'Center', 'Use object center'),
            ('ORIGIN', 'Origin', 'Use object origin'),
            ('CURSOR', '3D Cursor', 'Use 3D cursor'),
            ('INDIVIDUAL', 'Individual Origins', 'Use individual origins'),
            ('MEDIAN', 'Median Point', 'Use median point')
        ],
        default='CENTER'
    )

     # New properties
    random_seed: bpy.props.IntProperty(
        name="Random Seed",
        description="Seed for random operations",
        default=1
    )
    
    snap_offset: bpy.props.FloatProperty(
        name="Snap Offset",
        description="Offset distance for snapping",
        default=0.0,
        unit='LENGTH'
    )
    
    align_to_normal: bpy.props.BoolProperty(
        name="Align to Normal",
        description="Align objects to surface normal when snapping",
        default=True
    )

class ITEMPRO_PT_MainPanel(bpy.types.Panel):
    bl_label = "DP Item Pro"
    bl_idname = "ITEMPRO_PT_MainPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        props = context.scene.item_pro_props

        if obj:
            # Basic Transformations
            box = layout.box()
            box.label(text="Basic Transformations:")
            col = box.column(align=True)
            col.prop(obj, "location")
            col.prop(obj, "rotation_euler")
            col.prop(obj, "scale")

            # Dimensions and Transform Settings
            box = layout.box()
            box.label(text="Dimensions and Transform:")
            
            # Dimensions
            row = box.row(align=True)
            row.prop(obj, "dimensions")
            
            # Lock Dimensions
            row = box.row(align=True)
            row.prop(props, "lock_dimensions", text="Lock")
            
            # Constrain Proportional
            row = box.row()
            row.prop(props, "constrain_proportional")
            
            # Transform Precision
            row = box.row()
            row.prop(props, "transform_precision")
            
            # Apply Dimensions Button
            row = box.row()
            row.operator("itempro.apply_dimensions")
            
            row = box.row(align=True)
            row.operator("itempro.reset_transformations", text="Reset All")
            row.operator("itempro.reset_rotation", text="Reset Rotation")
            
            # Scaling Tools
            box = layout.box()
            box.label(text="Scaling Tools:")
            box.prop(props, "uniform_scale")
            row = box.row(align=True)
            row.operator("itempro.apply_uniform_scale")
            row.operator("itempro.reset_scale")

            # Ground and Pivot Tools
            box = layout.box()
            box.label(text="Ground and Pivot Tools:")
            box.operator("itempro.place_on_ground", text="Place on Ground")
            
            sub_box = box.box()
            sub_box.label(text="Set Pivot Point:")
            row = sub_box.row(align=True)
            op = row.operator("itempro.set_pivot", text="Center")
            op.pivot_type = 'CENTER'
            op = row.operator("itempro.set_pivot", text="Bottom")
            op.pivot_type = 'BOTTOM'
            op = row.operator("itempro.set_pivot", text="Top")
            op.pivot_type = 'TOP'
            op = row.operator("itempro.set_pivot", text="To Cursor")
            op.pivot_type = 'CURSOR'

            # Distribution Tools
            box = layout.box()
            box.label(text="Distribution:")
            box.prop(props, "distribution_type")
            
            if props.distribution_type == 'GRID':
                box.prop(props, "grid_size")
            elif props.distribution_type == 'CIRCULAR':
                box.prop(props, "circular_count")
                box.prop(props, "radius")
            elif props.distribution_type == 'RANDOM':
                box.prop(props, "random_range")
            
            box.prop(props, "spacing")
            box.operator("itempro.distribute_objects")

            # Rotation Tools
            box = layout.box()
            box.label(text="Rotation Tools:")
            box.prop(props, "rotation_angle")
            row = box.row(align=True)
            row.operator("itempro.smooth_rotate")
            row.operator("itempro.random_rotate")

            # Array Tools
            box = layout.box()
            box.label(text="Array Tools:")
            box.prop(props, "duplication_count")
            box.prop(props, "duplication_offset")
            box.operator("itempro.create_array")

            # Symmetry Tools
            box = layout.box()
            box.label(text="Symmetry Tools:")
            box.prop(props, "mirror_axis")
            row = box.row(align=True)
            row.operator("itempro.mirror_object")
            row.operator("itempro.create_symmetry")

            # Add new tools section
            box = layout.box()
            box.label(text="Advanced Tools:")
            
            row = box.row(align=True)
            row.operator("itempro.randomize_properties")
            row.operator("itempro.snap_to_surface")
            
            box.prop(props, "random_seed")
            box.prop(props, "snap_offset")
            box.prop(props, "align_to_normal")
            
            row = box.row()
            row.operator("itempro.align_objects")

def error_handler(func):
    @functools.wraps(func)
    def wrapper(self, context):
        try:
            return func(self, context)
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
    return wrapper


class ITEMPRO_OT_RandomizeProperties(bpy.types.Operator):
    bl_idname = "itempro.randomize_properties"
    bl_label = "Randomize Properties"
    bl_description = "Randomize object properties"
    bl_options = {'REGISTER', 'UNDO'}

    @error_handler
    def execute(self, context):
        obj = context.active_object
        if obj:
            props = context.scene.item_pro_props
            random.seed(props.random_seed)
            
            # Randomize location
            obj.location.x += random.uniform(-1, 1)
            obj.location.y += random.uniform(-1, 1)
            obj.location.z += random.uniform(-1, 1)
            
            # Randomize rotation
            obj.rotation_euler.x += random.uniform(-0.5, 0.5)
            obj.rotation_euler.y += random.uniform(-0.5, 0.5)
            obj.rotation_euler.z += random.uniform(-0.5, 0.5)
            
            # Randomize scale
            random_scale = random.uniform(0.8, 1.2)
            obj.scale = (random_scale, random_scale, random_scale)

        return {'FINISHED'}



class ITEMPRO_OT_SnapToSurface(bpy.types.Operator):
    bl_idname = "itempro.snap_to_surface"
    bl_label = "Snap to Surface"
    bl_options = {'REGISTER', 'UNDO'}
    
    @error_handler
    def execute(self, context):
        obj = context.active_object
        if not obj:
            raise Exception("No active object selected")
            
        # Ray cast from object to find surface below
        scene = context.scene
        hit, loc, norm, _, _, _ = scene.ray_cast(
            context.view_layer.depsgraph,
            obj.location + Vector((0, 0, 1000)),
            Vector((0, 0, -1))
        )
        
        if hit:
            obj.location = loc
        return {'FINISHED'}


class ITEMPRO_OT_AlignObjects(bpy.types.Operator):
    bl_idname = "itempro.align_objects"
    bl_label = "Align Objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    align_mode: bpy.props.EnumProperty(
        items=[
            ('MIN', 'Minimum', 'Align to minimum boundary'),
            ('MAX', 'Maximum', 'Align to maximum boundary'),
            ('CENTER', 'Center', 'Align to center'),
        ],
        default='CENTER'
    )
    
    @error_handler
    def execute(self, context):
        if len(context.selected_objects) < 2:
            raise Exception("Select at least two objects")
            
        active = context.active_object
        selected = [obj for obj in context.selected_objects if obj != active]
        
        for obj in selected:
            if self.align_mode == 'MIN':
                obj.location = active.location
            elif self.align_mode == 'MAX':
                bounds = active.bound_box[:]
                obj.location = active.location + Vector((bounds[7]))
            else:  # CENTER
                obj.location = active.location
                
        return {'FINISHED'}


class ITEMPRO_OT_ResetTransformations(bpy.types.Operator):
    bl_idname = "itempro.reset_transformations"
    bl_label = "Reset Transformations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        obj.location = (0, 0, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)
        return {'FINISHED'}

class ITEMPRO_OT_ResetRotation(bpy.types.Operator):
    bl_idname = "itempro.reset_rotation"
    bl_label = "Reset Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        obj.rotation_euler = (0, 0, 0)
        return {'FINISHED'}

class ITEMPRO_OT_CenterToOrigin(bpy.types.Operator):
    bl_idname = "itempro.center_to_origin"
    bl_label = "Center to Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        obj.location = (0, 0, 0)
        return {'FINISHED'}

class ITEMPRO_OT_LockTransformations(bpy.types.Operator):
    bl_idname = "itempro.lock_transformations"
    bl_label = "Lock Transformations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        # Toggle location locks
        obj.lock_location[0] = not obj.lock_location[0]
        obj.lock_location[1] = not obj.lock_location[1]
        obj.lock_location[2] = not obj.lock_location[2]
        
        # Toggle rotation locks
        obj.lock_rotation[0] = not obj.lock_rotation[0]
        obj.lock_rotation[1] = not obj.lock_rotation[1]
        obj.lock_rotation[2] = not obj.lock_rotation[2]
        
        # Toggle scale locks
        obj.lock_scale[0] = not obj.lock_scale[0]
        obj.lock_scale[1] = not obj.lock_scale[1]
        obj.lock_scale[2] = not obj.lock_scale[2]
        
        return {'FINISHED'}

class ITEMPRO_OT_AlignObjects(bpy.types.Operator):
    bl_idname = "itempro.align_objects"
    bl_label = "Align Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        active = context.active_object
        
        if len(selected) < 2 or not active:
            self.report({'ERROR'}, "Select at least two objects, with one active")
            return {'CANCELLED'}
        
        axis = context.scene.item_pro_props.align_axis
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        
        target_pos = active.location[axis_index]
        
        for obj in selected:
            if obj != active:
                loc = list(obj.location)
                loc[axis_index] = target_pos
                obj.location = loc
        
        return {'FINISHED'}

class ITEMPRO_OT_StackObjects(bpy.types.Operator):
    bl_idname = "itempro.stack_objects"
    bl_label = "Stack Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least two objects")
            return {'CANCELLED'}
        
        props = context.scene.item_pro_props
        spacing = props.spacing
        
        # Sort objects by Z location
        sorted_objects = sorted(selected, key=lambda obj: obj.location.z)
        base_z = sorted_objects[0].location.z
        
        for i, obj in enumerate(sorted_objects):
            obj.location.z = base_z + (i * spacing)
        
        return {'FINISHED'}

class ITEMPRO_OT_DistributeObjects(bpy.types.Operator):
    bl_idname = "itempro.distribute_objects"
    bl_label = "Distribute Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least two objects")
            return {'CANCELLED'}
        
        props = context.scene.item_pro_props
        
        if props.distribution_type == 'LINEAR':
            self.distribute_linear(context, selected)
        elif props.distribution_type == 'CIRCULAR':
            self.distribute_circular(context, selected)
        elif props.distribution_type == 'GRID':
            self.distribute_grid(context, selected)
        elif props.distribution_type == 'RANDOM':
            self.distribute_random(context, selected)
        
        return {'FINISHED'}
    
    def distribute_linear(self, context, objects):
        props = context.scene.item_pro_props
        spacing = props.spacing
        
        for i, obj in enumerate(objects):
            obj.location[0] = i * spacing
    
    def distribute_circular(self, context, objects):
        props = context.scene.item_pro_props
        radius = props.radius
        count = len(objects)
        
        for i, obj in enumerate(objects):
            angle = (2 * math.pi * i) / count
            obj.location[0] = math.cos(angle) * radius
            obj.location[1] = math.sin(angle) * radius
    
    def distribute_grid(self, context, objects):
        props = context.scene.item_pro_props
        spacing = props.spacing
        grid_x, grid_y = props.grid_size
        
        for i, obj in enumerate(objects):
            if i >= grid_x * grid_y:
                break
            
            row = i // grid_x
            col = i % grid_x
            
            obj.location[0] = col * spacing
            obj.location[1] = row * spacing
    
    def distribute_random(self, context, objects):
        props = context.scene.item_pro_props
        range_x, range_y, range_z = props.random_range
        
        for obj in objects:
            obj.location = (
                random.uniform(-range_x, range_x),
                random.uniform(-range_y, range_y),
                random.uniform(-range_z, range_z)
            )

class ITEMPRO_OT_MirrorObject(bpy.types.Operator):
    bl_idname = "itempro.mirror_object"
    bl_label = "Mirror Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        axis = context.scene.item_pro_props.mirror_axis
        
        if axis == 'X':
            obj.scale[0] *= -1
        elif axis == 'Y':
            obj.scale[1] *= -1
        elif axis == 'Z':
            obj.scale[2] *= -1
        
        return {'FINISHED'}


class ITEMPRO_OT_ApplyUniformScale(bpy.types.Operator):
    bl_idname = "itempro.apply_uniform_scale"
    bl_label = "Apply Uniform Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        scale = context.scene.item_pro_props.uniform_scale
        obj.scale = (scale, scale, scale)
        return {'FINISHED'}

class ITEMPRO_OT_ResetScale(bpy.types.Operator):
    bl_idname = "itempro.reset_scale"
    bl_label = "Reset Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        obj.scale = (1.0, 1.0, 1.0)
        return {'FINISHED'}

class ITEMPRO_OT_SmoothRotate(bpy.types.Operator):
    bl_idname = "itempro.smooth_rotate"
    bl_label = "Smooth Rotate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        angle = context.scene.item_pro_props.rotation_angle
        obj.rotation_euler.z += math.radians(angle)
        return {'FINISHED'}

class ITEMPRO_OT_RandomRotate(bpy.types.Operator):
    bl_idname = "itempro.random_rotate"
    bl_label = "Random Rotate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj.rotation_euler = (
                random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi)
            )
        return {'FINISHED'}

class ITEMPRO_OT_CreateArray(bpy.types.Operator):
    bl_idname = "itempro.create_array"
    bl_label = "Create Array"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        props = context.scene.item_pro_props
        offset = props.duplication_offset
        
        for i in range(props.duplication_count):
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.location = (
                obj.location[0] + offset[0] * i,
                obj.location[1] + offset[1] * i,
                obj.location[2] + offset[2] * i
            )
            context.collection.objects.link(new_obj)
        
        return {'FINISHED'}


class ITEMPRO_OT_CreateSymmetry(bpy.types.Operator):
    bl_idname = "itempro.create_symmetry"
    bl_label = "Create Symmetry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        axis = context.scene.item_pro_props.mirror_axis
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        
        if axis == 'X':
            new_obj.location.x = -obj.location.x
        elif axis == 'Y':
            new_obj.location.y = -obj.location.y
        elif axis == 'Z':
            new_obj.location.z = -obj.location.z
            
        context.collection.objects.link(new_obj)
        return {'FINISHED'}
    
class ITEMPRO_OT_ApplyDimensions(bpy.types.Operator):
    bl_idname = "itempro.apply_dimensions"
    bl_label = "Apply Dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.item_pro_props

        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Store original dimensions
        original_dims = obj.dimensions[:]

        # Calculate scale factors
        new_dims = props.dimensions
        scale_factors = [
            new_dims[i] / original_dims[i] if original_dims[i] != 0 else 1.0
            for i in range(3)
        ]

        # Apply scaling based on lock status and proportional constraint
        if props.constrain_proportional:
            # Find the average scale factor of unlocked dimensions
            unlocked_scales = [
                scale_factors[i]
                for i in range(3)
                if not props.lock_dimensions[i]
            ]
            if unlocked_scales:
                avg_scale = sum(unlocked_scales) / len(unlocked_scales)
                scale_factors = [avg_scale] * 3

        # Apply scale factors
        for i in range(3):
            if not props.lock_dimensions[i]:
                obj.scale[i] *= scale_factors[i]

        return {'FINISHED'}

# Operator to reset dimensions
class ITEMPRO_OT_ResetDimensions(bpy.types.Operator):
    bl_idname = "itempro.reset_dimensions"
    bl_label = "Reset Dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        obj.dimensions = (1.0, 1.0, 1.0)
        return {'FINISHED'}

class ITEMPRO_OT_PlaceOnGround(bpy.types.Operator):
    bl_idname = "itempro.place_on_ground"
    bl_label = "Place on Ground"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
            
        # Get the lowest point of the object
        lowest_point = min((obj.matrix_world @ Vector(v.co) for v in obj.data.vertices), key=lambda v: v.z).z
        
        # Move object up by its lowest point
        obj.location.z -= lowest_point
        
        return {'FINISHED'}

class ITEMPRO_OT_SetPivot(bpy.types.Operator):
    bl_idname = "itempro.set_pivot"
    bl_label = "Set Pivot Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    pivot_type: bpy.props.EnumProperty(
        items=[
            ('CENTER', 'Center', 'Set pivot to center'),
            ('BOTTOM', 'Bottom', 'Set pivot to bottom'),
            ('TOP', 'Top', 'Set pivot to top'),
            ('CURSOR', 'Cursor', 'Set pivot to 3D cursor')
        ],
        name="Pivot Type",
        default='CENTER'
    )
    
    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
            
        if self.pivot_type == 'CENTER':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        elif self.pivot_type == 'BOTTOM':
            # Save current cursor location
            cursor_loc = context.scene.cursor.location.copy()
            # Get object bounds
            bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            lowest_z = min(v.z for v in bounds)
            # Set cursor to bottom center
            context.scene.cursor.location = obj.location
            context.scene.cursor.location.z = lowest_z
            # Set origin to cursor
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            # Restore cursor location
            context.scene.cursor.location = cursor_loc
        elif self.pivot_type == 'TOP':
            cursor_loc = context.scene.cursor.location.copy()
            bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            highest_z = max(v.z for v in bounds)
            context.scene.cursor.location = obj.location
            context.scene.cursor.location.z = highest_z
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            context.scene.cursor.location = cursor_loc
        elif self.pivot_type == 'CURSOR':
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
        return {'FINISHED'}


# Add precision transform operator
class ITEMPRO_OT_PrecisionTransform(bpy.types.Operator):
    bl_idname = "itempro.precision_transform"
    bl_label = "Precision Transform"
    bl_options = {'REGISTER', 'UNDO'}

    transform_type: bpy.props.EnumProperty(
        items=[
            ('LOCATION', 'Location', 'Precise location adjustment'),
            ('ROTATION', 'Rotation', 'Precise rotation adjustment'),
            ('SCALE', 'Scale', 'Precise scale adjustment')
        ],
        default='LOCATION'
    )

    value: bpy.props.FloatProperty(
        name="Value",
        description="Transform value",
        default=0.0
    )

    axis: bpy.props.EnumProperty(
        items=[
            ('X', 'X', 'X axis'),
            ('Y', 'Y', 'Y axis'),
            ('Z', 'Z', 'Z axis')
        ],
        default='X'
    )

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        precision = context.scene.item_pro_props.transform_precision
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]

        if self.transform_type == 'LOCATION':
            obj.location[axis_index] += self.value * precision
        elif self.transform_type == 'ROTATION':
            obj.rotation_euler[axis_index] += math.radians(self.value * precision)
        elif self.transform_type == 'SCALE':
            obj.scale[axis_index] += self.value * precision

        return {'FINISHED'}    

# Registration
classes = [
    ITEMPRO_Properties,
    ITEMPRO_PT_MainPanel,
    ITEMPRO_OT_ResetTransformations,
    ITEMPRO_OT_RandomizeProperties,
    ITEMPRO_OT_SnapToSurface,
    ITEMPRO_OT_AlignObjects,
    ITEMPRO_Properties,
    ITEMPRO_PT_MainPanel,
    ITEMPRO_OT_ResetTransformations,
    ITEMPRO_OT_ResetRotation,
    ITEMPRO_OT_CenterToOrigin,
    ITEMPRO_OT_LockTransformations,
    ITEMPRO_OT_AlignObjects,
    ITEMPRO_OT_StackObjects,
    ITEMPRO_OT_DistributeObjects,
    ITEMPRO_OT_ApplyUniformScale,
    ITEMPRO_OT_ResetScale,
    ITEMPRO_OT_SmoothRotate,
    ITEMPRO_OT_RandomRotate,
    ITEMPRO_OT_CreateArray,
    ITEMPRO_OT_CreateSymmetry,
    ITEMPRO_OT_MirrorObject,
    ITEMPRO_OT_ApplyDimensions,
    ITEMPRO_OT_ResetDimensions,
    ITEMPRO_OT_PlaceOnGround,
    ITEMPRO_OT_SetPivot,
    ITEMPRO_OT_PrecisionTransform,
]


def register():
    # First try to unregister everything
    try:
        unregister()
    except:
        pass

    # Register all classes
    for cls in classes:
        try:
            register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {str(e)}")
            
    # Register properties
    bpy.types.Scene.item_pro_props = bpy.props.PointerProperty(type=ITEMPRO_Properties)

def unregister():
    # Remove properties
    try:
        del bpy.types.Scene.item_pro_props
    except:
        pass

    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {str(e)}")

if __name__ == "__main__":
    register()