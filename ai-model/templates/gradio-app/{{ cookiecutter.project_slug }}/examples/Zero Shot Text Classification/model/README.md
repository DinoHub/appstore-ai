# Triton Deployment

To deploy the model onto Triton, do the following

1. Run `build-model.sh` which will run a build container that will output a `model.pt` inside the `xlm_roberta_zsl` folder. Note this build process requires access to a GPU. So your machine must be configured with the Nvidia Container Runtime to allow for GPU to be used. Otherwise, you can attempt to directly run the `convert_model.py` script (assuming you have dependencies installed)
2. Move the `xlm_roberta_zsl` folder to your model repository so that Triton can access it

Note that sometimes Triton may not be able to run your model if the pytorch version used to compile the model is different from that supported by Triton. So in such cases, you may need to update the `Dockerfile.build` to use a different PyTorch version.
