import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)

from common.models import ReviewStatus

# Готовые русскоязычные модели:
# - токсичность: s-nlp/russian_toxicity_classifier
# - спам: RUSpam/spam_deberta_v4
_toxic_pipe = pipeline(
    "text-classification",
    model="s-nlp/russian_toxicity_classifier",
    tokenizer="s-nlp/russian_toxicity_classifier",
    top_k=None,
)

_spam_tokenizer = AutoTokenizer.from_pretrained("RUSpam/spam_deberta_v4")
_spam_model = AutoModelForSequenceClassification.from_pretrained("RUSpam/spam_deberta_v4")


def _is_spam(text: str) -> bool:
    inputs = _spam_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = _spam_model(**inputs)
        logits = outputs.logits
        label_id = int(torch.argmax(logits, dim=1))
    return label_id == 1  # label 1 = spam


def _is_toxic(text: str) -> bool:
    result = _toxic_pipe(text, truncation=True)
    if isinstance(result, list):
        first = result[0]
        if isinstance(first, list):
            first = first[0]
    else:
        first = result
    label = first["label"] if isinstance(first, dict) else ""
    return label.lower() == "toxic"


def moderate_text(text: str) -> tuple[ReviewStatus, str | None]:
    """Используем готовые модели для токсичности и спама на русском."""
    toxic = _is_toxic(text)
    spam = _is_spam(text)
    if toxic:
        return ReviewStatus.rejected, "Отклонено: токсичный текст (toxic model)"
    if spam:
        return ReviewStatus.rejected, "Отклонено: спам (spam model)"
    return ReviewStatus.published, None
