using UnityEngine;
using UnityEngine.InputSystem;

namespace MachuPicchu
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class WalkController : MonoBehaviour
    {
        public Transform view;
        public float speed = 2.2f;
        public float sensitivity = 1.5f;
        private CharacterController controller;
        private float verticalSpeed;
        private float pitch;

        public void ResetFallSpeed() { verticalSpeed = 0; }

        void Awake() { controller = GetComponent<CharacterController>(); }
        void OnDisable() { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
        void Update()
        {
            var keyboard = Keyboard.current;
            var mouse = Mouse.current;
            if (keyboard != null && keyboard.escapeKey.wasPressedThisFrame)
            {
                Cursor.lockState = CursorLockMode.None; Cursor.visible = true;
                return;
            }
            bool capturedThisFrame = false;
            if (mouse != null && mouse.leftButton.wasPressedThisFrame && Cursor.lockState != CursorLockMode.Locked)
            {
                Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false;
                capturedThisFrame = true;
            }
            if (Cursor.lockState != CursorLockMode.Locked) return;
            Vector2 look = mouse != null && !capturedThisFrame ? mouse.delta.ReadValue() * (sensitivity * .1f) : Vector2.zero;
            transform.Rotate(0, look.x, 0);
            pitch = Mathf.Clamp(pitch - look.y, -85, 85);
            if (view != null) view.localRotation = Quaternion.Euler(pitch, 0, 0);
            Vector3 input = Vector3.zero;
            if (keyboard != null)
            {
                input.x = ((keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) ? 1 : 0)
                    - ((keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) ? 1 : 0);
                input.z = ((keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) ? 1 : 0)
                    - ((keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) ? 1 : 0);
                input = Vector3.ClampMagnitude(input, 1);
            }
            if (controller.isGrounded && verticalSpeed < 0) verticalSpeed = -2;
            verticalSpeed += Physics.gravity.y * Time.deltaTime;
            Vector3 motion = transform.TransformDirection(input) * speed;
            motion.y = verticalSpeed;
            controller.Move(motion * Time.deltaTime);
        }
    }
}
