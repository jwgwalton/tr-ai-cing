# tr-ai-cing
A monitoring and observability platform for use in LLM applications

This project will be made of 2 parts

A logging tool that logs to a structured log file. This will allow for arbitrary logging but is focussed on logging the inputs & outputs of calls to LLMs within an application so that we can trace how data is transformed & identify errors.

There will also be a visualisation component which will take these structured logs & visualise them in a HTML file so we can see the DAG of the calls to LLMs and what the inputs & outputs look like of each stage.
