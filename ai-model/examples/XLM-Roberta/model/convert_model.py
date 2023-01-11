import torch
from transformers import (
    XLMRobertaForSequenceClassification,
    XLMRobertaTokenizer,
)

nli_model = XLMRobertaForSequenceClassification.from_pretrained(
    "joeddav/xlm-roberta-large-xnli", return_dict=False
)
tokenizer = XLMRobertaTokenizer.from_pretrained(
    "joeddav/xlm-roberta-large-xnli"
)

premise = "Earth is warming up"
hypothesis = "This text is about climate change"

# run through model pre-trained on MNLI
x = tokenizer.encode(
    premise,
    hypothesis,
    return_tensors="pt",
    truncation=True,
    max_length=256,
    padding="max_length",
)

mask = x != 1
mask = mask.long()
print(mask)
print(x)


class PyTorch_to_TorchScript(torch.nn.Module):
    def __init__(self):
        super(PyTorch_to_TorchScript, self).__init__()
        self.model = XLMRobertaForSequenceClassification.from_pretrained(
            "joeddav/xlm-roberta-large-xnli", return_dict=False
        ).cuda()

    def forward(self, data, attention_mask=None):
        return self.model(data.cuda(), attention_mask.cuda())


model = PyTorch_to_TorchScript().eval()
tracer = torch.jit.trace(model, (x, mask))
tracer.save("xlm_roberta_zsl/1/model.pt")
