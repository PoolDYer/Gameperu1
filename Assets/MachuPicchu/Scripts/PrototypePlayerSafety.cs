using UnityEngine;
using UnityEngine.InputSystem;
namespace MachuPicchu
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class PrototypePlayerSafety : MonoBehaviour
    {
        public Vector3 spawn;
        public float width=200, length=530;
        void Update()
        {
            Vector3 p=transform.position;
            if ((Keyboard.current != null && Keyboard.current.rKey.wasPressedThisFrame) || p.y < -10 || p.x < -2 || p.z < -2 || p.x > width+2 || p.z > length+2)
            {
                var controller=GetComponent<CharacterController>(); controller.enabled=false;
                transform.position=spawn; controller.enabled=true;
                GetComponent<WalkController>()?.ResetFallSpeed();
            }
        }
    }
}
