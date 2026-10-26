using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MachuPicchu.Editor
{
    public static class PrototypeSceneBuilder
    {
        [MenuItem("Machu Picchu/Crear escenas editables del prototipo")]
        public static void BuildEditableScenes()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            string root="Assets/MachuPicchu/Generated/Prototype_"+Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(root); AssetDatabase.Refresh();
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var world=new GameObject("Interpretive prototype — not surveyed").AddComponent<PrototypeWorld>();
            world.Build();
            var persisted=new HashSet<int>();
            Action<UnityEngine.Object,string> save=(asset,name)=>
            {
                if (asset && !AssetDatabase.Contains(asset) && persisted.Add(asset.GetInstanceID()))
                    AssetDatabase.CreateAsset(asset,AssetDatabase.GenerateUniqueAssetPath(root+"/"+name+".asset"));
            };
            foreach (var layer in world.BuiltTerrain.terrainData.terrainLayers)
            { save(layer.diffuseTexture,layer.name+"Texture"); save(layer,layer.name+"Layer"); }
            save(world.BuiltTerrain.terrainData,"Terrain");
            foreach (var renderer in world.GetComponentsInChildren<MeshRenderer>())
                foreach (var material in renderer.sharedMaterials)
                { if (!material) continue; save(material.mainTexture,material.name+"Texture"); save(material,material.name); }
            var terrain=world.transform.Find("Terrain").gameObject;
            var architecture=world.transform.Find("Architecture").gameObject;
            var gameplay=world.transform.Find("Gameplay").gameObject;
            terrain.transform.SetParent(null,true); architecture.transform.SetParent(null,true); gameplay.transform.SetParent(null,true);
            var player=world.BuiltPlayer;
            UnityEngine.Object.DestroyImmediate(world.gameObject);
            var terrainScene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
            SceneManager.MoveGameObjectToScene(terrain,terrainScene);
            string terrainPath=root+"/Terrain.unity";
            if (!EditorSceneManager.SaveScene(terrainScene,terrainPath)) throw new IOException("Could not save Terrain scene.");
            var architectureScene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
            SceneManager.MoveGameObjectToScene(architecture,architectureScene);
            string architecturePath=root+"/Architecture.unity";
            if (!EditorSceneManager.SaveScene(architectureScene,architecturePath)) throw new IOException("Could not save Architecture scene.");
            var loader=gameplay.AddComponent<LoadTerrainScene>(); loader.player=player;
            loader.terrainScenePath=terrainPath; loader.architectureScenePath=architecturePath;
            string explorePath=root+"/Exploration.unity";
            if (!EditorSceneManager.SaveScene(scene,explorePath)) throw new IOException("Could not save Exploration scene.");
            var settings=new List<EditorBuildSettingsScene> {
                new EditorBuildSettingsScene(explorePath,true),new EditorBuildSettingsScene(terrainPath,true),new EditorBuildSettingsScene(architecturePath,true) };
            foreach (var entry in EditorBuildSettings.scenes) settings.Add(entry);
            EditorBuildSettings.scenes=settings.ToArray(); AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(explorePath,OpenSceneMode.Single);
            Debug.Log("Editable prototype saved: "+root+". Extent 200 x 530 metres. Layout is interpretive, not surveyed.");
        }
    }
}
