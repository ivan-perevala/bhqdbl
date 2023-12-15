# BlenderHQ Double precision float property group utility module unit-test utility.
# Copyright (C) 2023 Ivan Perevala (ivpe)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


#####################################################################
# It is ment that this script is started by a third-party unit-test #
#       as a subprocess with a standard Blender startup file        #
#####################################################################

import os
import sys
import unittest
import numpy as np

import bpy
from bpy.types import (
    Camera,
    Object,
    PropertyGroup,
)
from bpy.props import PointerProperty

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import bhqdbl


####################################
# Camera Properties Property Group #
####################################
class CameraProps(PropertyGroup):
    def _cb_get_lens(self) -> float:
        cam: Camera = self.id_data
        return cam.lens

    def _cb_set_lens(self, value: float):
        cam: Camera = self.id_data
        cam.lens = value

    lens, _prop_lens = bhqdbl.double_property(
        "lens",
        name="Lens",
        description="Focal lens with double precision",
        precision=6,
        subtype='DISTANCE_CAMERA',
        get=_cb_get_lens,
        set=_cb_set_lens,
    )

    s_lens: _prop_lens

    k1, _prop_k1 = bhqdbl.double_property(
        "k1",
        name="K1",
        description="First distortion coefficient",
        precision=6,
    )
    s_k1: _prop_k1


class Camera(bpy.types.Camera):
    bd: CameraProps


####################################
# Object Properties Property Group #
####################################
class ObjectProps(PropertyGroup):
    def _get_location(self):
        ob: Object = self.id_data
        return ob.location

    def _set_location(self, value):
        ob: Object = self.id_data
        ob.matrix_world[0][3] = value[0]
        ob.matrix_world[1][3] = value[1]
        ob.matrix_world[2][3] = value[2]

    location = bhqdbl.double_array(
        "location",
        get=_get_location,
        set=_set_location,
        size=3,
        precision=6,
    )

    coeffs = bhqdbl.double_array(
        "coeffs",
        size=4,
    )


class Object(bpy.types.Object):
    bd: ObjectProps


#####################
# Utility Functions #
#####################
def get_local_variables() -> tuple[Object, ObjectProps, Camera, CameraProps]:
    context = bpy.context
    scene = context.scene
    camera: Object = scene.camera
    camera_props = camera.bd
    cam: Camera = camera.data
    cam_props: CameraProps = cam.bd

    return camera, camera_props, cam, cam_props


#########################
# Property Registration #
#########################
def register():
    bpy.utils.register_class(CameraProps)
    bpy.types.Camera.bd = PointerProperty(type=CameraProps)

    bpy.utils.register_class(ObjectProps)
    bpy.types.Object.bd = PointerProperty(type=ObjectProps)


#########
# Tests #
#########
class Test_bhqdbl(unittest.TestCase):
    def test_basic_property(self):
        _camera, _camera_props, _cam, cam_props = get_local_variables()

        attr_name = "k1"
        dbl_val = 0.12345678912345
        sng_val = 0.987654

        # Double precision value
        # The property should not be in the datablok dict if not yet set but must return a default value
        self.assertFalse(attr_name in cam_props)
        self.assertEqual(cam_props.k1, 0.0)
        self.assertFalse(attr_name in cam_props)

        # Single precision value
        # The property should not be in the datablok dict if not yet set but must return a default value
        self.assertFalse(attr_name in cam_props)
        self.assertEqual(cam_props.s_k1, 0.0)
        self.assertFalse(attr_name in cam_props)

        # ---

        # Set the value through property
        cam_props.k1 = dbl_val

        # The attribute should appear in the data block
        self.assertTrue(attr_name in cam_props)

        # Property value must be exactly the same with the set value
        self.assertEqual(cam_props.k1, dbl_val)

        # Datablok property value (single precision) must be approximately the same value
        self.assertAlmostEqual(cam_props.s_k1, dbl_val, places=6)
        # self.assertNotEqual(cam_props.s_k1, dbl_val)

        # Datablok attribute value must be exactly the same
        self.assertEqual(cam_props[attr_name], dbl_val)

        # ---

        # Set the value through datablock property
        cam_props.s_k1 = sng_val

        # The value of the set attribute (single precision) and property (double precision) must approximately match
        # the set value
        self.assertAlmostEqual(cam_props.s_k1, sng_val, places=6)
        self.assertAlmostEqual(cam_props.k1, sng_val, places=6)

    def test_property_with_callbacks(self):
        _camera, _camera_props, cam, cam_props = get_local_variables()

        attr_name = "lens"
        dbl_val = 12.345678912345
        sng_val = 38.5432  # Thats why next would be `places=4`
        default_val = 50.0

        # Check whether the values of the datablok property (double precision) and the attribute (single precision)
        # are equal to the default value. After the first call of the attribute in the datablock must appear the key
        # with the name of the attribute
        self.assertFalse(attr_name in cam_props)
        self.assertEqual(cam_props.lens, default_val)
        self.assertTrue(attr_name in cam_props)
        self.assertEqual(cam_props.s_lens, default_val)

        # ---

        # Set the value through property
        cam_props.lens = dbl_val

        # Property value must be exactly the same with the set value
        self.assertEqual(cam_props.lens, dbl_val)

        # Datablok property value (single precision) must be approximately the same value
        self.assertAlmostEqual(cam_props.lens, dbl_val, places=4)

        # The value in the datablock itself, which is set through the callback, must be approximately equal
        self.assertAlmostEqual(cam_props.lens, dbl_val, places=4)

        # Datablok attribute value must be exactly the same
        self.assertEqual(cam_props[attr_name], dbl_val)

        # ---

        # Set the value through datablock property
        cam_props.s_lens = sng_val

        # The value of the set attribute (single precision), property (double precision) and value in the datablock
        # itself, which is set through the callback must approximately match
        # the set value
        self.assertAlmostEqual(cam_props.s_lens, sng_val, places=4)
        self.assertAlmostEqual(cam_props.lens, sng_val, places=4)
        self.assertAlmostEqual(cam.lens, sng_val, places=4)

    def test_basic_array(self):
        camera, camera_props, _cam, _cam_props = get_local_variables()

        attr_name = "coeffs"

    def test_array_with_callbacks(self):
        _camera, _camera_props, _cam, _cam_props = get_local_variables()


if __name__ == '__main__':
    register()
    unittest.main(verbosity=2, argv=(sys.argv[0],), exit=True)
