from inference_sdk import InferenceHTTPClient
import cv2
client = InferenceHTTPClient(
    api_url="http://localhost:9001", # use local inference server
    api_key="Qnrt6xKZYqRPVyNIRL5n"
)

result = client.run_workflow(
    workspace_name="project-vrpiq",
    workflow_id="custom-workflow",
    images={
        "image": "mysor1.jpg"
    }
)
