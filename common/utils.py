from django.forms import model_to_dict


def component_group_order(query):
    local_final_dict = dict()
    local_final_dict['component_id'] = query.component_id
    local_final_dict['component_name'] = query.component_name
    local_final_dict['group_no'] = query.group_no
    local_final_dict['has_subgroup'] = query.has_subgroup
    local_final_dict['businessunit'] = model_to_dict(query.businessunit)
    local_final_dict['component_status'] = model_to_dict(
        query.component_status)
    return local_final_dict
