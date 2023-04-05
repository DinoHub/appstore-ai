# Use Case Diagram

```{mermaid}
%%{init: {'theme':'dark'}}%%
flowchart TD
    subgraph End User
    direction LR
    user[/End User\]
    user -->aas-4(List Models)
    user -->aas-22(Search Models)-->aas-7(Filter Models)
    user-->aas-8(Open Model)-->|includes|aas-9(View Model Page)
    user-->aas-5(Test Sample)-->|includes|aas-12(Upload Sample Batch)-->|includes|aas-13(View Sampled Inference)
    user-->aas-6(Transfer Learn Datasets)-->aas-14(Upload Datasets)
    aas-6-->aas-15(Monitor Progress)
    end
```

```{mermaid}
%%{init: {'theme':'dark'}}%%
flowchart TD
    subgraph Model Owner
    owner[/Model Owner\]
    owner-->aas-3(Create Model)
    aas-3-->|includes|aas-26(Select ClearML Pipeline ID)
    aas-3-->|includes|aas-10(Enter Model Card Attributes)
    aas-3-->aas-27(Upload Inference Application)
    aas-26-->|includes|aas-11(Pick Available Metrics as Model Card Attributes)
    aas-10-->|includes|aas-25(Upload images for Model Card)
    owner-->aas-19(Update Model)
    aas-19-->|includes|aas-29(Update Model Card Attributes)
    aas-19-->|includes|aas-28(Update Inference Application)
    owner-->aas-18(Delete Model)
    end
```

```{mermaid}
%%{init: {'theme':'dark'}}%%
flowchart TD
    subgraph System Administrator
    direction LR
    sa[/System Administrator\]
    sa-->aas-21(Create User)
    sa-->aas-20(Set Permissions)
    end
```
