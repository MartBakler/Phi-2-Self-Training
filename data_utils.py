import os
import json
import random

def load_gsm8k_data(data_path):
    data = {"question":[], "answer":[]}
    with open(data_path, "r", encoding = "utf-8") as f:
        for line in f:
            line = json.loads(line)
            data["question"].append(line["question"])
            data["answer"].append(line["answer"].replace("####", "FINAL ANSWER:"))
    return data


def load_synthetic_data(dataset_file):
    data = {"question":[], "correct_predictions":[], "original_answer": [], "incorrect_predictions":[]}
    with open(dataset_file, "r", encoding = "utf-8") as f:
        for line in f:
            line = json.loads(line)
            data["question"].append(line["question"])
            data["correct_predictions"].append(line["correct_predictions"])
            data["incorrect_predictions"].append(line["incorrect_predictions"])
            data["original_answer"].append(line["original_answer"])
    return data

def load_prompt(prompt_path):
      with open(prompt_path, "r", encoding = "utf-8") as f:
          prompt = f.read()
      return prompt

class DatasetProcessor:
    def __init__(self,
                 tokenizer,
                 sft_generation_prompt_path,
                 eval_prompt_path,
                 training_mode):
        self.tokenizer = tokenizer
        self.sft_generation_prompt = load_prompt(sft_generation_prompt_path)
        self.eval_prompt = load_prompt(eval_prompt_path)
        self.training_mode = training_mode

    
    def training_preprocessor_function(self, examples):
            inputs = [(self.sft_generation_prompt.format(question = examples["question"][idx]), examples["correct_predictions"][idx][0] + self.tokenizer.eos_token) for idx in range(len(examples["question"]))]
            if self.training_mode == "sft_generation+eval":
                correct_eval_inputs = [(self.eval_prompt.format(question = examples["question"][idx],
                                                                solution = examples["correct_predictions"][idx][-1]), "Correct") for idx in range(len(examples["question"]))
                                                                if len(examples["correct_predictions"][idx]) > 1]
                incorrect_eval_inputs = [(self.eval_prompt.format(question = examples["question"][idx],
                                                                solution = examples["incorrect_predictions"][idx][-1]), "Incorrect") for idx in range(len(examples["question"]))
                                                                if len(examples["incorrect_predictions"][idx]) > 1]
                inputs.extend(correct_eval_inputs)
                inputs.extend(incorrect_eval_inputs)
            model_inputs = self.tokenizer(inputs, padding="max_length",
                                           max_length=384, truncation=True,
                                           return_token_type_ids=True)
            #model_inputs["original_queston"] = [self.sft_generation_prompt.format(question = examples["question"][idx]) for idx in range(len(examples["question"]))]
            #model_inputs["original_answer"] = examples["original_answer"]
            #tokenized_questions = self.tokenizer(model_inputs["original_queston"], padding="max_length", max_length=384)
            #model_inputs["tokenized_question_ids"] = tokenized_questions["input_ids"]
            #model_inputs["tokenized_question_attentions"] = tokenized_questions["attention_mask"]



            #labels = model.tokenizer(text_target=examples["answer"], max_length=512, truncation=True)

            #model_inputs["labels"] = model_inputs["input_ids"]
            return model_inputs
