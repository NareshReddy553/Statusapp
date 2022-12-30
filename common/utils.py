from django.forms import model_to_dict

from common.models import ComponentsStatus


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


def get_component_status():
    comp_status_obj = ComponentsStatus.objects.values(
        'component_status_id', 'component_status_name')
    status_list = []
    if comp_status_obj:
        for data in comp_status_obj:
            status_dict = {}
            status_dict[data['component_status_name']
                        ] = data['component_status_id']
            status_list.append(status_dict)
    return status_list
