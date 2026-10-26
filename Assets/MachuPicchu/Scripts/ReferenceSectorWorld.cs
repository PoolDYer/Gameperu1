using System;
using UnityEngine;
namespace MachuPicchu
{
    public sealed class ReferenceSectorWorld : MonoBehaviour
    {
        public bool buildOnAwake=true;
        public Bounds ModelBounds { get; private set; }
        void Awake() { if(buildOnAwake) Build(); }
        public void Build()
        {
            if(transform.childCount!=0) throw new InvalidOperationException("Use an empty scene root; edits are preserved.");
            var model=Resources.Load<GameObject>("MachuPicchu/ReferenceSector_VisualEstimate");
            if(!model) throw new InvalidOperationException("Reference-sector model is missing.");
            var architecture=Instantiate(model,transform);architecture.name="Reference sector — estimated geometry";
            Bounds bounds=new Bounds();bool first=true;
            foreach(var renderer in architecture.GetComponentsInChildren<MeshRenderer>())
            { if(first){bounds=renderer.bounds;first=false;}else bounds.Encapsulate(renderer.bounds); }
            if(first) throw new InvalidOperationException("Reference-sector model has no renderers.");
            ModelBounds=bounds;
            foreach(var mesh in architecture.GetComponentsInChildren<MeshFilter>())
            {mesh.gameObject.isStatic=true;mesh.gameObject.AddComponent<MeshCollider>().sharedMesh=mesh.sharedMesh;}
            var sun=new GameObject("Sun").AddComponent<Light>();sun.transform.SetParent(transform,false);
            sun.type=LightType.Directional;sun.intensity=1.2f;sun.shadows=LightShadows.Soft;sun.transform.rotation=Quaternion.Euler(40,-30,0);
            RenderSettings.ambientLight=new Color(.45f,.48f,.5f);
            Physics.SyncTransforms();
            Vector3 origin=new Vector3(bounds.min.x+4,bounds.max.y+20,bounds.min.z+7);
            if(!Physics.Raycast(origin,Vector3.down,out var hit,bounds.size.y+100))
                throw new InvalidOperationException("No ground at proposed start. Inspect model orientation.");
            var player=new GameObject("Explorer");player.transform.SetParent(transform,false);player.transform.position=hit.point+Vector3.up*.2f;
            var controller=player.AddComponent<CharacterController>();controller.height=1.8f;controller.radius=.28f;
            controller.center=new Vector3(0,.9f,0);controller.stepOffset=.3f;controller.slopeLimit=48;
            var camera=new GameObject("Main Camera").AddComponent<Camera>();camera.tag="MainCamera";
            camera.transform.SetParent(player.transform,false);camera.transform.localPosition=new Vector3(0,1.65f,0);
            camera.nearClipPlane=.05f;camera.farClipPlane=500;camera.gameObject.AddComponent<AudioListener>();
            player.AddComponent<WalkController>().view=camera.transform;
            buildOnAwake=false;
        }
    }
}
