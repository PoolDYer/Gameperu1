using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

namespace MachuPicchu
{
    public sealed class LoadTerrainScene : MonoBehaviour
    {
        public string terrainScenePath;
        public string architectureScenePath;
        public GameObject player;
        IEnumerator Start()
        {
            // Disable gravity until the terrain collider is loaded.
            if (player != null) player.SetActive(false);
            if (!SceneManager.GetSceneByPath(terrainScenePath).isLoaded)
                yield return SceneManager.LoadSceneAsync(terrainScenePath, LoadSceneMode.Additive);
            if (!SceneManager.GetSceneByPath(architectureScenePath).isLoaded)
                yield return SceneManager.LoadSceneAsync(architectureScenePath, LoadSceneMode.Additive);
            if (player != null) player.SetActive(true);
        }
    }
}
