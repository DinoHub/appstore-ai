# AAS Inference Engine

[Documentation](https://ai-app-store.readthedocs.io/projects/inference-engine/en/latest/)

The AAS Inference Engine provides a way for a model creator to provide the AI App Store with an interface for sending inferences. 

## Roadmap

### v0.5
- [x] Text, JSON, Media File IO Interface
- [x] Interactive setup script

### v1.0
- [ ] Simplify creation of inference engine, see if it is possible to decouple it completely (in terms of defining the exact input and output fields) from the AAS (i.e standalone ala Gradio)
    - [ ] Extend IOSchema to allow specifying input name, description etc
    - [ ] Adjust inference engine code to read from multiple IOSchemas, and map request inputs to corresponding components
    - [ ] Somehow combine the outputs of multiple IOSchemas into an API response?
- [ ] Ability to set example inputs and outputs
- [ ] Use of websockets 
- [ ] More IO Types (e.g Tabular data, etc)

### v2.0
- [ ] Front-end interface separated from the AI App Store?
- [ ] Figure out how to support streamed webcam footage
## Licence

This project is under the [GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).

### TL;DR

You may copy, distribute and modify the software as long as you track changes/dates in source files. Any modifications to or software including (via compiler) GPL-licensed code must also be made available under the GPL along with build & install instructions.

## Contributors

### Core Contributors

- [Mathias Ho](https://github.com/OrionSolaris)
- [Tien Cheng](https://github.com/Tien-Cheng)

### Special Thanks

- Our project supervisor and mentor in DSTA Digital Hub, [Kah Siong](https://github.com/jax79sg)
