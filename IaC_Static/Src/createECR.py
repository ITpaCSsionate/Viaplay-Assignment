from troposphere import Template, Tags
from troposphere.ecr import Repository

import json 

configuration = json.load(open("../Configuration/Configuration.json", 'r'))
repositoryName = configuration["repositoryName"]
tagsC = configuration["tags"]
tags = Tags(tagsC)
t = Template()

t.add_resource(
    Repository(
        "MyRepository",
        RepositoryName=repositoryName,
        Tags=tags
    )
)

print(t.to_yaml())