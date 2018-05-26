def resource_name(resource_dict):
    if 'Tags' in resource_dict:
        for tag in resource_dict['Tags']:
            if tag['Key'] == 'Name':
                return tag['Value']


def tag(resource, *tags):
    resource.create_tags(Tags=[{'Key': k, 'Value': v} for k, v in tags])


def taglist_keys(taglist):
    return [tag['Key'] for tag in taglist]


def tagged_resource(resources, target_tag):
    target_key = target_tag[0]
    target_val = target_tag[1]

    def has_matching_tag(resource):
        if not resource.tags:
            return

        for resource_tag in resource.tags:
            if target_key == resource_tag['Key'] and \
               target_val == resource_tag['Value']:
                return resource

    for resource in resources:
        if has_matching_tag(resource):
            return resource

