using UnityEngine;

namespace MachuPicchu
{
    // Attach source provenance to the editable terrain; never bake large UTM values into transforms.
    public sealed class SurveyMetadata : MonoBehaviour
    {
        [TextArea(4, 20)] public string sourceJson;
        public double eastingMeters;
        public double northingMeters;
        public double elevationMeters;
    }
}
