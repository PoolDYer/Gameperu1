using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace MachuPicchu.Editor
{
    public static class ReferenceSectorSceneBuilder
    {
        [MenuItem("Machu Picchu/Crear escena del sector de referencia")]
        public static void Build()
        {
            if(!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())return;
            string folder="Assets/MachuPicchu/Generated/ReferenceSector_"+Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(folder);AssetDatabase.Refresh();
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var world=new GameObject("Reference sector — NOT surveyed").AddComponent<ReferenceSectorWorld>();
            world.Build();Bounds bounds=world.ModelBounds;
            string path=folder+"/ReferenceSector.unity";
            if(!EditorSceneManager.SaveScene(scene,path))throw new IOException("Unable to save reference scene.");
            var entries=new System.Collections.Generic.List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            entries.Insert(0,new EditorBuildSettingsScene(path,true));EditorBuildSettings.scenes=entries.ToArray();
            if(SceneView.lastActiveSceneView)SceneView.lastActiveSceneView.LookAt(bounds.center,Quaternion.Euler(35,-25,0),bounds.extents.magnitude);
            Debug.Log("Reference scene saved to "+path+". Geometry is estimated; Unity traversal must be tested.");
        }
    }
}
