using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
namespace MachuPicchu.Editor
{
    public static class ReferenceSectorSceneBuilder
    {
        [MenuItem("Machu Picchu/Crear escena del sector de referencia")]
        public static void Build()
        {
            var model=Resources.Load<GameObject>("MachuPicchu/ReferenceSector_VisualEstimate");
            if (!model) throw new InvalidOperationException("ReferenceSector FBX has not been imported.");
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            string folder="Assets/MachuPicchu/Generated/ReferenceSector_"+Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(folder);AssetDatabase.Refresh();
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var root=UnityEngine.Object.Instantiate(model);root.name="Reference sector — visual estimate, NOT surveyed";
            Bounds bounds=new Bounds();bool first=true;
            foreach (var r in root.GetComponentsInChildren<MeshRenderer>())
            { if(first) {bounds=r.bounds;first=false;} else bounds.Encapsulate(r.bounds); }
            if(first) throw new InvalidOperationException("Imported model has no renderers.");
            foreach(var f in root.GetComponentsInChildren<MeshFilter>())
            { f.gameObject.isStatic=true;f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh; }
            var sun=new GameObject("Sun").AddComponent<Light>();sun.type=LightType.Directional;
            sun.intensity=1.2f;sun.shadows=LightShadows.Soft;sun.transform.rotation=Quaternion.Euler(40,-30,0);
            RenderSettings.ambientLight=new Color(.45f,.48f,.5f);
            // Find ground on the imported geometry rather than assuming FBX axis conversion.
            Physics.SyncTransforms();
            Vector3 rayOrigin=new Vector3(bounds.min.x+4,bounds.max.y+20,bounds.min.z+7);
            if(!Physics.Raycast(rayOrigin,Vector3.down,out var hit,bounds.size.y+100))
                throw new InvalidOperationException("No ground at proposed spawn. Inspect FBX orientation before creating a player.");
            var player=new GameObject("Explorer");player.transform.position=hit.point+Vector3.up*.2f;
            var controller=player.AddComponent<CharacterController>();controller.height=1.8f;controller.radius=.28f;
            controller.center=new Vector3(0,.9f,0);controller.stepOffset=.3f;controller.slopeLimit=48;
            var camera=new GameObject("Main Camera").AddComponent<Camera>();camera.tag="MainCamera";
            camera.transform.SetParent(player.transform,false);camera.transform.localPosition=new Vector3(0,1.65f,0);
            camera.nearClipPlane=.05f;camera.farClipPlane=500;
            camera.gameObject.AddComponent<AudioListener>();
            player.AddComponent<WalkController>().view=camera.transform;
            // Separate visual study; no assertion that all estimated routes are walkable.
            string path=folder+"/ReferenceSector.unity";
            if(!EditorSceneManager.SaveScene(scene,path)) throw new IOException("Unable to save reference scene.");
            var entries=new System.Collections.Generic.List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            entries.Insert(0,new EditorBuildSettingsScene(path,true));EditorBuildSettings.scenes=entries.ToArray();
            if(SceneView.lastActiveSceneView) SceneView.lastActiveSceneView.LookAt(bounds.center,Quaternion.Euler(35,-25,0),bounds.extents.magnitude);
            Debug.Log("Reference study created at "+path+". Ground and architecture are editable mesh sources in Blender. Unity traversal remains to be tested.");
        }
    }
}
