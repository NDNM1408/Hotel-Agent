import typing as t
from pydantic import BaseModel
import json
from constant import JSON_FORMAT_INSTRUCTIONS
import json


Example = t.Dict[str, t.Any]
TBaseModel = t.TypeVar("TBaseModel", bound=BaseModel)

def get_json_format_instructions(pydantic_object: t.Type[TBaseModel]) -> str:
    schema = {k: v for k, v in pydantic_object.schema().items()}
    reduced_schema = schema
    if "title" in reduced_schema:
        del reduced_schema["title"]
    # Ensure json in context is well-formed with double quotes.
    schema_str = json.dumps(reduced_schema)
    return JSON_FORMAT_INSTRUCTIONS.format(schema=schema_str)

class Prompt(BaseModel):
    name: str = ""
    instruction: str
    output_format_instruction: str = ""
    examples: t.List[Example] = []
    input_keys: t.List[str] = [""]
    output_key: str = ""
    output_type: t.Literal["json", "str"] = "json"

    def validate_prompt(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """
        Validate the template string to ensure that it is in desired format.
        """
        if values.get("instruction") is None or values.get("instruction") == "":
            raise ValueError("instruction cannot be empty")
        if values.get("input_keys") is None or values.get("instruction") == []:
            raise ValueError("input_keys cannot be empty")
        if values.get("output_key") is None or values.get("output_key") == "":
            raise ValueError("output_key cannot be empty")

        if values.get("examples"):
            output_key = values["output_key"]
            for no, example in enumerate(values["examples"]):
                for inp_key in values["input_keys"]:
                    if inp_key not in example:
                        raise ValueError(
                            f"example {no+1} does not have the variable {inp_key} in the definition"
                        )
                if output_key not in example:
                    raise ValueError(
                        f"example {no+1} does not have the variable {output_key} in the definition"
                    )
                if values["output_type"].lower() == "json":
                    try:
                        if output_key in example:
                            if isinstance(example[output_key], str):
                                json.loads(example[output_key])
                    except ValueError as e:
                        raise ValueError(
                            f"{output_key} in example {no+1} is not in valid json format: {e}"
                        )

        return values

    def to_string(self) -> str:
        """
        Generate the prompt string from the variables.
        """
        prompt_elements = [self.instruction]
        if self.output_format_instruction:
            prompt_elements.append(
                "\n"
                + self.output_format_instruction.replace("{", "{{").replace("}", "}}")
            )
        prompt_str = "\n".join(prompt_elements) + "\n"

        if self.examples:
            prompt_str += "\nExamples:\n"
            # Format the examples to match the Langchain prompt template
            for example in self.examples:
                for key, value in example.items():
                    is_json = isinstance(value, (dict, list))
                    value = (
                        json.dumps(value, ensure_ascii=False).encode("utf8").decode()
                    )
                    value = (
                        value.replace("{", "{{").replace("}", "}}")
                        if self.output_type.lower() == "json"
                        else value
                    )
                    prompt_str += (
                        f"\n{key}: {value}"
                        if not is_json
                        else f"\n{key}: ```{value}```"
                    )
                prompt_str += "\n"

        prompt_str += "\nYour actual task:\n"

        if self.input_keys:
            prompt_str += "".join(f"\n{key}: {{{key}}}" for key in self.input_keys)
        if self.output_key:
            prompt_str += f"\n{self.output_key}: \n"

        return prompt_str

    def get_example_str(self, example_no: int) -> str:
        """
        Get the example string from the example number.
        """
        if example_no >= len(self.examples):
            raise ValueError(f"example number {example_no} is out of range")
        example = self.examples[example_no]
        example_str = ""
        for key, value in example.items():
            value = json.dumps(value, ensure_ascii=False).encode("utf8").decode()
            value = (
                value.replace("{", "{{").replace("}", "}}")
                if self.output_type.lower() == "json"
                else value
            )
            example_str += f"\n{key}: {value}"
        return "```" + example_str + "```"

    def format(self, **kwargs: t.Any):
        """
        Format the Prompt object into a ChatPromptTemplate object to be used in metrics.
        """
        if set(self.input_keys) != set(kwargs.keys()):
            raise ValueError(
                f"Input variables {self.input_keys} do not match with the given parameters {list(kwargs.keys())}"
            )
        for key, value in kwargs.items():
            if isinstance(value, str):
                kwargs[key] = json.dumps(value)

        prompt = self.to_string()
        return prompt.format(**kwargs)