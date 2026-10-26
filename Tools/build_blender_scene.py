"""Build an editable interpretive .blend and Unity FBX from prototype-layout.json."""
import bpy, json, math, random, struct, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'Assets/Resources/MachuPicchu'
MODELS = ROOT/'Assets/Resources/MachuPicchu'
ART = ROOT/'Artifacts'
m = json.loads((DATA/'prototype-layout.json').read_text())
N=m['resolution']; W=m['widthMeters']; L=m['lengthMeters']; H=m['heightMeters']
raw=struct.unpack('<'+'H'*(N*N),(DATA/'prototype-heightmap.bytes').read_bytes())
rng=random.Random(m['seed'])
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials): bpy.data.materials.remove(x)

def material(name,color,roughness=.9):
    mat=bpy.data.materials.new(name); mat.diffuse_color=(*color,1); mat.use_nodes=True
    tree=mat.node_tree; shader=tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1); shader.inputs['Roughness'].default_value=roughness
    tex=tree.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=7; tex.inputs['Detail'].default_value=4
    coord=tree.nodes.new('ShaderNodeTexCoord'); tree.links.new(coord.outputs['Object'],tex.inputs['Vector'])
    bump=tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.3; bump.inputs['Distance'].default_value=.075
    tree.links.new(tex.outputs['Fac'],bump.inputs['Height']); tree.links.new(bump.outputs['Normal'],shader.inputs['Normal'])
    ramp=tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(*(c*.62 for c in color),1)
    ramp.color_ramp.elements[1].color=(*(min(1,c*1.22) for c in color),1)
    tree.links.new(tex.outputs['Fac'],ramp.inputs[0]); tree.links.new(ramp.outputs[0],shader.inputs['Base Color'])
    return mat
stone=[material('Granite_'+str(i),(.32+i*.025,.325+i*.023,.29+i*.02)) for i in range(5)]
grass=material('Grass_interpretive',(.23,.30,.105)); dirt=material('Earth_interpretive',(.38,.285,.17)); rock=material('Rock_interpretive',(.31,.32,.28))
architecture=[]

class MeshBuilder:
    def __init__(self): self.verts=[]; self.faces=[]; self.indices=[]
    def box(self,cx,cy,cz,sx,sy,sz,mat=0):
        n=len(self.verts)
        for z in (-1,1):
            for y in (-1,1):
                for x in (-1,1): self.verts.append((cx+x*sx/2,cy+y*sy/2,cz+z*sz/2))
        for face in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)):
            self.faces.append(tuple(n+i for i in face)); self.indices.append(mat)
    def object(self,name,materials,location=(0,0,0)):
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(self.verts,[],self.faces); mesh.materials.clear()
        for mat in materials: mesh.materials.append(mat)
        mesh.update()
        obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.location=location
        for p,idx in zip(mesh.polygons,self.indices): p.material_index=idx
        uv=mesh.uv_layers.new(name='UVMap')
        for face in mesh.polygons:
            normal=face.normal
            axis=max(range(3),key=lambda i:abs(normal[i])); axes=[i for i in range(3) if i!=axis]
            for loop_index in face.loop_indices:
                v=mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv=(v[axes[0]],v[axes[1]])
        obj['accuracy']='Interpretive approximation; not surveyed'
        return obj

def yheight(x,z):
    ix=max(0,min(N-1,round(x/W*(N-1)))); iz=max(0,min(N-1,round(z/L*(N-1))))
    return raw[iz*N+ix]/65535*H

def stone_wall(builder,x0,z0,x1,z1,height,door=False):
    length=math.hypot(x1-x0,z1-z0); vertical=abs(x1-x0)<.001
    courses=max(1,round(height/.39)); course=height/courses
    for j in range(courses):
        distance=0
        while distance<length-.02:
            width=min(rng.uniform(.65,1.25),length-distance)
            mid=distance+width/2
            if not door or j*course>2.05 or abs(mid-length/2)>1.05:
                x=x0+(x1-x0)*mid/length; z=z0+(z1-z0)*mid/length
                a=max(.03,width-.018); b=.54+rng.uniform(-.02,.02)
                builder.box(x,z,j*course+course/2,b if vertical else a,a if vertical else b,course-.015,rng.randrange(5))
            distance+=width
    if door:
        builder.box((x0+x1)/2,(z0+z1)/2,2.23,.58 if vertical else 2.7,2.7 if vertical else .58,.36,2)

for b in m['buildings']:
    mesh=MeshBuilder(); w=b['width']; d=b['depth']; h=b['wallHeight']
    # Door faces the long central pedestrian axis.
    right=b['x']<100
    stone_wall(mesh,-w/2,-d/2,w/2,-d/2,h)
    stone_wall(mesh,-w/2,d/2,w/2,d/2,h)
    stone_wall(mesh,-w/2,-d/2,-w/2,d/2,h,not right)
    stone_wall(mesh,w/2,-d/2,w/2,d/2,h,right)
    mesh.box(0,0,.025,w,d,.10,5)
    obj=mesh.object(b['id'],stone+[dirt],(b['x'],b['z'],b['y']))
    obj['recinto_index']=b['id']; architecture.append(obj)

# Long retaining walls articulate the stepped terrain; central openings allow transverse access.
for side in (-1,1):
    for terrace in range(1,8):
        mesh=MeshBuilder()
        for segment in range(90):
            z=8+segment*5.7
            if z>L-8 or any(abs(z-cross)<4 for cross in (88,180,265,350,440)): continue
            x=100+5*math.sin(z/125)+side*(38+terrace*7)
            low=yheight(x+side*.9,z); high=yheight(x-side*.9,z)
            base=min(low,high)-.5
            height=max(.8,abs(high-low)+.5)
            for course in range(max(1,round(height/.4))):
                mesh.box(x,z,base+course*.4+.2,.6,5.65,.385,rng.randrange(5))
        obj=mesh.object(f'Terrace_{side}_{terrace}',stone); architecture.append(obj)

# Separate stair treads fill the recessed cross-terrace corridors.
for crossing in (88,180,265,350,440):
    for side in (-1,1):
        mesh=MeshBuilder()
        inner=100+5*math.sin(crossing/125)+side*39
        outer=100+5*math.sin(crossing/125)+side*88
        steps=90
        for step in range(steps):
            x=inner+(outer-inner)*(step+.5)/steps
            top=yheight(x,crossing)+.24
            mesh.box(x,crossing,top-.18,abs(outer-inner)/steps+.02,3.1,.36,step%5)
        obj=mesh.object(f'Stairs_{crossing}_{side}',stone); architecture.append(obj)

# Curved-wall study from the supplied figure; its location and dimensions are interpretive.
t=m['tower']; mesh=MeshBuilder()
for course in range(9):
    for i in range(40):
        angle=-math.pi*.1+i/39*math.pi*1.4
        radius=t['radius']; cx=math.cos(angle)*radius; cy=math.sin(angle)*radius
        # Four vertices rotated about the tower centre give a continuous masonry arc.
        start=len(mesh.verts)
        mesh.box(cx,cy,3.5+course*.4,.64,.6,.385,(i+course)%5)
        for index in range(start,len(mesh.verts)):
            x,y,z=mesh.verts[index]; dx=x-cx; dy=y-cy
            mesh.verts[index]=(cx+dx*math.cos(angle)-dy*math.sin(angle),cy+dx*math.sin(angle)+dy*math.cos(angle),z)
obj=mesh.object('Torreon_interpretative_curved_wall',stone,(t['x'],t['z'],t['y'])); architecture.append(obj)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=(t['x'],t['z'],t['y']+1.3))
obj=bpy.context.object; obj.name='Torreon_interpretative_bedrock'; obj.scale=(7,6,3.7); obj.data.materials.append(rock)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); architecture.append(obj)

# Terrain as a true editable mesh in Blender; Unity uses the full-resolution native TerrainData.
mesh=MeshBuilder(); stride=2; size=(N-1)//stride+1
for j in range(0,N,stride):
    for i in range(0,N,stride): mesh.verts.append((i/(N-1)*W,j/(N-1)*L,raw[j*N+i]/65535*H))
for j in range(size-1):
    for i in range(size-1):
        v=j*size+i; mesh.faces.append((v,v+1,v+size+1,v+size)); mesh.indices.append(0)
terrain=mesh.object('Terrain_200x530m_INTERPRETIVE', [grass,dirt,rock])
for p in terrain.data.polygons:
    c=p.center; centre=100+5*math.sin(c.y/125)
    if abs(c.x-centre)<5 or 228<c.y<280 and abs(c.x-100)<16: p.material_index=1
    elif p.normal.z<.78: p.material_index=2
for polygon in terrain.data.polygons: polygon.use_smooth=True

# Geometry checks operate on actual mesh coordinates before exporting.
assert len([o for o in architecture if o.name.startswith('Recinto_interpretativo_')])==172
assert abs(terrain.dimensions.x-W)<.001 and abs(terrain.dimensions.y-L)<.001
for obj in architecture:
    assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
    obj.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for obj in architecture: obj.select_set(True)
bpy.context.view_layer.objects.active=architecture[0]
MODELS.mkdir(parents=True,exist_ok=True); ART.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(MODELS/'Architecture_Interpretive.fbx'),use_selection=True,
    object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
    add_leaf_bones=False,bake_anim=False,path_mode='AUTO',use_mesh_modifiers=True)

# Keep an editable native source and a real render of the generated geometry.
world=bpy.data.worlds.new('Sky') if not bpy.data.worlds else bpy.data.worlds[0]
bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.43,.55,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.45
bpy.ops.object.light_add(type='SUN',location=(120,40,180)); sun=bpy.context.object; sun.name='Sun'
sun.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-30)); sun.data.energy=3; sun.data.angle=.12
bpy.ops.object.camera_add(location=(590,-365,455)); cam=bpy.context.object; cam.name='Overview'
cam.rotation_euler=(Vector((100,255,27))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=640
scene=bpy.context.scene; scene.camera=cam; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.render.engine='CYCLES'; scene.cycles.samples=40; scene.cycles.use_denoising=False
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(ART/'Overview_INTERPRETIVE.png')
scene['source_warning']='Approximate model; terrain and 172 layouts are invented, not measured Machu Picchu.'
scene['footprint_meters']='200 x 530'; scene['reference_mean_elevation_m']=2430
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'MachuPicchu_Interpretive.blend'))
report=dict(buildingCount=172,architectureMeshObjects=len(architecture),
            architectureVertices=sum(len(o.data.vertices) for o in architecture),
            terrainVertices=len(terrain.data.vertices), terrainWidth=terrain.dimensions.x,
            terrainLength=terrain.dimensions.y, accuracy='interpretive, not surveyed')
(ART/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('VALIDATION',json.dumps(report),flush=True)
bpy.ops.render.render(write_still=True)
