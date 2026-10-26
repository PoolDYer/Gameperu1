using System;
using System.Security.Cryptography;
using UnityEngine;

namespace MachuPicchu
{
    /// <summary>Interpretive prototype only. Geographic details are not surveyed.</summary>
    public sealed class PrototypeWorld : MonoBehaviour
    {
        public bool buildOnAwake = true;
        [Serializable] public class Point { public float x, y, z; }
        [Serializable] public class Layout
        {
            public string kind, rawSha256;
            public int resolution;
            public float widthMeters, lengthMeters, heightMeters;
            public double baseElevationMeters, referenceMeanElevationMeters;
            public Point spawn;
        }
        public Terrain BuiltTerrain { get; private set; }
        public GameObject BuiltPlayer { get; private set; }
        public Layout Specification { get; private set; }

        void Awake() { if (buildOnAwake) Build(); }

        public void Build()
        {
            if (transform.childCount != 0)
                throw new InvalidOperationException("Build into an empty root; existing edits are preserved.");
            TextAsset json = Resources.Load<TextAsset>("MachuPicchu/prototype-layout");
            TextAsset raw = Resources.Load<TextAsset>("MachuPicchu/prototype-heightmap");
            GameObject architecture = Resources.Load<GameObject>("MachuPicchu/Architecture_Interpretive");
            if (!json || !raw || !architecture) throw new InvalidOperationException("Prototype resources missing.");
            var m = JsonUtility.FromJson<Layout>(json.text); Specification = m;
            if (m.kind != "INTERPRETIVE_PROTOTYPE_NOT_SURVEYED" || m.widthMeters != 200 || m.lengthMeters != 530 ||
                m.resolution != 513 || raw.bytes.Length != m.resolution * m.resolution * 2)
                throw new InvalidOperationException("Unexpected prototype dimensions or format.");
            using (var sha = SHA256.Create())
            {
                string actual = BitConverter.ToString(sha.ComputeHash(raw.bytes)).Replace("-", "").ToLowerInvariant();
                if (actual != m.rawSha256) throw new InvalidOperationException("Heightmap checksum mismatch.");
            }
            float[,] heights = new float[m.resolution,m.resolution];
            byte[] bytes = raw.bytes;
            for (int z = 0; z < m.resolution; z++)
                for (int x = 0; x < m.resolution; x++)
                {
                    int i = (z * m.resolution + x) * 2;
                    heights[z,x] = (bytes[i] | (bytes[i+1] << 8)) / 65535f;
                }
            var data = new TerrainData { name = "Interpretive_200x530m", heightmapResolution = m.resolution,
                size = new Vector3(m.widthMeters,m.heightMeters,m.lengthMeters), alphamapResolution = 512 };
            data.SetHeights(0,0,heights);
            var grass = Layer("Grass", new Color(.28f,.34f,.13f), 5);
            var soil = Layer("Soil", new Color(.43f,.34f,.22f), 4);
            var rock = Layer("Rock", new Color(.37f,.39f,.34f), 3);
            data.terrainLayers = new[] { grass,soil,rock };
            int n=data.alphamapResolution; var alpha=new float[n,n,3];
            for (int z=0; z<n; z++) for (int x=0; x<n; x++)
            {
                float u=x/(float)(n-1), v=z/(float)(n-1);
                float worldX=u*m.widthMeters, worldZ=v*m.lengthMeters;
                float centre=100+5*Mathf.Sin(worldZ/125);
                float path=1-SmoothRange(3,6,Mathf.Abs(worldX-centre));
                if (worldZ>228 && worldZ<280) path=Mathf.Max(path,1-SmoothRange(13,17,Mathf.Abs(worldX-100)));
                float steep=SmoothRange(25,50,data.GetSteepness(u,v))*(1-path);
                alpha[z,x,0]=(1-path)*(1-steep); alpha[z,x,1]=path; alpha[z,x,2]=(1-path)*steep;
            }
            data.SetAlphamaps(0,0,alpha);
            var terrainRoot=Terrain.CreateTerrainGameObject(data); terrainRoot.name="Terrain";
            terrainRoot.transform.SetParent(transform,false);
            BuiltTerrain=terrainRoot.GetComponent<Terrain>(); BuiltTerrain.heightmapPixelError=3;
            BuiltTerrain.basemapDistance=700; BuiltTerrain.drawInstanced=true;
            var metadata=terrainRoot.AddComponent<SurveyMetadata>(); metadata.sourceJson=json.text;
            metadata.elevationMeters=m.baseElevationMeters;
            var architectureRoot=Instantiate(architecture,transform); architectureRoot.name="Architecture";
            architectureRoot.transform.localPosition=Vector3.zero;
            // FBX authoring metres and Unity's standard Blender axis conversion are retained.
            foreach (var filter in architectureRoot.GetComponentsInChildren<MeshFilter>())
            {
                filter.gameObject.isStatic=true;
                var collider=filter.gameObject.AddComponent<MeshCollider>(); collider.sharedMesh=filter.sharedMesh;
            }
            var materials=new System.Collections.Generic.Dictionary<string,Material>();
            foreach (var renderer in architectureRoot.GetComponentsInChildren<MeshRenderer>())
            {
                var slots=renderer.sharedMaterials;
                for (int i=0;i<slots.Length;i++)
                {
                    string key=slots[i] ? slots[i].name : "Stone";
                    if (!materials.TryGetValue(key,out var replacement))
                    {
                        Shader shader=Shader.Find("Standard");
                        if (!shader) throw new InvalidOperationException("Open as a Built-in Render Pipeline project.");
                        replacement=new Material(shader) { name=key };
                        bool earth=key.Contains("Earth");
                        replacement.color=Color.white;
                        replacement.mainTexture=SurfaceTexture(key,earth ? new Color(.43f,.34f,.22f) : new Color(.46f,.47f,.42f));
                        replacement.SetFloat("_Glossiness",.12f); materials.Add(key,replacement);
                    }
                    slots[i]=replacement;
                }
                renderer.sharedMaterials=slots;
            }
            var gameplay=new GameObject("Gameplay"); gameplay.transform.SetParent(transform,false);
            var sun=new GameObject("Sun").AddComponent<Light>(); sun.transform.SetParent(gameplay.transform,false);
            sun.type=LightType.Directional; sun.intensity=1.3f; sun.shadows=LightShadows.Soft;
            sun.transform.rotation=Quaternion.Euler(42,-32,0);
            RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor=new Color(.43f,.52f,.65f);
            RenderSettings.ambientEquatorColor=new Color(.35f,.38f,.3f);
            RenderSettings.ambientGroundColor=new Color(.15f,.16f,.12f);
            RenderSettings.fog=true; RenderSettings.fogColor=new Color(.57f,.65f,.7f); RenderSettings.fogDensity=.0006f;
            BuiltPlayer=new GameObject("Explorer"); BuiltPlayer.transform.SetParent(gameplay.transform,false);
            var controller=BuiltPlayer.AddComponent<CharacterController>();
            controller.height=1.8f; controller.radius=.28f; controller.center=new Vector3(0,.9f,0);
            controller.stepOffset=.3f; controller.slopeLimit=48;
            BuiltPlayer.transform.position=new Vector3(m.spawn.x,m.spawn.y,m.spawn.z);
            var camera=new GameObject("Main Camera").AddComponent<Camera>(); camera.tag="MainCamera";
            camera.transform.SetParent(BuiltPlayer.transform,false); camera.transform.localPosition=new Vector3(0,1.65f,0);
            camera.nearClipPlane=.05f; camera.farClipPlane=1800; camera.fieldOfView=65;
            camera.clearFlags=CameraClearFlags.SolidColor; camera.backgroundColor=new Color(.57f,.65f,.72f);
            camera.gameObject.AddComponent<AudioListener>();
            var walk=BuiltPlayer.AddComponent<WalkController>(); walk.view=camera.transform; walk.speed=4;
            var recovery=BuiltPlayer.AddComponent<PrototypePlayerSafety>();
            recovery.spawn=BuiltPlayer.transform.position; recovery.width=m.widthMeters; recovery.length=m.lengthMeters;
            AddBoundary(gameplay.transform,new Vector3(-.5f,50,265),new Vector3(1,200,530));
            AddBoundary(gameplay.transform,new Vector3(200.5f,50,265),new Vector3(1,200,530));
            AddBoundary(gameplay.transform,new Vector3(100,50,-.5f),new Vector3(200,200,1));
            AddBoundary(gameplay.transform,new Vector3(100,50,530.5f),new Vector3(200,200,1));
            buildOnAwake=false;
        }
        static float SmoothRange(float low,float high,float value) => Mathf.SmoothStep(0,1,Mathf.InverseLerp(low,high,value));
        static void AddBoundary(Transform root,Vector3 position,Vector3 size)
        {
            var obj=new GameObject("Extent boundary"); obj.transform.SetParent(root,false); obj.transform.position=position;
            obj.AddComponent<BoxCollider>().size=size;
        }
        static TerrainLayer Layer(string name,Color color,float scale)
        {
            return new TerrainLayer { name=name,diffuseTexture=SurfaceTexture(name,color),tileSize=new Vector2(scale,scale) };
        }
        static Texture2D SurfaceTexture(string name,Color color)
        {
            const int n=128; var texture=new Texture2D(n,n,TextureFormat.RGB24,true) { name=name+"_Procedural",wrapMode=TextureWrapMode.Repeat };
            var colors=new Color[n*n];
            for (int y=0;y<n;y++) for (int x=0;x<n;x++)
            {
                float u=x/(float)n*Mathf.PI*2,v=y/(float)n*Mathf.PI*2;
                float noise=Mathf.PerlinNoise(10+2*Mathf.Sin(u)+2*Mathf.Cos(v),10+2*Mathf.Cos(u)+2*Mathf.Sin(v));
                float fine=Mathf.PerlinNoise(x*.75f,y*.75f);
                colors[y*n+x]=color*(.65f+noise*.5f+fine*.15f);
            }
            texture.SetPixels(colors); texture.Apply(); return texture;
        }
    }
}
