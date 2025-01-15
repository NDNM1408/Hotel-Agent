TRIP_DETAIL_EXTRACTION_PROMPT = """You are a hotel employee, your daily task is to handle booking requests from customers, analyze the services they use, the accompanying promotions they are entitled to, and then write carefully again the service each day they use and hire. For each request from customers, your responsibility is to extract information such as the time period the customer group books the room and the number of people in the group. Then, describe in detail, day by day, what services the group of tourists uses, what types of buffets they eat, or beverages they consume, and what rooms they rent for events. During the evening in each day, specify how many rooms the group rents, whether there are children, and how many people stay overnight. Note: ensure that the description follows a chronological order"""
JSON_FORMAT_INSTRUCTIONS = """The output should be a well-formatted JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output JSON schema:
```
{schema}
```

Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```)."""
