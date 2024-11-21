# Copyright (c) 2019 Elie Michel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. In no event shall
# the authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising from,
# out of or in connection with the software or the use or other dealings in the
# Software.
#
# This file is part of MapsModelsImporter, a set of addons to import 3D models
# from Maps services

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator

from .google_maps import importCapture, MapsModelsImportError
from .preferences import getPreferences

class IMP_OP_GoogleMapsCapture(Operator, ImportHelper):
    """Import a capture of a Google Maps frame recorded with RenderDoc"""
    bl_idname = "import_rdc.google_maps"
    bl_label = "Import Google Maps Capture"

    filename_ext = ".rdc"

    filter_glob: StringProperty(
        default="*.rdc",
        options={'HIDDEN'},
        maxlen=1024,  # Max internal buffer length, longer would be clamped.
    )

    max_blocks: IntProperty(
        name="Max Blocks",
        description="Maximum number of draw calls to load",
        default=-1,
    )

    use_experimental: BoolProperty(
        name="Experimental",
        description="Use the new experimental way of extracting draw calls.",
        default=False,
    )

    def execute(self, context):
        pref = getPreferences(context)
        try:
            importCapture(context, self.filepath, self.max_blocks, self.use_experimental, pref)
            error = None
        except MapsModelsImportError as err:
            error = err.args[0]
        if error is not None:
            self.report({'ERROR'}, error)
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(IMP_OP_GoogleMapsCapture.bl_idname, text="Google Maps Capture (.rdc)")


def register():
    bpy.utils.register_class(IMP_OP_GoogleMapsCapture)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(IMP_OP_GoogleMapsCapture)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


# ----- CSV -----
import bpy
import csv
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector

class ImportGeoCSV(bpy.types.Operator, ImportHelper):
    bl_idname = "import_geo.csv"
    bl_label = "Import Geo CSV"
    bl_description = "Import geographic coordinates from a CSV file"
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={'HIDDEN'})

    def execute(self, context):
        filepath = self.filepath
        try:
            self.import_csv(filepath)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            return {'CANCELLED'}

    def import_csv(self, filepath):
        with open(filepath, 'r') as file:
            reader = csv.reader(file)  # Adjust based on your CSV delimiter
            next(reader) #skip header if present

            for row in reader:
                try:
                    lat = float(row[0])
                    lon = float(row[1])
                    #alt = float(row[2]) #optional altitude
                    self.create_blender_object(lat, lon) #add altitude if needed
                except (ValueError, IndexError) as e:
                    self.report({'WARNING'}, f"Skipping invalid row: {row} - {e}")

    def create_blender_object(self, latitude, longitude):
        # Convert latitude/longitude to Blender coordinates (requires a projection)
        # This is a placeholder; you'll need to implement the actual conversion
        # based on your desired projection and coordinate system.
        x, y, z = self.geo_to_blender(latitude, longitude)
        location = Vector((x, y, z))

        # Create an empty object
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        # Or create a marker, mesh, etc. as needed.

    def geo_to_blender(self, latitude, longitude):
        # Implement your geographic coordinate to Blender coordinate conversion here.
        # This will likely involve a map projection (e.g., UTM, Web Mercator).
        # Consider using a library like pyproj for this.
        # Example (replace with your actual projection):
        # from pyproj import Transformer
        # transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857") #Example projection
        # x, y = transformer.transform(longitude, latitude)
        # return x, y, 0 #z=0 for now

        # Placeholder:  Simple conversion (not geographically accurate)
        return longitude, latitude, 0

# TODO: RENAME FUNCTIONS HERE 
def menu_func(self, context):
    self.layout.operator(ImportGeoCSV.bl_idname, text="Geo CSV")

def register():
    bpy.utils.register_class(ImportGeoCSV)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ImportGeoCSV)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()