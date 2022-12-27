# What are Model Cards?

First introduced in the paper "[Model Cards for Model Reporting (Mitchell, M. et al., 2019)](https://arxiv.org/abs/1810.03993)", model cards are described as a way to provide transparent and comprehensive information about a machine learning model. They are designed to be a standalone document that provides information about the model's performance, limitations, and ethical considerations.

Model cards typically include information such as:

- Model name and description
- Tasks the model is designed to perform
- Data used to train the model
- Evaluation metrics and performance on those metrics
- Limitations of the model
- Ethical considerations related to the model's use

Model cards are intended to help users understand the capabilities and limitations of a model, as well as the ethical considerations related to its use. By providing this information in a clear and concise way, model cards can help users make informed decisions about which models to use in their projects.

## Model Cards in the AI App Store

In the AI App Store, model cards provide similar information about each model, which are stored in the following attributes.

### What & Why: model description, its usage and purpose

| Attribute                 | Description                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model Title               | A name given to the model                                                                                                                                                                                                                                                                                                                                                           |
| Model Description and Use | A summary account of the model and its intended uses. Description may include: (a) intended uses; (b) intended users; (c) model architecture – what general architecture is used?; (d) training algorithms, parameters, learning constraints – how did the model learn?; (e) input variables; (f) output variables; and (g) optimization target – what defines the learning signal? |
| Published Date            | Calendar dates associated with the publication of the model.                                                                                                                                                                                                                                                                                                                        |
| Subject Tags              | Categories, keyword(s), label(s) or tag(s) that characterize the subject matter of the model resource.                                                                                                                                                                                                                                                                              |

### Who: contact for the model

| Attribute        | Description                                                                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model Creator    | The user account that submitted the model to the App Store. This is supposed to be the person or entity responsible for generating or developing the model                                                      |
| Model Owner      | The name of person or entity primarily responsible for the intellectual content and the endorsement for sharing of model resource. Note that this does not need to reference a user registered on the App Store |
| Point of Contact | The name of person to consult about this model.                                                                                                                                                                 |

### Where: source of original and related model components

| Attribute          | Description                                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model Source/Path  | A reference to entities, systems, assets or resources from which the model is derived (e.g a Git Repository). Please state if it is authoritative source. |
| Related Experiment | A reference to a related experiment (e.g ClearML experiment) that the model was derived from                                                              |
| Related Datasets   | A reference to a related dataset (e.g ClearML dataset) that was used to train the model                                                                   |

### How: composition and construction of model

| Attribute                        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Task                             | The nature, genre, or discipline of the content of the model (e.g. Reinforcement Learning, Computer Vision, etc).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Model Framework                  | The model framework used (e.g PyTorch, Keras, Scikit-Learn)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Model Limitations and Trade-Offs | A summary account of the model performance across a variety of relevant factors. Description may include: (a) groups – what divisions (e.g. demographics) matter?; (b) instrumentation – what input context (e.g. camera type) matters?; (c) environmental – what operating context (e.g. ambient lighting or humidity) matters?; and (d) model limitations and trade-offs.                                                                                                                                                                                                                      |
| Model Metrics                    | An account of appropriate metrics selected to feature in the model. Description may include: (a) model performance measures – what metrics were chosen; (b) decision thresholds – what thresholds were chosen and why?; (d) approaches to uncertainty and variability – how is it measured, calculated (e.g., resampling) and used?; and (e) privacy-preserving protections relevant to model’s design.                                                                                                                                                                                          |
| Model Performance                | An account of model performance. Description may include: (a) overall – rates of correct predictions and errors, derived metrics (e.g. precision, recall, FI, ROC, etc.); (b) by factor – how does performance vary by group, instrumentation and environment?; and (c) by factor intersection – how does performance vary at intersections (e.g., a demographic group under certain lighting conditions)?                                                                                                                                                                                       |
| Model Explanation                | An account of explanations of model or model explainability. Description may include: (a) general logic – what are the key features that matter and how are they related?; (b) particular inferences – are specific predictions explained?; (c) nature – are explanations in the form of associations (e.g., feature importance), contrasts (e.g., counterfactuals), or causal models?; (d) medium –are they provided as text, visuals or some other format?; (e) audience – which user personas are they meant for?; (f) motivation – why were this nature and medium chosen for this audience? |
