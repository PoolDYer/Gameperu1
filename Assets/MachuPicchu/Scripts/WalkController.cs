using UnityEngine;

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
            if (Input.GetKeyDown(KeyCode.Escape))
            { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
            if (Input.GetMouseButtonDown(0))
            { Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false; }
            if (Cursor.lockState != CursorLockMode.Locked) return;
            transform.Rotate(0, Input.GetAxis("Mouse X") * sensitivity, 0);
            pitch = Mathf.Clamp(pitch - Input.GetAxis("Mouse Y") * sensitivity, -85, 85);
            if (view != null) view.localRotation = Quaternion.Euler(pitch, 0, 0);
            Vector3 input = Vector3.ClampMagnitude(new Vector3(Input.GetAxisRaw("Horizontal"), 0, Input.GetAxisRaw("Vertical")), 1);
            if (controller.isGrounded && verticalSpeed < 0) verticalSpeed = -2;
            verticalSpeed += Physics.gravity.y * Time.deltaTime;
            Vector3 motion = transform.TransformDirection(input) * speed;
            motion.y = verticalSpeed;
            controller.Move(motion * Time.deltaTime);
        }
    }
}
