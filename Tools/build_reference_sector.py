"""Visual reconstruction study of the tower reference. Dimensions are estimated, not surveyed."""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Assets/Resources/MachuPicchu'; ART=ROOT/'Artifacts'
rng=random.Random(2829)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.92
 coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=5
 l.new(coord.outputs['Object'],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB')
 r.color_ramp.elements[0].color=(*(c*.6 for c in color),1);r.color_ramp.elements[1].color=(*(min(1,c*1.3) for c in color),1)
 l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.055
 l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);return m
stone=[material('Sector_granite_'+str(i),(.31+i*.025,.33+i*.024,.28+i*.021)) for i in range(6)]
earth=material('Sector_earth',(.46,.37,.23));grass=material('Sector_grass',(.28,.36,.12));rock=material('Sector_bedrock',(.34,.35,.31))
class Mesh:
 def __init__(self):self.v=[];self.f=[];self.mat=[]
 def box(self,x,y,z,w,d,h,angle=0,idx=None,irregular=.02):
  start=len(self.v);c=math.cos(angle);s=math.sin(angle)
  for dz in (-1,1):
   for dy in (-1,1):
    for dx in (-1,1):
     u=dx*w/2+rng.uniform(-irregular,irregular);v=dy*d/2+rng.uniform(-irregular,irregular)
     self.v.append((x+c*u-s*v,y+s*u+c*v,z+dz*h/2+rng.uniform(-irregular,irregular)))
  idx=rng.randrange(6) if idx is None else idx
  for face in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)):
   self.f.append(tuple(start+i for i in face));self.mat.append(idx)
 def object(self,name,mats=stone):
  mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.v,[],self.f);mesh.update()
  obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
  for m in mats:mesh.materials.append(m)
  for p,i in zip(mesh.polygons,self.mat):p.material_index=i
  uv=mesh.uv_layers.new(name='UVMap')
  for p in mesh.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
   for j in p.loop_indices:
    co=mesh.vertices[mesh.loops[j].vertex_index].co;uv.data[j].uv=(co[axes[0]],co[axes[1]])
  obj['accuracy']='Visual estimate from Figure 10, not surveyed'
  return obj

def wall(name,a,b,base,height,thickness=.65,doors=(),niches=(),fine=False):
 mesh=Mesh();dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);angle=math.atan2(dy,dx)
 course=.33 if fine else .42;rows=math.ceil(height/course)
 for row in range(rows):
  dist=0
  while dist<length-.05:
   width=min(rng.uniform(.65,1.15) if fine else rng.uniform(.45,.95),length-dist)
   mid=dist+width/2;z=base+row*course+course/2
   is_door=any(abs(mid-centre)<1 and z<base+2.25 for centre in doors)
   niche=any(abs(mid-centre)<.55 and base+1.15<z<base+2.5 for centre in niches)
   if not is_door:
    depth=thickness*.35 if niche else thickness
    offset=thickness*.325 if niche else 0
    mesh.box(a[0]+dx*mid/length-math.sin(angle)*offset,a[1]+dy*mid/length+math.cos(angle)*offset,
             z,width-.025,depth,course-.022,angle,irregular=.008 if fine else .045)
   dist+=width
 for centre in doors:mesh.box(a[0]+dx*centre/length,a[1]+dy*centre/length,base+2.4,2.5,thickness+.08,.34,angle,irregular=.01)
 return mesh.object(name)

def room(name,x,y,w,d,base,height,door=True):
 floor=Mesh();floor.box(x,y,base-.08,w,d,.16,idx=0,irregular=0);floor.object(name+'_floor',[earth])
 wall(name+'_front',(x-w/2,y-d/2),(x+w/2,y-d/2),base,height,doors=(w/2,) if door else ())
 wall(name+'_rear',(x-w/2,y+d/2),(x+w/2,y+d/2),base,height,niches=tuple(range(2,int(w),2)))
 wall(name+'_west',(x-w/2,y-d/2),(x-w/2,y+d/2),base,height)
 wall(name+'_east',(x+w/2,y-d/2),(x+w/2,y+d/2),base,height)

# Sampled multi-level ground. Levels derived visually; not absolute topographic elevations.
def elevation(x,y):
 z=.10*y
 if y>8:z+=1.4
 if y>17:z+=1.4
 if y>28:z+=1.8
 if y>36:z+=1.0
 z+=.3*math.sin(x*.24)
 for px,py,w,d,base in [(8,33,9,12,8.5),(8,21,9,8,5),(10,12,12,6,3),(36,34,12,11,8.7),(34,21,9,10,5.3)]:
  if abs(x-px)<w/2+.3 and abs(y-py)<d/2+.3: z=base-.18
 if 44<x<48.2 and 4.5<y<37.5:z=(y-5)*.36-.25
 return z
mesh=Mesh();n=161
for j in range(n):
 for i in range(n):
  x=i*50/(n-1);y=j*44/(n-1);mesh.v.append((x,y,elevation(x,y)))
for j in range(n-1):
 for i in range(n-1):
  k=j*n+i;mesh.f.append((k,k+1,k+n+1,k+n));mesh.mat.append(1 if j>n*.8 and i<n*.7 else 0)
mesh.object('Sector_ground_50x44m_estimate',[earth,grass])
# Foreground terrace and rear retaining platforms.
wall('Foreground_containment',(1,5),(40,5),.1,3.4,.9)
wall('Lower_right_containment',(39,5),(44,18),.5,4.1,.9)
wall('Rear_platform',(2,34),(42,34),5,3.8,.8)
room('Upper_west',8,33,9,12,8.5,5)
room('West_middle',8,21,9,8,5,3.6)
room('West_lower',10,12,12,6,3,2.8)
room('Upper_east',36,34,12,11,8.7,4.5)
room('Lower_east',34,21,9,10,5.3,3.1)
wall('Rear_niche_gallery',(12,41),(42,41),9,4,.7,niches=tuple(range(2,29,2)),fine=True)
# Irregular bedrock: rings taper and shift to form an exposed inclined rock face.
mesh=Mesh();rings=[(2.2,7.8,7.4,-.8),(5.5,7,6.2,-.3),(9.5,5.9,5.5,0),(11.2,5.7,5.2,.1)]
count=36
for level,(z,rx,ry,shift) in enumerate(rings):
 for i in range(count):
  a=2*math.pi*i/count;r=1+rng.uniform(-.09,.09)
  mesh.v.append((23+math.cos(a)*rx*r,24+shift+math.sin(a)*ry*r,z+rng.uniform(-.3,.3)))
for j in range(len(rings)-1):
 for i in range(count):
  mesh.f.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i));mesh.mat.append(0)
mesh.f.append(tuple(range((len(rings)-1)*count,len(rings)*count)));mesh.mat.append(0)
mesh.object('Tower_inclined_bedrock',[rock])
# U-shaped finely cut masonry atop the rock; open interior, no invented roof.
mesh=Mesh();radius=5.8;segments=30;courses=12
for row in range(courses):
 for i in range(segments):
  a=math.pi+(i+.5)/segments*math.pi
  # Tangential block length follows the curvature.
  mesh.box(23+radius*math.cos(a),24+radius*math.sin(a),11.2+row*.34+.17,
           radius*math.pi/segments-.012,.7,.325,a+math.pi/2,irregular=.008)
mesh.object('Tower_curved_ashlar_wall')
wall('Tower_west_return',(17.2,24),(17.2,30),11.2,4.08,.7,fine=True)
wall('Tower_east_return',(28.8,24),(28.8,30),11.2,4.08,.7,doors=(3,),fine=True)
wall('Tower_rear',(17.2,30),(28.8,30),11.2,3.7,.7,niches=(2.5,5.8,9),fine=True)
floor=Mesh();floor.box(23,25.5,11.12,10.8,8,.12,idx=0,irregular=0);floor.object('Tower_interior_platform',[earth])
# Main right stair rises through multiple terraces; rise .18m, tread .5m.
mesh=Mesh()
for i in range(64):
 top=.18*(i+1);bottom=min(elevation(46,5+i*.5)-.2,top-.3);mesh.box(46,5+i*.5,(top+bottom)/2,3.8,.51,top-bottom,irregular=.012)
mesh.object('East_main_stair_64_steps')
wall('Stair_outer_lower',(48.2,4),(48.2,18),0,2.5,.75)
wall('Stair_outer_upper',(48.2,24),(48.2,40),5.7,4.9,.75)
mesh=Mesh()
for i in range(20):
 top=3.5+i*.19;bottom=min(elevation(15,14+i*.36)-.2,top-.3);mesh.box(15,14+i*.36,(top+bottom)/2,2,.37,top-bottom,irregular=.01)
mesh.object('Tower_west_access_steps')
# Reference study export: all architecture and topography are editable meshes.
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
OUT.mkdir(exist_ok=True,parents=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'ReferenceSector_VisualEstimate.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
world=bpy.data.worlds.new('Reference_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.37,.43,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene=bpy.context.scene;scene.world=world;scene.unit_settings.system='METRIC'
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.5,-.4,-.6);sun.data.energy=2.7;sun.data.angle=.15
bpy.ops.object.camera_add(location=(57,-66,61));camera=bpy.context.object;camera.rotation_euler=(Vector((25,24,7))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=65;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.render.resolution_x=1400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'ReferenceSector_VisualEstimate.png')
scene['status']='Partial visual reconstruction study, not measured or complete Machu Picchu'
report=dict(status=scene['status'],meshObjects=len(objects),vertices=sum(len(o.data.vertices) for o in objects),groundExtentMeters=[50,44],towerWallBaseMeters=11.2,towerWallTopMeters=15.28,units='metres, estimated',source='User PDF figure 10 plus panoramic visual references')
(ART/'reference-sector-validation.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'ReferenceSector_VisualEstimate.blend'))
bpy.ops.render.render(write_still=True)
