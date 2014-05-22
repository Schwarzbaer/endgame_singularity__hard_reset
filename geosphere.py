# TODO
#   Replace add_base/add_connection by reparse_network_graph(), setting a
#     reference to it on __init__().
# PRETTIFICATION
#   Make better base connections
#     http://gis.stackexchange.com/questions/52949/great-circle-lines-in-equirectangular-projection
#   Move geometry creation/updates into shaders
#   Make surface shaders (sun-vector based blending of day/night shaders

from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomLines, GeomVertexWriter, \
    GeomVertexReader
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import VBase4, Vec3
from direct.task import Task

from math import sqrt, sin, cos, pi
from direct.showbase.DirectObject import DirectObject
from random import random, choice

class Geosphere(DirectObject):
    def __init__(self, res = (32, 16),
                 unwrap_state = 0.0, unwrap_target = 0.0, unwrap_time = 0.4,
                 base_zoom = 0.02, base_zoom_max_dist = 1.0,
                 camera_max_dist = 4.0, camera_min_dist = 0.15, camera_dist = 3.0, ):
        DirectObject.__init__(self)
        self.res = res
        self.unwrap_state = unwrap_state
        self.unwrap_target = unwrap_target
        self.unwrap_time = unwrap_time
        self.base_zoom = base_zoom
        self.base_zoom_max_dist = base_zoom_max_dist
        self.camera_max_dist = camera_max_dist
        self.camera_min_dist = camera_min_dist
        self.camera_dist = camera_dist
        # Bases
        base.taskMgr.add(self.refresh_geosphere, 'refresh_geosphere', sort = 10)
        self.bases = []
        self.connections = []
        # Camera management
        base.camera.set_pos(0, -10, 0)
        base.camera.look_at(0, 0, 0)
        self.camera_position = [0.5, 0.8]
        self.camera_movement = [0.0, 0.0]
        self.camera_distance = 3.0
        self.camera_controlled = False
        
    def move_camera(self, x, y, zoom):
        self.camera_distance += self.camera_distance * zoom * 0.1
        if self.camera_distance < self.camera_min_dist:
            self.camera_distance = self.camera_min_dist
        if self.camera_distance > self.camera_max_dist:
            self.camera_distance = self.camera_max_dist
        self.camera_position[0] = (self.camera_position[0] + x) % 1.0
        self.camera_position[1] += y
        if self.camera_position[1] > 0.9999:
            self.camera_position[1] = 0.9999
        if self.camera_position[1] < 0.0001:
            self.camera_position[1] = 0.0001

    def add_base(self, base):
        np = base.get_nodepath()
        np.reparent_to(self.sphere_np)
        self.bases.append(base)

    def add_connection(self, coord_1, coord_2):
        self.connections.append((coord_1, coord_2))

    def create_node(self):
        # Set up the vertex arrays
        vformat = GeomVertexFormat.get_v3n3c4t2()
        vdata = GeomVertexData("Data", vformat, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        geom = Geom(vdata)

        # Write vertex data
        for v in range(0, self.res[1] + 1):
            for u in range(0, self.res[0] + 1):
                # vertex_number = u * (self.res[0] + 1) + v
                t_u, t_v = float(u)/float(self.res[0]), float(v)/float(self.res[1])
                # Vertex positions and normals will be overwritten before the first displaying anyways.
                vertex.addData3f(0, 0, 0)
                normal.addData3f(0, 0, 0)
                # Color is actually not an issue and should probably be kicked out of here.
                color.addData4f(1, 1, 1, 1)
                # Texcoords are constant, so this should be moved into its own array.
                texcoord.addData2f(t_u, t_v)

        # Add triangles
        for u in range(0, self.res[0]):
            for v in range(0, self.res[1]):
                # The vertex arrangement (y up, x right)
                # 2 3
                # 0 1
                u_verts = self.res[0] + 1
                v_0 = u       + v       * u_verts
                v_1 = (u + 1) + v       * u_verts
                v_2 = u       + (v + 1) * u_verts
                v_3 = (u + 1) + (v + 1) * u_verts
                tris = GeomTriangles(Geom.UHDynamic)
                tris.addVertices(v_2, v_0, v_1)
                tris.closePrimitive()
                geom.addPrimitive(tris)
                tris = GeomTriangles(Geom.UHDynamic)
                tris.addVertices(v_1, v_3, v_2)
                tris.closePrimitive()
                geom.addPrimitive(tris)

        # Create the actual node
        sphere = GeomNode('geom_node')
        sphere.addGeom(geom)
        sphere_np = NodePath(sphere)
        tex = base.loader.loadTexture("assets/geosphere/geosphere_day.jpg")
        sphere_np.setTexture(tex)
        self.sphere_np = sphere_np
        self.sphere_vdata = vdata

        # -----
        vformat = GeomVertexFormat.get_v3n3c4()
        vdata = GeomVertexData("Data", vformat, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        geom = Geom(vdata)
        
        vertex.addData3f(-1, -1, 0)
        color.addData4f(1, 1, 1, 1)

        vertex.addData3f(1, -1, 0)
        color.addData4f(1, 1, 1, 1)

        tris = GeomLines(Geom.UHDynamic)
        tris.addVertices(0, 1)
        tris.closePrimitive()
        geom.addPrimitive(tris)

        connections = GeomNode('geom_node')
        connections.addGeom(geom)
        connections_np = NodePath(connections)
        connections_np.setRenderModeThickness(3)
        self.connections_np = connections_np
        self.connections_vdata = vdata
        self.connections_geom = geom
        
        self.connections_np.reparent_to(sphere_np)

        return sphere_np

    def toggle_unwrap(self):
        if self.unwrap_target == 0.0:
            self.unwrap_target = 1.0
        else:
            self.unwrap_target = 0.0

    def refresh_geosphere(self, task):
        if task.time == 0.0:
            self.update_geometry()
            self.last_time = task.time
        else:
            dt = task.time - self.last_time
            self.last_time = task.time
            if self.unwrap_state != self.unwrap_target:
                # Adjust unwrap_state
                if self.unwrap_target < self.unwrap_state:
                    self.unwrap_state -= dt / self.unwrap_time
                    if self.unwrap_state < 0.0:
                        self.unwrap_state = 0.0
                else:
                    self.unwrap_state += dt / self.unwrap_time
                    if self.unwrap_state > 1.0:
                        self.unwrap_state = 1.0
                # Redraw the mesh
                self.update_geometry()

        for base_g in self.bases:
            vertex, normal = self.uv_to_xyz(base_g.get_coordinates()[0], base_g.get_coordinates()[1])
            (v_x, v_y, v_z) = vertex
            (n_x, n_y, n_z) = normal
            np = base_g.get_nodepath()
            if self.camera_distance > self.base_zoom_max_dist:
                base_dist = self.base_zoom_max_dist
            else:
                base_dist = self.camera_distance
            np.set_scale(base_dist * self.base_zoom)
            np.set_pos(v_x, v_y, v_z)
            np.look_at(v_x + n_x, v_y + n_y, v_z + n_z)
            #np.set_color(1,0,0,1)

        (v_x_c, v_y_c, v_z_c), (n_x_c, n_y_c, n_z_c) = self.uv_to_xyz(self.camera_position[0], self.camera_position[1])
        base.camera.set_pos(v_x_c + n_x_c * self.camera_distance,
                            v_y_c + n_y_c * self.camera_distance,
                            v_z_c + n_z_c * self.camera_distance)
        base.camera.look_at(v_x_c, v_y_c, v_z_c)

        return Task.cont

    def update_geometry(self):
        # The geosphere itself
        vertex = GeomVertexWriter(self.sphere_vdata, 'vertex')
        normal = GeomVertexWriter(self.sphere_vdata, 'normal')
        # u_map and v_map are in [-pi, pi]
        u_map_list = [(float(u) / float(self.res[0]) - 0.5) * 2.0 * pi for u in range(0, self.res[0] + 1)]
        v_map_list = [(float(v) / float(self.res[1]) - 0.5) * 2.0 * pi for v in range(0, self.res[1] + 1)]
        if self.unwrap_state == 0.0: # Flat map
            for v_map in v_map_list:
                for u_map in u_map_list:
                    vertex.addData3f(u_map, 0.0, v_map / 2.0)
                    normal.addData3f(0.0, -1.0, 0.0)
        else: # Non-flat map
            sphere_radius = 1.0 / self.unwrap_state
            sphere_offset = sphere_radius - self.unwrap_state
            for v_map in v_map_list:
                for u_map in u_map_list:
                    u_sphere = u_map / sphere_radius
                    v_sphere = v_map / sphere_radius
                    # And this, kids, is why you should pay attention in trigonometry.
                    v_x, v_y, v_z = sin(u_sphere) * cos(v_sphere/2.0) * sphere_radius, \
                                    -cos(u_sphere) * cos(v_sphere/2.0) * sphere_radius + sphere_offset, \
                                    sin(v_sphere / 2.0) * sphere_radius
                    n_x_un, n_y_un, n_z_un = v_x, sphere_offset - v_y, v_z # FIXME: This is a lie.
                    length = sqrt(n_x_un**2 + n_y_un**2 + n_z_un**2)
                    n_x, n_y, n_z = n_x_un / length, n_y_un / length, n_z_un / length
                    vertex.addData3f(v_x, v_y, v_z)
                    normal.addData3f(n_x, n_y, n_z)
                    
        # The connections between bases
        segs_per_connection = 30
        vertex = GeomVertexWriter(self.connections_vdata, 'vertex')
        color = GeomVertexWriter(self.connections_vdata, 'color')
        for c_1_uv, c_2_uv in self.connections:
            # s will be [0.0, 1.0]
            for s in [float(c)/float(segs_per_connection+1) for c in range(0, segs_per_connection+2)]:
                u = (c_1_uv[0] * s) + (c_2_uv[0] * (1.0 - s))
                v = (c_1_uv[1] * s) + (c_2_uv[1] * (1.0 - s))
                (v_x, v_y, v_z), (n_x, n_y, n_z) = self.uv_to_xyz(u, v)
                min_height = 0.0001 * (1.0 - self.unwrap_state)
                max_height = (0.2 - min_height) * self.unwrap_state
                seg_height = (1.0 - (abs(s-0.5) * 2.0)**2.0) * max_height + min_height
                vertex.addData3f(v_x + n_x*seg_height,
                                 v_y + n_y*seg_height,
                                 v_z + n_z*seg_height)
                color.addData4f(1, 1, 1, 1)
        for c in range(0, len(self.connections)):
            for s in range(0, segs_per_connection+1):
                seg = GeomLines(Geom.UHDynamic)
                seg.addVertices(c*(segs_per_connection+2) + s, c*(segs_per_connection+2) + s + 1)
                seg.closePrimitive()
                self.connections_geom.addPrimitive(seg)

    def uv_to_xyz(self, u, v):
        u_r = (u - 0.5) * 2.0 * pi
        v_r = (v - 0.5) * 2.0 * pi
        if self.unwrap_state == 0.0: # Flat map
            vertex = (u_r, 0.0, v_r / 2.0)
            normal = (0.0, -1.0, 0.0)
        else: # Non-flat map
            sphere_radius = 1.0 / self.unwrap_state
            sphere_offset = sphere_radius - self.unwrap_state
            u_sphere = u_r / sphere_radius
            v_sphere = v_r / sphere_radius
            # And this, kids, is why you should pay attention in trigonometry.
            vertex = (sin(u_sphere) * cos(v_sphere/2.0) * sphere_radius,
                      -cos(u_sphere) * cos(v_sphere/2.0) * sphere_radius + sphere_offset,
                      sin(v_sphere / 2.0) * sphere_radius)
            normal_unnormalized = (vertex[0], -sphere_offset + vertex[1], vertex[2])
            length = sqrt(normal_unnormalized[0]**2 + normal_unnormalized[1]**2 + normal_unnormalized[2]**2)
            normal = (normal_unnormalized[0] / length, normal_unnormalized[1] / length, normal_unnormalized[2] / length)
        return (vertex, normal)

