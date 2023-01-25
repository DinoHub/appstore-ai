# ClearML Integration
ClearML Integration within the AI App Store currently works as follows:
- When creating/editing a model card, you can select ClearML as an experiment provider. After passing a ClearML experiment ID, we will pull in available metadata about the experiment and integrate it to your model card. This includes:
   - Tags, Frameworks
   - Related artifacts (e.g Model weights)
   - Scalars and plots

## Limitations
- At the moment, only 1 ClearML account can be linked to a deployment of the application at a time. This means that all ClearML operations will be done with a single service account that needs access to your projects. 
  - This is intended to be fixed in the future, to allow each user to sign in with their own accounts, but the ClearML API's don't currently allow for a good way to do this at the moment.