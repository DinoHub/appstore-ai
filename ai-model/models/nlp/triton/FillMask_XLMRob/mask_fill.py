from doctest import OutputChecker
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch
import numpy as np

tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
model = AutoModelForMaskedLM.from_pretrained("xlm-roberta-base", return_dict=False)

# prepare input
text = "Hello I'm a new <mask> model."
encoded_input = tokenizer(
    text, return_tensors="pt", truncation=True, padding="max_length"
)
model.eval()
print(model(encoded_input.input_ids, encoded_input.attention_mask))
traced_model = torch.jit.trace(
    model, [encoded_input.input_ids, encoded_input.attention_mask]
)
torch.jit.save(traced_model, "model.pt")
# loaded_model = torch.jit.load("model.pt")
# print(encoded_input['input_ids'].size(),encoded_input['attention_mask'].size())
# output = loaded_model(encoded_input['input_ids'],encoded_input['attention_mask'])
# print(output[0].size())
# mask_token_index = torch.where(encoded_input["input_ids"] == tokenizer.mask_token_id)[1]
# mask_token_logits = output[0][0, mask_token_index, :]
# print(mask_token_index)
# print(mask_token_logits)
# # Pick the [MASK] candidates with the highest logits
# top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()

# for token in top_5_tokens:
#     print(f"'>>> {text.replace(tokenizer.mask_token, tokenizer.decode([token]))}'")
# loaded_model = torch.jit.load("model.pt")
# loaded_model.eval()
# text = "Hello I'm a <mask> model."
# encoded_input = tokenizer(text, return_tensors="pt",truncation=True,padding = 'max_length' )
# dummy_input = [encoded_input.input_ids,encoded_input.attention_mask]
# all_encoder_layers, pooled_output = loaded_model(*dummy_input)

# print(pooled_output)
