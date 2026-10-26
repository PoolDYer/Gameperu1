using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MachuPicchu.Editor
{
    public static class SurveyTerrainImporter
    {
        [Serializable] private class Manifest
        {
            public int schemaVersion, resolution;
            public float widthMeters, lengthMeters, heightMeters;
            public double baseElevationMeters, originEastingMeters, originNorthingMeters;
            public string crs, verticalDatum, rawFile, rawSha256, byteOrder, sampleOrder;
        }
        private static bool Positive(float n) => n > 0 && !float.IsInfinity(n) && !float.IsNaN(n);
        private static bool Finite(double n) => !double.IsInfinity(n) && !double.IsNaN(n);

        [MenuItem("Machu Picchu/Importar terreno medido")]
        public static void Import()
        {
            string file = EditorUtility.OpenFilePanel("Seleccionar terrain.json generado con prepare_dem.py", "", "json");
            if (string.IsNullOrEmpty(file)) return;
            try { ImportFile(file); }
            catch (Exception error) { Debug.LogException(error); EditorUtility.DisplayDialog("No se pudo importar", error.Message, "Cerrar"); }
        }

        public static void ImportFile(string file)
        {
            string json = File.ReadAllText(file);
            Manifest m = JsonUtility.FromJson<Manifest>(json);
            if (m == null || m.schemaVersion != 1 || m.resolution < 33 || m.resolution > 4097 ||
                ((m.resolution - 1) & (m.resolution - 2)) != 0 ||
                !Positive(m.widthMeters) || !Positive(m.lengthMeters) || !Positive(m.heightMeters) ||
                !Finite(m.baseElevationMeters) || !Finite(m.originEastingMeters) || !Finite(m.originNorthingMeters) ||
                string.IsNullOrWhiteSpace(m.crs) || string.IsNullOrWhiteSpace(m.verticalDatum) ||
                m.rawFile != "heightmap.r16" || m.byteOrder != "little-endian" ||
                m.sampleOrder != "south-to-north, west-to-east")
                throw new InvalidDataException("Metadatos inválidos. Usar Tools/prepare_dem.py con unidades métricas verificadas.");
            byte[] bytes = File.ReadAllBytes(Path.Combine(Path.GetDirectoryName(file), m.rawFile));
            if (bytes.Length != checked(m.resolution * m.resolution * 2))
                throw new InvalidDataException("Tamaño de altura incorrecto.");
            using (var sha = SHA256.Create())
                if (!string.Equals(BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(), m.rawSha256, StringComparison.Ordinal))
                    throw new InvalidDataException("La suma SHA256 del relieve no coincide.");
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            var previous = EditorSceneManager.GetSceneManagerSetup();
            string root = "Assets/MachuPicchu/Generated/Survey_" + Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(root);
            AssetDatabase.Refresh();
            try
            {
                float[,] heights = new float[m.resolution, m.resolution];
                for (int z = 0; z < m.resolution; z++)
                    for (int x = 0; x < m.resolution; x++)
                    {
                        int index = (z * m.resolution + x) * 2;
                        heights[z, x] = (bytes[index] | bytes[index + 1] << 8) / 65535f;
                    }
                var data = new TerrainData { heightmapResolution = m.resolution,
                    size = new Vector3(m.widthMeters, m.heightMeters, m.lengthMeters) };
                data.SetHeights(0, 0, heights);
                AssetDatabase.CreateAsset(data, root + "/Terrain.asset");
                // Explicit diagnostic surface; replace with surveyed PBR materials after reference acquisition.
                var texture = new Texture2D(2, 2);
                texture.SetPixels(Enumerable.Repeat(new Color(.42f, .44f, .38f), 4).ToArray());
                texture.Apply();
                AssetDatabase.CreateAsset(texture, root + "/DiagnosticTexture.asset");
                var layer = new TerrainLayer { diffuseTexture = texture, tileSize = new Vector2(5, 5) };
                AssetDatabase.CreateAsset(layer, root + "/DiagnosticLayer.terrainlayer");
                data.terrainLayers = new[] { layer };
                Scene terrainScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                GameObject terrainObject = Terrain.CreateTerrainGameObject(data);
                terrainObject.name = "Survey terrain — local metres — NOT visually reconstructed";
                var provenance = terrainObject.AddComponent<SurveyMetadata>();
                provenance.sourceJson = json;
                provenance.eastingMeters = m.originEastingMeters;
                provenance.northingMeters = m.originNorthingMeters;
                provenance.elevationMeters = m.baseElevationMeters;
                // Local Y = 0 at minimum measured elevation; datum is preserved in metadata.
                string terrainPath = root + "/Terrain.unity";
                Save(terrainScene, terrainPath);

                Scene architectureScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                new GameObject("Architecture — awaiting measured structures");
                string architecturePath = root + "/Architecture.unity";
                Save(architectureScene, architecturePath);

                Scene gameplay = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var sun = new GameObject("Inspection light").AddComponent<Light>();
                sun.type = LightType.Directional; sun.intensity = 1;
                sun.shadows = LightShadows.Soft;
                sun.transform.rotation = Quaternion.Euler(45, -30, 0);
                RenderSettings.ambientLight = new Color(.35f, .35f, .35f);
                var player = new GameObject("Explorer (metres)");
                var controller = player.AddComponent<CharacterController>();
                controller.height = 1.8f; controller.radius = .3f;
                controller.center = new Vector3(0, .9f, 0);
                controller.stepOffset = .25f; controller.slopeLimit = 40;
                var camera = new GameObject("Camera").AddComponent<Camera>();
                camera.tag = "MainCamera"; camera.nearClipPlane = .05f;
                camera.farClipPlane = Mathf.Max(2000, Mathf.Max(m.widthMeters, m.lengthMeters) * 2);
                camera.transform.SetParent(player.transform, false);
                camera.transform.localPosition = new Vector3(0, 1.65f, 0);
                camera.gameObject.AddComponent<AudioListener>();
                player.AddComponent<WalkController>().view = camera.transform;
                float spawnX = .5f, spawnZ = .5f, best = float.PositiveInfinity;
                for (int z = 1; z < 32; z++)
                    for (int x = 1; x < 32; x++)
                    {
                        float u = x / 32f, v = z / 32f;
                        float slope = data.GetSteepness(u, v);
                        if (slope < best) { best = slope; spawnX = u; spawnZ = v; }
                    }
                player.transform.position = new Vector3(spawnX * m.widthMeters,
                    data.GetInterpolatedHeight(spawnX, spawnZ) + .15f, spawnZ * m.lengthMeters);
                if (best > 30) Debug.LogWarning("No se encontró zona suave de inicio. Revisar Spawn antes de jugar.");
                var loader = new GameObject("Scene loader").AddComponent<LoadTerrainScene>();
                loader.terrainScenePath = terrainPath; loader.architectureScenePath = architecturePath;
                loader.player = player;
                string gameplayPath = root + "/Exploration.unity";
                Save(gameplay, gameplayPath);
                var entries = EditorBuildSettings.scenes.ToList();
                entries.AddRange(new[] { gameplayPath, terrainPath, architecturePath }
                    .Select(path => new EditorBuildSettingsScene(path, true)));
                EditorBuildSettings.scenes = entries.ToArray();
                AssetDatabase.SaveAssets();
                Debug.Log("Terreno importado sin exageración vertical: " + root +
                    ". Abrir Exploration.unity. Revisar escala, spawn y colisiones en Unity 6.6.");
            }
            finally
            {
                if (previous.Length > 0 && previous.All(s => !string.IsNullOrEmpty(s.path)))
                    EditorSceneManager.RestoreSceneManagerSetup(previous);
            }
        }
        private static void Save(Scene scene, string path)
        {
            if (!EditorSceneManager.SaveScene(scene, path)) throw new IOException("No se pudo guardar " + path);
        }
    }
}
