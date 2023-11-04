import onnxruntime as ort

# Load the ONNX model using onnxruntime
model_path = './arcfaceresnet100-11-int8.onnx'
session = ort.InferenceSession(model_path)

# Get the model's input and output details
input_details = session.get_inputs()[0]
output_details = session.get_outputs()[0]

# Print the input and output details
print("Input Details:")
print("Name:", input_details.name)
print("Shape:", input_details.shape)
print("Type:", input_details.type)

print("\nOutput Details:")
print("Name:", output_details.name)
print("Shape:", output_details.shape)
print("Type:", output_details.type)
